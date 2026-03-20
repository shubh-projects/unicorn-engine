import pandas as pd
import numpy as np
import os

DATA_PATH = "historical_data/historical_nifty.csv"
INITIAL_CAPITAL = 100000.0

def run_backtest():
    print("🚀 [SIMULATOR] Running Dynamic SMA Strategy...")
    df = pd.read_csv(DATA_PATH, usecols=['date', 'close'])
    
    # CALCULATE SMA (The 20-minute average)
    df['sma'] = df['close'].rolling(window=20).mean()
    
    prices = df['close'].values
    sma = df['sma'].values
    dates = df['date'].values
    
    balance = INITIAL_CAPITAL
    position = 0
    trades = 0

    for i in range(20, len(prices)):
        current_price = prices[i]
        current_sma = sma[i]
        
        # BUY: Price crosses ABOVE the average
        if current_price > current_sma and position == 0:
            shares = int(balance // current_price)
            balance -= (shares * current_price)
            position = shares
            trades += 1

        # SELL: Price crosses BELOW the average
        elif current_price < current_sma and position > 0:
            balance += (position * current_price)
            position = 0
            trades += 1

    final_value = balance + (position * prices[-1])
    print(f"🏁 BACKTEST COMPLETE")
    print(f"📈 Final Portfolio: ₹{final_value:,.2f}")
    print(f"🔄 Total Trades:    {trades}")

if __name__ == "__main__":
    run_backtest()
