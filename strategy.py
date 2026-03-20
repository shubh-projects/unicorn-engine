import redis
import os
import time
import json
from collections import deque
from dhanhq import dhanhq

print("🎯 Sniper Strategy Engine (Dhan Execution Edition) Online.")

# 1. Connect to Redis Memory
redis_host = os.environ.get('REDIS_HOST', 'localhost')
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# 2. Authenticate with Dhan (using our hidden .env keys)
client_id = os.environ.get("DHAN_CLIENT_ID")
access_token = os.environ.get("DHAN_ACCESS_TOKEN")

dhan = None
if client_id and client_id != "YOUR_CLIENT_ID_HERE":
    dhan = dhanhq(client_id, access_token)
    print("🔓 Dhan Execution Module Authenticated.")
else:
    print("⏳ Running in Simulation Mode (No API Keys found).")

# 3. Strategy Parameters
price_history = deque(maxlen=10)
current_position = None 
TRADE_QUANTITY = 50 # 1 Lot of Nifty

while True:
    try:
        data = cache.get("LATEST_NIFTY")
        if data:
            tick = json.loads(data)
            price = float(tick['price'])
            
            if not price_history or price_history[-1] != price:
                price_history.append(price)
                
                if len(price_history) == 10:
                    sma = sum(price_history) / 10
                    
                    # 🚀 BUY LOGIC
                    if price > sma and current_position != 'LONG':
                        print(f"🚀 [SIGNAL] Price {price} > SMA {sma:.2f}. EXECUTING BUY...")
                        
                        if dhan:
                            # REAL TRADE CODE (Commented out for your safety)
                            # dhan.place_order(tag='Unicorn', transaction_type=dhan.BUY, 
                            # exchange_segment=dhan.NSE, product_type=dhan.INTRA,
                            # order_type=dhan.MARKET, quantity=TRADE_QUANTITY, security_id='13')
                            print("✅ PAPER TRADE: BOUGHT 50 QTY NIFTY")
                        
                        current_position = 'LONG'
                        
                    # 🩸 SELL LOGIC
                    elif price < sma and current_position != 'SHORT':
                        print(f"🩸 [SIGNAL] Price {price} < SMA {sma:.2f}. EXECUTING SELL...")
                        
                        if dhan:
                            # REAL TRADE CODE (Commented out for your safety)
                            # dhan.place_order(tag='Unicorn', transaction_type=dhan.SELL, 
                            # exchange_segment=dhan.NSE, product_type=dhan.INTRA,
                            # order_type=dhan.MARKET, quantity=TRADE_QUANTITY, security_id='13')
                            print("✅ PAPER TRADE: SOLD 50 QTY NIFTY")
                            
                        current_position = 'SHORT'
                        
        time.sleep(0.1)
    except Exception as e:
        print(f"⚠️ Strategy Error: {e}")
        time.sleep(1)
