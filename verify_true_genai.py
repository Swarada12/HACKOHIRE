import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.service import BankRiskService, RiskInput

async def verify_true_genai():
    from service import feature_store
    service = BankRiskService()
    
    print("\n--- TRUE GENAI INTELLIGENCE AUDIT ---")
    customer_list = feature_store.get_customers(limit=5)
    customers = customer_list['customers']
    
    for c in customers:
        cid = c['customer_id']
        name = c['name']
        
        # Analyze Risk
        res = await service.analyze_customer_risk(RiskInput(customer_id=cid))
        score = res['risk_analysis']['score']
        narrative = res['risk_analysis']['genai_narrative']
        intervention_msg = res['intervention']['message']
        gap = res['intervention'].get('spending_gap', 0)
        
        print(f"\nID: {cid} | Name: {name} | Score: {score}")
        print(f"Spending Gap: Rs. {gap}")
        print(f"Lead Stressor: {res['intervention']['lead_stressor']}")
        print(f"Narrative Preview: {narrative[:120]}...")
        print(f"Intervention Preview: {intervention_msg[:120]}...")
        
        if "Deterministic Fallback" in narrative:
            print("⚠️ WARNING: Static template detected.")
        else:
            print("✅ SUCCESS: Unique LLM Narrative generated.")

if __name__ == "__main__":
    asyncio.run(verify_true_genai())
