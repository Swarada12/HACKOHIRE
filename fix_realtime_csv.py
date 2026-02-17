
import pandas as pd
from datetime import datetime, timedelta
import random

# Load Realtime Data
try:
    df = pd.read_csv('backend/realtime_banking_data.csv')
    print("Loaded CSV successfully.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# 1. Fix Customer IDs (CUST -> CUSR and align numbers)
# Assuming CUSR matches CUST but with different prefix format
# CUST-1000 -> CUSR-100000 
# Mapping strategy: Base ID + offset?
# Let's align based on the assumption that CUST-1000 is the first customer and corresponds to CUSR-100000
# Actually, let's just make sure they overlap with the core set.
# CUSR IDs start at CUSR-100000 and go up.
# CUST IDs start at CUST-1000.
# Let's map CUST-1000 -> CUSR-100000, CUST-1001 -> CUSR-100001, etc.

def fix_id(cust_id):
    if isinstance(cust_id, str) and cust_id.startswith('CUST-'):
        num_part = int(cust_id.split('-')[1])
        # Map 1000 to 100000
        new_num = 100000 + (num_part - 1000)
        return f"CUSR-{new_num}"
    return cust_id

df['customer_id'] = df['customer_id'].apply(fix_id)
print("Updated Customer IDs.")

# 2. Fix Timestamps (Shift to Now)
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    max_ts = df['timestamp'].max()
    now = datetime.now()
    
    # Calculate shift
    delta = now - max_ts
    
    # Apply shift
    df['timestamp'] = df['timestamp'] + delta
    print(f"Shifted timestamps by {delta}. Max time is now {df['timestamp'].max()}")

# Save back to CSV
df.to_csv('backend/realtime_banking_data.csv', index=False)
print("Saved updated CSV.")
