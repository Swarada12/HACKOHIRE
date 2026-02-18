import requests
import json

def verify_list():
    try:
        r = requests.post('http://localhost:8000/list_customers', json={'input_data': {'risk_filter': 'All'}})
        data = r.json()
        
        customers = data.get('customers', [])
        ananya = next((c for c in customers if c['customer_id'] == 'CUSR-100001'), None)
        
        if ananya:
            print(f"Customer: {ananya['name']} ({ananya['customer_id']})")
            print(f"Signal Count: {len(ananya['signals'])}")
            print(f"Signals: {json.dumps(ananya['signals'], indent=2)}")
        else:
            print("CUSR-100001 not found in list.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_list()
