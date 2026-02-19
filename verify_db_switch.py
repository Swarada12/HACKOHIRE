import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.feature_store import FeatureStore

def verify_db():
    print("--- VERIFYING DB SWITCH ---")
    store = FeatureStore()
    print(f"Connected DB Path: {store.db_path}")
    
    if "bank_risk(1).db" in store.db_path:
        print("✅ Correctly pointing to bank_risk(1).db")
    else:
        print("❌ Still pointing to old DB!")
        
    conn = store.get_conn()
    try:
        count = pd.read_sql_query("SELECT COUNT(*) as c FROM customers", conn).iloc[0]['c']
        print(f"Customer Count in DB: {count}")
    except Exception as e:
        print(f"❌ Error querying DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_db()
