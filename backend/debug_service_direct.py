import asyncio
import sys
import os

# Ensure backend dir is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.service import BankRiskService, CustomerListInput
    print("Imported BankRiskService successfully.")
except ImportError:
    # Fallback if running from backend dir
    sys.path.append(os.getcwd())
    from service import BankRiskService, CustomerListInput
    print("Imported BankRiskService (fallback) successfully.")

async def test_direct():
    print("Instantiating Service...")
    svc = BankRiskService()
    print("Service Instantiated.")
    
    print("Preparing Input...")
    inp = CustomerListInput(risk_filter="All", search="")
    
    print("Calling list_customers...")
    try:
        res = await svc.list_customers(inp)
        print(f"Success! Got {len(res.get('customers', []))} customers.")
    except Exception as e:
        print(f"Error calling list_customers: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct())
