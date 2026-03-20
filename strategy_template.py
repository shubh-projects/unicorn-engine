"""
🦄 UNICORN ENGINE: BLANK CANVAS SDK
Welcome, Quant. 
Your strategy runs in a strictly isolated, secure cloud container.
We handle the high-speed data feeds, Redis caching, and UI rendering.
You only need to write your logic inside the 'on_tick' function.
"""
import redis
import os
import json
import time

class CustomQuantStrategy:
    def __init__(self):
        # Define your custom variables, indicators, and memory here
        self.position = None
        print("🟢 Custom Strategy Initialized. Waiting for data...")

    def on_tick(self, symbol, price, timestamp):
        """
        THE BLANK CANVAS:
        This function is automatically triggered every millisecond the market moves.
        Write your proprietary logic here.
        """
        
        # --- YOUR SECRET SAUCE GOES HERE ---
        # Example: 
        # if price > my_secret_indicator:
        #     self.execute_trade("BUY", quantity=50)

        pass

    def execute_trade(self, action, quantity):
        # This securely routes the order using YOUR encrypted broker keys
        print(f"⚡ [EXECUTION SIGNAL] {action} {quantity} shares. Routing to broker...")

# ---------------------------------------------------------
# UNICORN ENGINE INFRASTRUCTURE (DO NOT MODIFY)
# ---------------------------------------------------------
redis_host = os.environ.get('REDIS_HOST', 'localhost')
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)

strategy = CustomQuantStrategy()
last_timestamp = None

while True:
    try:
        data = cache.get("LATEST_NIFTY")
        if data:
            tick = json.loads(data)
            # Only trigger strategy logic on a brand new tick
            if tick['timestamp'] != last_timestamp:
                strategy.on_tick(tick['symbol'], tick['price'], tick['timestamp'])
                last_timestamp = tick['timestamp']
        
        # High-frequency polling
        time.sleep(0.01)
    except Exception as e:
        pass
