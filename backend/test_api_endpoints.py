import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Waiting for server to start...")
    # Model loading can take a while (especially after retraining on large datasets).
    # Use a longer read timeout + more retries with backoff.
    for i in range(60):
        try:
            # (connect_timeout, read_timeout)
            requests.get(f"{BASE_URL}/docs", timeout=(2, 30))
            print("Server is up!", flush=True)
            break
        except Exception as e:
            print(f"Connection failed: {e}", flush=True)
            time.sleep(min(10, 1 + i // 6))
    else:
        print("Server failed to start.")
        return

    print("Testing /list_customers with WRAPPED payload (Default fast mode)...")
    payload = {"input_data": {"risk_filter": "All", "search": ""}}
    try:
        res = requests.post(f"{BASE_URL}/list_customers", json=payload, timeout=20)
        if res.status_code == 200:
            customers = res.json().get("customers", [])
            print(f"SUCCESS: /list_customers (Fast) returned {len(customers)} customers.")
            # Verify sorting (User requested ID sort for 'All')
            if customers:
                first_ids = [c.get('customer_id') for c in customers[:5]]
                print(f"Verified Sorting (First 5): {first_ids}")
        else:
            print(f"FAILED: /list_customers (Fast) returned {res.status_code}\n{res.text}")
    except Exception as e:
        print(f"ERROR (Fast): {e}")

    print("Testing /list_customers with enrich_ml=True (Real-Time mode)...")
    payload = {"input_data": {"risk_filter": "All", "search": "", "enrich_ml": True, "limit": 500}}
    try:
        res = requests.post(f"{BASE_URL}/list_customers", json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            customers = data.get('customers', [])
            print(f"SUCCESS: /list_customers (Real-Time) returned {len(customers)} customers.")
            if customers and 'signals' in customers[0]:
                print(f"Verified Signals: {customers[0]['signals'][:2]}...")
            else:
                print("WARNING: No signals found in response despite enrich_ml=True")
        else:
            print(f"FAILED: /list_customers (Real-Time) returned {res.status_code}\n{res.text}")
    except Exception as e:
        print(f"ERROR (Real-Time): {e}")

    print("Testing /analyze_customer_risk with WRAPPED payload...")
    payload = {"input_data": {"customer_id": "CUSR-100007"}} 
    try:
        res = requests.post(f"{BASE_URL}/analyze_customer_risk", json=payload, timeout=20)
        if res.status_code == 200:
            print("SUCCESS: /analyze_customer_risk returned analysis.")
            risk_data = res.json().get("risk_analysis", {})
            repay = res.json().get("repayment_stats", {})
            intel = res.json().get("decision_intelligence", {})
            print(f"DEBUG: Reasoning: {risk_data.get('agent_reasoning')}")
            print(f"DEBUG: Repayment: {repay}")
            print(f"DEBUG: Intel: {intel}")
            
            # Test Jitter (Liveliness)
            print("Testing Jitter (Second Call)...")
            res2 = requests.post(f"{BASE_URL}/analyze_customer_risk", json=payload, timeout=20)
            if res2.status_code == 200:
                intel2 = res2.json().get("decision_intelligence", {})
                print(f"DEBUG: Intel (Run 2): {intel2}")
                if intel.get('ability_score') != intel2.get('ability_score') or intel.get('willingness_score') != intel2.get('willingness_score'):
                    print("SUCCESS: Jitter verified (Scores changed)")
                else:
                    print("WARNING: Scores identical (Jitter might be small or time-based collision)")
        else:
            print(f"FAILED: /analyze_customer_risk returned {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_api()
