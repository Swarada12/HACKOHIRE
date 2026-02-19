import requests
import time

def test_list_customers():
    url = "http://localhost:8000/list_customers"
    payload = {
        "input_data": {
            "risk_filter": "All",
            "search": "",
            "enrich_ml": True,
            "limit": 500
        }
    }
    
    print("Testing list_customers with 500 enrichements...")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=60)
        end_time = time.time()
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            customers = data.get("customers", [])
            print(f"Received {len(customers)} customers")
            if customers:
                first = customers[0]
                print(f"Sample Customer: {first.get('name')} (ID: {first.get('customer_id')}) - Score: {first.get('risk_score')}")
                print(f"Signals: {first.get('signals')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_list_customers()
