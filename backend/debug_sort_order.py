import requests
import json

BASE_URL = "http://localhost:8000"

def test_sort(filter, expect_field, ascending=True):
    print(f"\nTesting Filter: {filter} (Expect sort by {expect_field} {'ASC' if ascending else 'DESC'})")
    
    payload = {
        "input_data": {
            "risk_filter": filter,
            "search": "",
            "enrich_ml": False,
            "limit": 20
        }
    }
    
    try:
        res = requests.post(f"{BASE_URL}/list_customers", json=payload, timeout=10)
        if res.status_code == 200:
            customers = res.json().get("customers", [])
            print(f"Stats: Fetched {len(customers)} customers.")
            
            if not customers:
                print("WARNING: No customers returned.")
                return

            values = []
            if expect_field == 'customer_id':
                values = [c.get('customer_id') for c in customers]
            elif expect_field == 'risk_score':
                values = [c.get('risk_score', 0) for c in customers]
            
            print(f"First 10 Values: {values[:10]}")
            
            is_sorted = False
            if ascending:
                is_sorted = all(values[i] <= values[i+1] for i in range(len(values)-1))
            else:
                is_sorted = all(values[i] >= values[i+1] for i in range(len(values)-1))
            
            if is_sorted:
                print("✅ SORT ORDER VERIFIED")
            else:
                print("❌ SORT ORDER FAILED")
                # find where it failed
                for i in range(len(values)-1):
                    if ascending and values[i] > values[i+1]:
                        print(f"  Fail at index {i}: {values[i]} > {values[i+1]}")
                        break
                    if not ascending and values[i] < values[i+1]:
                        print(f"  Fail at index {i}: {values[i]} < {values[i+1]}")
                        break
        else:
            print(f"Request Failed: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test 1: All -> Expect ID ASC
    test_sort("All", "customer_id", ascending=True)
    
    # Test 2: Critical -> Expect Risk Score DESC
    test_sort("Critical", "risk_score", ascending=False)
