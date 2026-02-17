
import requests
import json

try:
    # BentonML 1.0+ often expects POST for functions
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:8000/get_dashboard_stats', headers=headers, json={})
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print("Keys:", data.keys())
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Connection failed: {e}")
