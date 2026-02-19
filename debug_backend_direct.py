import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.service import BankRiskService, RiskInput

async def debug_logic():
    print("Initializing Service...")
    svc = BankRiskService()
    
    print("Testing analyze_customer_risk DIRECTLY...")
    inp = RiskInput(customer_id="CUSR-100001")
    
    try:
        # We need to mock the context if service uses lifespan, but here it constructs global objects
        # We might need to manually call 'sync_pending_customers' if needed, but let's try the main method
        res = await svc.analyze_customer_risk(inp)
        print("\nSUCCESS! Result snippet:")
        print(str(res)[:500])
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_logic())
