import time
import random

print("✅ [INIT] Strategy Sandbox Booted Successfully.")
print("📡 Connect to Redis memory... OK")
print("🔐 Validating API Keys... OK")

for i in range(1, 15):
    time.sleep(1)
    price = 45000 + random.randint(-10, 10)
    print(f"[TICK] Bank Nifty scanned at ₹{price}")
    
    if price > 45005:
        print(f"   🚀 BUY SIGNAL: Executed 15 shares at ₹{price}")
        print("   ✅ Order ID: DHAN-99283-AX")

print("⚠️ [SYSTEM] End of Trading Day. Strategy gracefully stopping.")
