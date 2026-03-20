import redis
import time
import json
import random

# Connect directly to our local Redis container
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

price = 46000.0
print("💉 Injecting 30 seconds of simulated Bank Nifty volatility...")

for _ in range(60):
    # Create realistic-looking random price jumps
    price += random.uniform(-15, 15)
    
    tick_data = {
        "symbol": "BANKNIFTY",
        "price": price,
        "timestamp": time.time()
    }
    
    # Slam it into the exact key the UI is watching
    cache.set("LATEST_BANKNIFTY", json.dumps(tick_data))
    time.sleep(0.5) # Pump twice a second

print("🏁 Test complete.")
