import requests
import json

BASE_URL = "http://localhost:8000"

def verify_count():
    payload = {
        "input_data": {
            "risk_filter": "All",
            "search": "",
            "enrich_ml": False,
            "limit": 1000
        }
    }
    
    try:
        res = requests.post(f"{BASE_URL}/list_customers", json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            customers = data.get("customers", [])
            total = data.get("total", 0)
            print(f"Total customers in response: {len(customers)}")
            print(f"Total count reported by API: {total}")
            
            if len(customers) >= 500:
                print("✅ SUCCESS: 500+ customers verified.")
            else:
                print(f"❌ FAILURE: Only {len(customers)} customers found.")
        else:
            print(f"API Error: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_count()
