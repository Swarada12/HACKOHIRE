import requests
import json
import time

customer_id = "CUSR-100001"
base_url = "http://127.0.0.1:8000"

print(f"--- Testing Master Orchestrator (No AI) ---")
try:
    res = requests.post(f"{base_url}/analyze_customer_risk", json={"input_data": {"customer_id": customer_id}}, timeout=30)
    data = res.json()
    print(f"Status: {res.status_code}")
    print(f"GenAI Narrative: {data['risk_analysis']['genai_narrative']!r}")
    print(f"Intervention Message: {data['intervention']['message']!r}")
except Exception as e:
    print(f"Error: {e}")

print(f"\n--- Testing On-Demand GenAI Insights ---")
try:
    start_time = time.time()
    res = requests.post(f"{base_url}/generate_ai_insights", json={"input_data": {"customer_id": customer_id}}, timeout=30)
    end_time = time.time()
    data = res.json()
    print(f"Status: {res.status_code}")
    print(f"Time Taken: {end_time - start_time:.2f}s")
    print(f"GenAI Narrative (First 50 chars): {data['genai_narrative'][:50]}...")
    print(f"Personalized Message: {data['personalized_message']}")
except Exception as e:
    print(f"Error: {e}")
