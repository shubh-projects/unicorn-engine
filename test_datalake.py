import pandas as pd
import os

print("🧬 Unicorn Engine: Accessing Historical Data Lake...")
file_path = "historical_data/historical_nifty.csv"

if not os.path.exists(file_path):
    print(f"❌ ERROR: Cannot find {file_path}")
else:
    df = pd.read_csv(file_path, nrows=5)
    print(f"✅ Data Lake Connected!")
    print(f"📋 Columns Detected: {list(df.columns)}")
