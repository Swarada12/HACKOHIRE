
import pandas as pd
import os

files = [
    "customers_core.csv",
    "app_activity.csv",
    "payment_history.csv",
    "salary_history.csv",
    "realtime_banking_data.csv"
]

target_id = "CUSR-101449"

print(f"Checking for {target_id} in BACKEND dir...")

for f in files:
    try:
        if not os.path.exists(f):
            print(f"[MISSING] {f}")
            continue
            
        df = pd.read_csv(f)
        matches = df[df['customer_id'] == target_id]
        if not matches.empty:
            print(f"  ✅ {f}: FOUND {len(matches)} records.")
            if f == 'realtime_banking_data.csv':
                print("    Sample Realtime Data:")
                print(matches.head(1).to_dict(orient='records'))
        else:
            print(f"  ❌ {f}: NOT FOUND")
            
    except Exception as e:
        print(f"  ⚠️ Error reading {f}: {e}")
