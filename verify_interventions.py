import requests
import json

def test_interventions():
    base_url = "http://127.0.0.1:8000"
    
    # Fetch first 50 customers to find diverse profiles
    r_list = requests.post(f"{base_url}/list_customers", json={"input_data": {"risk_filter": "All"}})
    customers = r_list.json().get('customers', [])[:50]
    
    print(f"--- INTERVENTION DIVERSITY TEST (Sample N={len(customers)}) ---")
    
    seen_offers = set()
    
    for c in customers:
        cid = c['customer_id']
        r = requests.post(f"{base_url}/analyze_customer_risk", json={"input_data": {"customer_id": cid}})
        data = r.json()
        
        inte = data['intervention']
        offer = inte['recommended_offer']
        stressor = inte.get('lead_stressor', 'N/A')
        
        if offer not in seen_offers:
            print(f"\n[NEW PATTERN FOUND: {offer}]")
            print(f"Customer: {cid} | Risk: {data['risk_analysis']['score']}")
            print(f"Lead Stressor: {stressor}")
            print(f"Context: {data['decision_intelligence']['case_type']}")
            print(f"Message: {inte['message'][:100]}...")
            seen_offers.add(offer)

    print(f"\nTotal Unique Offers Found: {len(seen_offers)}")

if __name__ == "__main__":
    test_interventions()
