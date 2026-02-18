import sqlite3
import requests
import json

def verify():
    conn = sqlite3.connect('backend/bank_risk.db')
    cursor = conn.cursor()
    
    # Find a customer with Utility Delay > 10 days
    cursor.execute("SELECT customer_id, days_past_due FROM utility_payments WHERE days_past_due > 10 LIMIT 1")
    util_customer = cursor.fetchone()
    
    # Find a customer with EMI Bounce
    cursor.execute("SELECT customer_id FROM transactions WHERE transaction_type = 'EMI_BOUNCE' LIMIT 1")
    bounce_customer = cursor.fetchone()
    
    conn.close()
    
    print(f"Testing Utility Delay User: {util_customer}")
    print(f"Testing EMI Bounce User: {bounce_customer}")
    
    if util_customer:
        cid = util_customer[0]
        try:
            r = requests.post('http://localhost:8000/analyze_customer_risk', json={'input_data': {'customer_id': cid}})
            res = r.json()
            print(f"\nAPI Result for {cid}:")
            print(json.dumps(res['risk_analysis']['agent_reasoning'], indent=2))
        except Exception as e:
            print(f"API Failed: {e}")

    if bounce_customer and bounce_customer[0] != util_customer[0]:
        cid = bounce_customer[0]
        try:
            r = requests.post('http://localhost:8000/analyze_customer_risk', json={'input_data': {'customer_id': cid}})
            res = r.json()
            print(f"\nAPI Result for {cid}:")
            print(json.dumps(res['risk_analysis']['agent_reasoning'], indent=2))
        except Exception as e:
            print(f"API Failed: {e}")

if __name__ == "__main__":
    verify()
