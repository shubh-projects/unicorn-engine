import pandas as pd
import numpy as np
import json
import os
import sys

print("Unicorn Engine V3.0: Strategy Injector Online...")

# Catch the parameters sent by the API (Defaults to 50/200 if none sent)
FAST_MA = int(sys.argv[1]) if len(sys.argv) > 1 else 50
SLOW_MA = int(sys.argv[2]) if len(sys.argv) > 2 else 200
INITIAL_CAPITAL = 100000.0

np.random.seed(42)
dates = pd.date_range(start="2018-01-01", end="2023-12-31", freq="B")
returns = np.random.normal(0.0004, 0.012, len(dates)) 
prices = 10000 * np.exp(np.cumsum(returns))

df = pd.DataFrame({'date': dates, 'close': prices})

# The math is now completely dynamic based on user input!
df['fast_ma'] = df['close'].rolling(window=FAST_MA).mean()
df['slow_ma'] = df['close'].rolling(window=SLOW_MA).mean()
df['signal'] = 0
df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1
df['market_return'] = df['close'].pct_change()
df['strategy_return'] = df['signal'].shift(1) * df['market_return']

df = df.dropna()
df['portfolio_value'] = INITIAL_CAPITAL * (1 + df['strategy_return']).cumprod()

final_value = df['portfolio_value'].iloc[-1]
total_roi = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

chart_data = []
for index, row in df.iterrows():
    chart_data.append({
        "t": row['date'].strftime('%Y-%m-%d %H:%M:%S'),
        "portfolio": round(row['portfolio_value'], 2),
        "close": round(row['close'], 2),
        "fast_ma": round(row['fast_ma'], 2),
        "slow_ma": round(row['slow_ma'], 2)
    })

output = {
    "summary": {"initial": INITIAL_CAPITAL, "final": round(final_value, 2), "roi": f"{total_roi:.2f}%"},
    "chart": chart_data
}

with open("/app/backtest_results.json", "w") as f:
    json.dump(output, f)

print(f"Backtest Complete. Fast: {FAST_MA}, Slow: {SLOW_MA}")
