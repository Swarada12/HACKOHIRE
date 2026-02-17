import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_loan_data():
    print("Generating Real-World Loan Data...")
    
    try:
        # Load Core Customers
        df_core = pd.read_csv("customers_core.csv")
        customers = df_core['customer_id'].tolist()
        incomes = df_core['monthly_salary'].tolist()
        
        loans = []
        
        np.random.seed(42) # Deterministic for consistent demo
        
        for i, cid in enumerate(customers):
            # Dynamic Logic based on Income
            salary = incomes[i]
            
            # Loan Amount: 10x to 40x of Monthly Salary
            multiplier = np.random.randint(10, 40)
            loan_amount = round(salary * multiplier, -3) # Round to nearest 1000
            
            # Tenure: 12 to 60 months
            tenure_months = np.random.choice([12, 24, 36, 48, 60])
            
            # Interest Rate: 10% to 18%
            roi = np.random.uniform(10, 18)
            
            # EMI Calculation (Standard Formula)
            r = roi / 12 / 100
            emi = loan_amount * r * (1 + r)**tenure_months / ((1 + r)**tenure_months - 1)
            emi = round(emi, 0)
            
            # Loan Progress (How many months paid?)
            # Randomly 10% to 90% through the tenure
            months_paid = int(tenure_months * np.random.uniform(0.1, 0.9))
            
            # Total Paid Calculation
            total_paid = emi * months_paid
            
            # Start Date
            start_date = (datetime.now() - timedelta(days=months_paid*30)).strftime('%Y-%m-%d')
            
            loans.append({
                "customer_id": cid,
                "loan_contract_id": f"LN-{cid[-6:]}",
                "loan_amount": loan_amount,
                "monthly_emi": emi,
                "tenure_months": tenure_months,
                "interest_rate": round(roi, 1),
                "total_repaid": total_paid,
                "installments_paid": months_paid,
                "start_date": start_date,
                "status": "Active"
            })
            
        # Create DataFrame
        df_loans = pd.DataFrame(loans)
        df_loans.to_csv("loans.csv", index=False)
        print(f"✅ Generated loans.csv with {len(df_loans)} records.")
        print(df_loans.head())
        
    except Exception as e:
        print(f"❌ Error generating loan data: {e}")

if __name__ == "__main__":
    generate_loan_data()
