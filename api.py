from fastapi import FastAPI, WebSocket, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import redis
import os
import asyncio
import shutil
import psycopg2
import hashlib

app = FastAPI()

redis_host = os.environ.get('REDIS_HOST', 'localhost')
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)
os.makedirs("strategies", exist_ok=True)

def get_db():
    return psycopg2.connect(
        dbname="unicorn_engine", user="unicorn_admin", password="unicorn_secret",
        host=os.environ.get("DB_HOST", "postgres-db"), port="5432"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/")
async def get():
    with open("index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

@app.post("/auth/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING user_id", (email, hash_password(password)))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Account created! You can now log in.", "user_id": user_id}
    except psycopg2.IntegrityError:
        return JSONResponse(status_code=400, content={"message": "Email already exists."})
    finally:
        cursor.close()
        conn.close()

@app.post("/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and user[1] == hash_password(password):
        return {"message": "Login successful", "user_id": user[0]}
    return JSONResponse(status_code=401, content={"message": "Invalid email or password"})

@app.post("/upload-strategy/")
async def upload_strategy(user_id: int = Form(...), client_id: str = Form(...), access_token: str = Form(...), strategy_file: UploadFile = File(...)):
    try:
        if not strategy_file.filename.endswith('.py'):
            return JSONResponse(status_code=400, content={"message": "Only .py files are allowed."})
            
        safe_filename = f"user_{user_id}_{strategy_file.filename}"
        with open(f"strategies/{safe_filename}", "wb+") as f:
            shutil.copyfileobj(strategy_file.file, f)
            
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO broker_keys (user_id, broker_name, client_id, encrypted_token) VALUES (%s, 'Dhan', %s, %s)", (user_id, client_id, hash_password(access_token)))
        cursor.execute("INSERT INTO deployments (user_id, strategy_name, status) VALUES (%s, %s, 'DEPLOYED')", (user_id, safe_filename))
        conn.commit()
        cursor.close()
        conn.close()

        cache.hset(f"KEYS_{client_id}", mapping={"client_id": client_id, "token": access_token, "strategy": safe_filename})
        return {"message": "Strategy deployed.", "status": "Ready"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Upload failed: {str(e)}"})

# ---------------------------------------------------------
# NEW: THE KILL SWITCH ENDPOINT
# ---------------------------------------------------------
@app.post("/api/stop/{user_id}")
async def stop_strategy(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Find the exact strategy this user currently has running
        cursor.execute("SELECT strategy_name FROM deployments WHERE user_id = %s AND status = 'DEPLOYED' ORDER BY deployed_at DESC LIMIT 1", (user_id,))
        deployment = cursor.fetchone()
        
        if deployment:
            strategy_name = deployment[0]
            
            # 1. Fire the Kill Signal into Redis for the Orchestrator to catch
            cache.set(f"KILL_FILE_{strategy_name}", "1")
            
            # 2. Update the database to show it was stopped
            cursor.execute("UPDATE deployments SET status = 'STOPPED' WHERE strategy_name = %s", (strategy_name,))
            conn.commit()
            
            return {"message": "Kill signal transmitted.", "status": "Stopped"}
            
        return JSONResponse(status_code=404, content={"message": "No active strategy found to stop."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"System Error: {str(e)}"})
    finally:
        cursor.close()
        conn.close()

@app.get("/api/logs/{user_id}")
async def get_logs(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT strategy_name FROM deployments WHERE user_id = %s ORDER BY deployed_at DESC LIMIT 1", (user_id,))
        deployment = cursor.fetchone()
        if not deployment:
            return {"logs": "> System Idle. Awaiting strategy deployment...\n"}
        strategy_name = deployment[0]
        log_file_path = f"strategies/{strategy_name}.log"
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as f:
                logs = "".join(f.readlines()[-50:])
            return {"logs": logs}
        else:
            return {"logs": f"> Booting sandbox container for {strategy_name}...\n"}
    except Exception as e:
        return {"logs": f"Error fetching logs: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    redis_key = f"LATEST_{symbol.upper()}"
    last_data = None
    try:
        while True:
            data = cache.get(redis_key)
            if data and data != last_data:
                await websocket.send_text(data)
                last_data = data
            await asyncio.sleep(0.05)
    except Exception:
        pass
