import os
import time
import subprocess
import redis

VAULT_DIR = "strategies"
running_processes = {}
log_files = {}

print("🧠 Unicorn Orchestrator Online. Monitoring Vault & Kill Switches...")
os.makedirs(VAULT_DIR, exist_ok=True)

# Connect to Redis to listen for the Emergency Stop signals
redis_host = os.environ.get('REDIS_HOST', 'localhost')
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)

while True:
    try:
        # 1. Scan for new files
        for filename in os.listdir(VAULT_DIR):
            if filename.endswith(".py") and filename not in running_processes:
                filepath = os.path.join(VAULT_DIR, filename)
                logpath = os.path.join(VAULT_DIR, f"{filename}.log")
                
                log_handle = open(logpath, "w")
                process = subprocess.Popen(["python", "-u", filepath], stdout=log_handle, stderr=subprocess.STDOUT)
                
                running_processes[filename] = process
                log_files[filename] = log_handle
        
        # 2. Monitor for Crashes OR Kill Commands
        for filename, process in list(running_processes.items()):
            
            # THE ASSASSIN: Check if the web UI triggered the Kill Switch for this specific file
            if cache.get(f"KILL_FILE_{filename}"):
                print(f"🛑 [KILL SWITCH] Assassinating strategy: {filename}")
                log_files[filename].write("\n🛑 [SYSTEM] MASTER KILL SWITCH ACTIVATED BY USER. FORCE STOPPING.\n")
                
                process.kill() # Terminate the process instantly at the OS level
                cache.delete(f"KILL_FILE_{filename}") # Clear the signal
            
            # Clean up if process naturally finished or was just killed
            if process.poll() is not None:
                log_files[filename].close()
                del running_processes[filename]
                del log_files[filename]

        time.sleep(2)
        
    except Exception as e:
        print(f"🔴 Orchestrator Error: {e}")
        time.sleep(5)
