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
    print(f"Generating enterprise dataset for {NUM_CUSTOMERS} customers...")
    
    # 1. Customers Core (Demographics & Baseline)
    customers = []
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']
    products = ['Personal Loan', 'Home Loan', 'Credit Card', 'Auto Loan', 'Gold Loan']
    
    first_names = ['Aarav', 'Vihaan', 'Aditya', 'Arjun', 'Sai', 'Ishaan', 'Krishna', 'Aaryan', 'Shaurya', 'Kabir', 'Ananya', 'Diya', 'Ishani', 'Myra', 'Aadhya', 'Saanvi', 'Kiara', 'Anvi', 'Sara', 'Riya']
    last_names = ['Sharma', 'Verma', 'Gupta', 'Malhotra', 'Kapoor', 'Singh', 'Reddy', 'Patel', 'Iyer', 'Chatterjee', 'Joshi', 'Nair', 'Aggarwal', 'Bose', 'Deshmukh']
    
    for i in range(NUM_CUSTOMERS):
        c_id = f"CUSR-{100000 + i}"
        name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        customers.append({
            'customer_id': c_id,
            'name': name,
            'age': np.random.randint(22, 65),
            'city': np.random.choice(cities),
            'product_type': np.random.choice(products),
            'annual_income': np.random.randint(400000, 5000000),
            'credit_score': np.random.randint(600, 850),
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
    for c_id in df_customers['customer_id']:
        income = df_customers[df_customers['customer_id'] == c_id]['annual_income'].values[0]
        monthly_salary = income / 12
        
        # Base credit date (1st of month)
        for m in range(12):
            date = datetime.now() - timedelta(days=30 * m)
            # Add some variability/drift (mostly 0-2 days, but some stressed)
            is_stressed = np.random.random() < 0.1
            delay = np.random.randint(0, 3) 
            if is_stressed:
                delay = np.random.randint(5, 15) # Risk Signal
            
            credit_date = datetime(date.year, date.month, 1) + timedelta(days=delay)
            salaries.append({
                'customer_id': c_id,
                'amount': round(monthly_salary * np.random.uniform(0.98, 1.02), 2),
                'credit_date': credit_date.strftime('%Y-%m-%d'),
                'delay_days': delay
            })
    
    pd.DataFrame(salaries).to_csv("salary_history.csv", index=False)
    print("✓ Created salary_history.csv")

    # 3. Payment History (Transactions)
    payments = []
    categories = ['Utility', 'Rent', 'EMI', 'Shopping', 'Food', 'Gambling', 'Lending App', 'Entertainment', 'Investment']
    
    # Generate ~50 transactions per customer
    for c_id in df_customers['customer_id']:
        num_tx = np.random.randint(30, 70)
        for _ in range(num_tx):
            cat = np.random.choice(categories, p=[0.15, 0.05, 0.1, 0.25, 0.2, 0.05, 0.05, 0.1, 0.05])
            amt = np.random.exponential(2000)
            if cat == 'Rent': amt = np.random.uniform(10000, 40000)
            if cat == 'EMI': amt = np.random.uniform(5000, 25000)
            if cat == 'Gambling' or cat == 'Lending App': amt = np.random.uniform(2000, 15000)
            
            date = datetime.now() - timedelta(days=np.random.randint(0, DAYS_OF_HISTORY))
            payments.append({
                'customer_id': c_id,
                'transaction_id': str(uuid.uuid4())[:8].upper(),
                'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'category': cat,
                'amount': round(amt, 2),
                'method': np.random.choice(['UPI', 'Debit Card', 'Net Banking', 'Auto-Debit'])
            })
            
    pd.DataFrame(payments).to_csv("payment_history.csv", index=False)
    print("✓ Created payment_history.csv")

    # 4. App Activity Logs
    activity = []
    actions = ['Login', 'Check Balance', 'Statement View', 'Loan Inquiry', 'Support Chat', 'Profile Update']
    
    for c_id in df_customers['customer_id']:
        # High risk customers might check balance more often or inquire about loans
        num_logs = np.random.randint(10, 100)
        for _ in range(num_logs):
            action = np.random.choice(actions)
            date = datetime.now() - timedelta(days=np.random.randint(0, DAYS_OF_HISTORY))
            hour = np.random.randint(0, 24)
            # Signal: High risk often logins late at night or checks balance repeatedly
            activity.append({
                'customer_id': c_id,
                'timestamp': date.replace(hour=hour).strftime('%Y-%m-%d %H:%M:%S'),
                'action': action,
                'session_duration_sec': np.random.randint(10, 600),
                'device': np.random.choice(['iOS', 'Android', 'Web'])
            })
            
    pd.DataFrame(activity).to_csv("app_activity.csv", index=False)
    print("✓ Created app_activity.csv")

    print("\nEnterprise Data Generation Complete.")

if __name__ == "__main__":
    generate_enterprise_dataset()
