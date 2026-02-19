import sqlite3
import os
import sys
import pandas as pd

# Add current directory and backend directory to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.service import BankRiskService
from backend.feature_store import FeatureStore

async def test_jit_autofetch():
    print("--- REAL-TIME AI AUTOFETCH TEST ---")
    store = FeatureStore()
    
    # 1. Manually insert a "Mystery" customer directly into DB
    conn = sqlite3.connect('backend/bank_risk.db')
    cursor = conn.cursor()
    
    mystery_id = "CUSR-MYSTERY-999"
    print(f"1. Manually inserting {mystery_id} into DB via SQL...")
    
    cursor.execute("DELETE FROM customers WHERE customer_id = ?", (mystery_id,))
    cursor.execute("""
        INSERT INTO customers (customer_id, name, city, product_type, monthly_salary, credit_utilization, current_salary_delay_days, risk_score)
        VALUES (?, 'Mystery User', 'Mumbai', 'Credit Card', 80000, 95.0, 15, NULL)
    """, (mystery_id,))
    conn.commit()
    
    # Verify it has NO score
    row = pd.read_sql_query(f"SELECT risk_score, risk_level FROM customers WHERE customer_id = '{mystery_id}'", conn)
    print(f"   Initial DB State: Score={row['risk_score'].iloc[0]}, Level={row['risk_level'].iloc[0]}")
    conn.close()

    # 2. Simulate Website Dashboard Loading (calls get_dashboard_stats)
    print("\n2. Simulating Website Dashboard Load (Calling Service API)...")
    service = BankRiskService()
    await service.get_dashboard_stats()
    
    # 3. Check if DB was automatically updated by the AI Engine
    print("\n3. Checking if AI Engine auto-analyzed the new user...")
    conn = sqlite3.connect('backend/bank_risk.db')
    row_final = pd.read_sql_query(f"SELECT risk_score, risk_level FROM customers WHERE customer_id = '{mystery_id}'", conn)
    
    score = row_final['risk_score'].iloc[0]
    level = row_final['risk_level'].iloc[0]
    
    print(f"   Final DB State: Score={score}, Level={level}")
    
    if score is not None and score > 0:
        print("\n✅ SUCCESS: AI Engine detected the manual DB entry and performed real-time inference!")
    else:
        print("\n❌ FAILED: AI Engine did not catch the new user.")
    
    conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_jit_autofetch())
