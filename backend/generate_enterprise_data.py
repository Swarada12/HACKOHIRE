import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os

# Configuration
NUM_CUSTOMERS = 10000
DAYS_OF_HISTORY = 180
START_DATE = datetime.now() - timedelta(days=DAYS_OF_HISTORY)

def generate_enterprise_dataset():
    print(f"Generating enterprise dataset with risk labels for {NUM_CUSTOMERS} customers...")
    
    # 1. Customers Core (Demographics & Baseline + Legacy Banking Fields)
    customers = []
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']
    products = ['Personal Loan', 'Home Loan', 'Credit Card', 'Auto Loan', 'Gold Loan']
    
    first_names = ['Aarav', 'Vihaan', 'Aditya', 'Arjun', 'Sai', 'Ishaan', 'Krishna', 'Aaryan', 'Shaurya', 'Kabir', 'Ananya', 'Diya', 'Ishani', 'Myra', 'Aadhya', 'Saanvi', 'Kiara', 'Anvi', 'Sara', 'Riya']
    last_names = ['Sharma', 'Verma', 'Gupta', 'Malhotra', 'Kapoor', 'Singh', 'Reddy', 'Patel', 'Iyer', 'Chatterjee', 'Joshi', 'Nair', 'Aggarwal', 'Bose', 'Deshmukh']
    
    for i in range(NUM_CUSTOMERS):
        c_id = f"CUSR-{100000 + i}"
        name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        income = np.random.randint(400000, 5000000)
        
        # Legacy Fields Parity
        monthly_salary = income / 12
        
        # Risk Persona Distribution - RANDOMIZED (Same as setup_db.py)
        persona_roll = int(np.random.randint(0, 10))
        
        if persona_roll == 0: # Persona 1: Liquidity Crunch
            delay = int(np.random.randint(10, 25))
            util = float(np.random.uniform(10, 30))
            savings_change = float(np.random.uniform(-10, 5))
        elif persona_roll == 1: # Persona 2: Over-Leverage
            util = float(np.random.uniform(88, 99))
            delay = int(np.random.randint(0, 5))
            savings_change = float(np.random.uniform(-15, -5))
        elif persona_roll == 2: # Persona 3: Behavioral Drift
            savings_change = float(np.random.uniform(-30, -15))
            util = float(np.random.uniform(40, 70))
            delay = int(np.random.randint(0, 5))
        elif persona_roll == 3: # Persona 4: Cash Flow Failure
            savings_change = float(np.random.uniform(-55, -35))
            delay = int(np.random.randint(0, 5))
            util = float(np.random.uniform(50, 80))
        else: # Safe
            delay = int(np.random.randint(0, 3))
            util = float(np.random.uniform(10, 45))
            savings_change = float(np.random.uniform(2, 12))

        # Initial risk score - BALANCED & NORMALIZED (0-100)
        score = int(min(100, round(5 + (delay * 2.5) + (util * 0.4) + (abs(min(0, savings_change)) * 0.8))))
        
        # Ensure personas can reach Critical (85+)
        if persona_roll == 1 and util > 95: score = max(score, 87)
        if persona_roll == 3 and savings_change < -45: score = max(score, 88)
        
        lvl = 'Critical' if score >= 85 else 'High' if score >= 45 else 'Medium' if score >= 30 else 'Low'
        
        # Ability & Willingness
        ability = int(np.random.randint(20, 95))
        willingness = int(np.random.randint(30, 98))
        
        loan_amount = float(np.random.randint(50000, 5000000))
        monthly_emi = float(loan_amount / np.random.choice([12, 24, 36, 60]))
        
        if score > 70:
            ability = np.random.randint(15, 50) 
            if np.random.random() > 0.5:
                ability = np.random.randint(60, 90)
                willingness = np.random.randint(10, 40)
        
        rare_type = "Normal"
        if ability < 40 and willingness > 70: rare_type = "Victim of Circumstance"
        elif ability > 60 and willingness < 40: rare_type = "Strategic Defaulter"

        action = "Standard Monitoring"
        if delay > 15: action = f"📞 Call {name}: Salary Delay Relief"
        elif util > 85: action = f"🔒 Shield: Limit Cap at {int(util)}%"
        elif savings_change < -30: action = f"🛡️ Wellness: Savings Protection"

        customers.append({
            'customer_id': c_id,
            'name': name,
            'age': np.random.randint(22, 65),
            'city': np.random.choice(cities),
            'product_type': np.random.choice(products),
            'annual_income': income,
            'monthly_salary': round(monthly_salary, 2),
            'credit_score': np.random.randint(600, 850),
            'credit_utilization': round(util, 2),
            'savings_change_pct': round(savings_change, 2),
            'loan_amount': round(loan_amount, 2),
            'monthly_emi': round(monthly_emi, 2),
            'current_salary_delay_days': delay,
            'risk_score': score,
            'risk_level': lvl,
            'suggested_action': action,
            'ability_score': ability,
            'willingness_score': willingness,
            'rare_case_type': rare_type,
            'employment_type': np.random.choice(['Salaried', 'Self-Employed', 'Business']),
            'aadhar_no': f"{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}",
            'pan_no': f"{chr(np.random.randint(65, 90))}{chr(np.random.randint(65, 90))}{chr(np.random.randint(65, 90))}P{np.random.randint(1000, 9999)}{chr(np.random.randint(65, 90))}",
            'account_opened_date': (datetime.now() - timedelta(days=np.random.randint(365, 3650))).strftime('%Y-%m-%d')
        })
    
    df_customers = pd.DataFrame(customers)
    df_customers.to_csv("customers_core.csv", index=False)
    print("✓ Created customers_core.csv")

    # 2. Salary Credits (Last 12 months)
    salaries = []
    for _, row in df_customers.iterrows():
        c_id = row['customer_id']
        monthly_salary = row['monthly_salary']
        delay = row['current_salary_delay_days']
        score = row['risk_score']
        
        for m in range(12):
            date = datetime.now() - timedelta(days=30 * m)
            # Sync with current_salary_delay_days for the latest month
            m_delay = delay if m == 0 else np.random.randint(0, 5)
            # Signal 1: Salary reduction or delay history for high risk
            m_amt = monthly_salary if m > 2 else monthly_salary * (0.85 if score > 70 else 1.0)

            credit_date = datetime(date.year, date.month, 1) + timedelta(days=m_delay)
            salaries.append({
                'customer_id': c_id,
                'amount': round(m_amt, 2),
                'credit_date': credit_date.strftime('%Y-%m-%d'),
                'delay_days': m_delay,
                'employer': 'Tech Corp',
                'month_year': date.strftime('%Y-%m')
            })
    
    pd.DataFrame(salaries).to_csv("salary_history.csv", index=False)
    print("✓ Created salary_history.csv")

    # 3. Payment History (Transactions)
    payments = []
    categories = ['Utility', 'Rent', 'EMI', 'Shopping', 'Food', 'Gambling', 'Lending App', 'Entertainment', 'Investment']
    for _, row in df_customers.iterrows():
        c_id = row['customer_id']
        score = row['risk_score']
        
        num_tx = np.random.randint(30, 70)
        for _ in range(num_tx):
            cat = np.random.choice(categories, p=[0.15, 0.05, 0.1, 0.25, 0.2, 0.05, 0.05, 0.1, 0.05])
            amt = np.random.exponential(2000)
            if cat == 'Rent': amt = np.random.uniform(10000, 40000)
            if cat == 'EMI': amt = np.random.uniform(5000, 25000)
            
            # Distress Signals for high risk
            if score > 60:
                if np.random.random() > 0.8:
                    cat = 'Gambling'
                    amt = np.random.randint(1000, 10000)
                if np.random.random() > 0.9:
                    cat = 'Lending App'
                    amt = 5000.0

            date = datetime.now() - timedelta(days=np.random.randint(0, DAYS_OF_HISTORY))
            
            txn_type = 'DEBIT'
            if cat == 'EMI':
                # Signal: EMI Bounce
                if score > 80 and np.random.random() > 0.7:
                     txn_type = 'EMI_BOUNCE'
                     amt = 0.0

            payments.append({
                'customer_id': c_id,
                'transaction_id': str(uuid.uuid4())[:8].upper(),
                'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                'category': cat,
                'amount': round(amt, 2),
                'method': np.random.choice(['UPI', 'Debit Card', 'Net Banking', 'Auto-Debit']),
                'merchant': 'Merchant', # Simplified
                'transaction_type': txn_type
            })
    pd.DataFrame(payments).to_csv("payment_history.csv", index=False)
    print("✓ Created payment_history.csv")

    # 4. App Activity Logs
    activity = []
    actions = ['Login', 'Check Balance', 'Statement View', 'Loan Inquiry', 'Support Chat', 'Profile Update']
    for _, row in df_customers.iterrows():
        c_id = row['customer_id']
        score = row['risk_score']
        
        num_logs = np.random.randint(10, 100)
        for _ in range(num_logs):
            action = np.random.choice(actions)
            date = datetime.now() - timedelta(days=np.random.randint(0, DAYS_OF_HISTORY))
            hour = np.random.randint(0, 24)
            # Signal 9: Late night logins
            if score > 75 and np.random.random() > 0.7:
                hour = np.random.randint(1, 4)

            activity.append({
                'customer_id': c_id,
                'timestamp': date.replace(hour=hour).strftime('%Y-%m-%d %H:%M:%S'),
                'action': action,
                'session_duration_sec': np.random.randint(10, 600),
                'device': np.random.choice(['iOS', 'Android', 'Web'])
            })
    pd.DataFrame(activity).to_csv("app_activity.csv", index=False)
    print("✓ Created app_activity.csv")

    # 5. Utility Payments (New Signal)
    utility = []
    for _, row in df_customers.iterrows():
        c_id = row['customer_id']
        score = row['risk_score']
        
        for m in range(1, 4):
            bill_date_dt = datetime.now() - timedelta(days=30*m)
            # High risk users pay late
            days_late = np.random.randint(0, 5)
            if score > 60: days_late = np.random.randint(5, 20)
            
            pay_date_dt = bill_date_dt + timedelta(days=days_late)
            amt = np.random.randint(800, 3000)
            utility.append({
                'customer_id': c_id,
                'bill_date': bill_date_dt.strftime('%Y-%m-%d'),
                'payment_date': pay_date_dt.strftime('%Y-%m-%d'),
                'amount': amt,
                'category': 'Electricity',
                'days_past_due': days_late
            })
    pd.DataFrame(utility).to_csv("utility_payments.csv", index=False)
    print("✓ Created utility_payments.csv")

    print("\nEnterprise Data Generation with Risk Labels Complete.")

if __name__ == "__main__":
    generate_enterprise_dataset()
