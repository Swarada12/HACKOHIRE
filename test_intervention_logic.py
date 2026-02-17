import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from intervention_engine import InterventionEngine

def test_intervention():
    ie = InterventionEngine()
    features = {'name': 'John Doe', 'f_savings_account_balance': 50000, 'f_savings_change_pct': -13, 'f_monthly_salary': 60000, 'f_loan_amount': 200000, 'f_monthly_emi': 5000}
    
    # 1. Smart Saver
    res1 = ie.generate_intervention("T1", features, {'fusion_score': 30}, {})
    print(f"WELLNESS: {'✅' if 'Smart Saver' in res1['message'] and '6500' in res1['message'] else '❌'}")

    # 2. Salary Advance
    features['t_current_salary_delay'] = 5
    res2 = ie.generate_intervention("T2", features, {'fusion_score': 55}, {})
    print(f"SALARY_ADV: {'✅' if 'Rs.24000' in res2['message'] else '❌'}")

    # 3. Moratorium
    features['t_current_salary_delay'] = 0
    res3 = ie.generate_intervention("T3", features, {'fusion_score': 85}, {})
    print(f"MORATORIUM: {'✅' if 'breathing room' in res3['message'] else '❌'}")

if __name__ == "__main__":
    test_intervention()
