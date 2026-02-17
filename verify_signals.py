import sys
import os
import json
import asyncio

# Ensure paths correctly point to backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from service import BankRiskService, RiskInput, CustomerListInput

service = BankRiskService()

async def verify_signals():
    print("\n--- Verifying Enterprise Data Migration & Signals ---")
    
    # 1. Verify 300 customers
    customers_res = await service.list_customers(CustomerListInput(risk_filter="All"))
    count = customers_res.get('stats', {}).get('total', 0)
    print(f"Total Customers in DB: {count}")
    if count >= 300:
        print("✅ PASS: 300+ Customers seeded in SQLite.")
    else:
        print(f"❌ FAIL: Expected 300, found {count}.")

    # 2. Verify Dynamic EMI Prediction
    print("\n--- Checking EMI Prediction Dynamics ---")
    customer_ids = ['CUSR-100001', 'CUSR-100010', 'CUSR-100020', 'CUSR-100030', 'CUSR-100040']
    probabilities = []
    
    for cid in customer_ids:
        res = await service.analyze_customer_risk(RiskInput(customer_id=cid))
        if 'error' not in res:
            prob = res['repayment_stats'].get('emi_probability', 0)
            probabilities.append(prob)
            print(f"Customer {cid}: EMI Probability = {prob}%")
        else:
            print(f"Customer {cid}: Error fetching data")

    unique_probs = set(probabilities)
    print(f"\nUnique Probabilities found: {unique_probs}")
    
    if len(unique_probs) > 1:
        print("✅ PASS: EMI Probability is dynamic (not fixed at 50%).")
    else:
        print("❌ FAIL: All EMI Probabilities are identical.")

if __name__ == "__main__":
    asyncio.run(verify_signals())
