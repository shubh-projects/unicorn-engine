import pandas as pd
import numpy as np
import datetime
import os

print("🧬 Unicorn Engine: Initializing Market Synthesizer...")

# Parameters for 1 Year of 1-Minute Candles (approx 250 trading days * 375 minutes)
num_candles = 93750 
start_price = 42000.0
volatility = 0.0005 # 0.05% per minute movement

print(f"⏳ Generating {num_candles} rows of historical Bank Nifty data...")

# Generate a time index (1 minute intervals during market hours)
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
date_rng = pd.date_range(start=start_date, periods=num_candles, freq='min')

# Generate realistic price movements using a Random Walk
returns = np.random.normal(loc=0.000001, scale=volatility, size=num_candles)
price_path = start_price * np.exp(np.cumsum(returns))

# Create Open, High, Low, Close (OHLC) adding minor noise
df = pd.DataFrame(index=date_rng)
df['Open'] = price_path
df['High'] = price_path * (1 + np.abs(np.random.normal(0, volatility/2, num_candles)))
df['Low'] = price_path * (1 - np.abs(np.random.normal(0, volatility/2, num_candles)))
df['Close'] = price_path * (1 + np.random.normal(0, volatility/4, num_candles))
df['Volume'] = np.random.randint(1000, 50000, size=num_candles)

# Fix High/Low boundaries
df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)

# Ensure the folder exists
os.makedirs("historical_data", exist_ok=True)

# Save to CSV
file_path = "historical_data/banknifty_1yr.csv"
df.to_csv(file_path, index_label='Timestamp')

print(f"✅ Data Synthesis Complete! Saved to {file_path}")
print(f"📊 Total Rows: {len(df)} | Size: {os.path.getsize(file_path) / (1024*1024):.2f} MB")
