from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import json, os, subprocess

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    with open("/app/index.html", "r") as f:
        return f.read()

# NEW: API now accepts fast_ma and slow_ma
@app.get("/run-backtest")
def run_logic(capital: float = 100000.0, fast_ma: int = 50, slow_ma: int = 200):
    try:
        # Pass the variables directly into the Python terminal command
        subprocess.run(["python", "/app/engine.py", str(fast_ma), str(slow_ma)], check=True)
        
        with open("backtest_results.json", "r") as f:
            data = json.load(f)
            
        original_initial = data["summary"]["initial"]
        multiplier = capital / original_initial
        
        data["summary"]["initial"] = capital
        data["summary"]["final"] = data["summary"]["final"] * multiplier
        
        peak = 0.0; max_dd = 0.0; winning_days = 0; total_days = 0; last_v = None

        for point in data["chart"]:
            v = point["portfolio"] * multiplier
            point["portfolio"] = v  
            
            if v > peak: peak = v
            dd = (v - peak) / peak if peak > 0 else 0
            if dd < max_dd: max_dd = dd
                
            if last_v is not None:
                total_days += 1
                if v > last_v: winning_days += 1
            last_v = v
            
        data["summary"]["max_drawdown"] = f"{max_dd * 100:.2f}%"
        win_rate_calc = (winning_days / total_days * 100) if total_days > 0 else 0
        data["summary"]["win_rate"] = f"{win_rate_calc:.1f}%"
        
        return JSONResponse(content=data)
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
