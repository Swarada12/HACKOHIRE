import sqlite3
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.getcwd(), 'bank_risk.db')
if 'backend' not in os.getcwd():
    DB_PATH = os.path.join(os.getcwd(), 'backend', 'bank_risk.db')

def setup_database():
    print(f"Initializing SQLite Database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Customers Core Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            product_type TEXT,
            annual_income REAL,
            monthly_salary REAL,
            credit_score INTEGER,
            credit_utilization REAL,
            savings_change_pct REAL,
            current_salary_delay_days INTEGER,
            loan_amount REAL,
            monthly_emi REAL,
            risk_score INTEGER,
            risk_level TEXT,
            suggested_action TEXT,
            ability_score INTEGER,
            willingness_score INTEGER,
            rare_case_type TEXT
        )
    ''')

    # 2. Transactions Table (for Signals 2, 4, 5, 8)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            timestamp DATETIME,
            amount REAL,
            category TEXT,
            merchant TEXT,
            transaction_type TEXT, -- 'DEBIT', 'CREDIT', 'TRANSFER', 'EMI_BOUNCE'
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')

    # 3. Salary History (for Signal 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            month_year TEXT,
            amount REAL,
            delay_days INTEGER,
            employer TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')

    # 4. App Activity (for Signals 5, 9)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            timestamp DATETIME,
            action TEXT, -- 'Login', 'Balance Check', 'EMI View', 'Loan Inquiry'
            device TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')

    conn.commit()
    return conn

def seed_data(conn):
    print("Seeding 300 high-fidelity customers...")
    cursor = conn.cursor()
    
    first_names = ['Aarav', 'Advait', 'Vihaan', 'Arjun', 'Ananya', 'Ishaan', 'Sai', 'Aadhya', 'Vivaan', 'Zara', 'Kabir', 'Riya', 'Aaryan', 'Diya', 'Reyansh', 'Myra', 'Siddharth', 'Avani', 'Karthik', 'Sneha', 'Manish', 'Pooja', 'Rohan', 'Sanya', 'Vikram', 'Neha', 'Rahul', 'Shreya', 'Amit', 'Sunita']
    last_names = ['Sharma', 'Verma', 'Gupta', 'Malhotra', 'Kapoor', 'Khan', 'Patel', 'Reddy', 'Iyer', 'Nair', 'Singhania', 'Chauhan', 'Deshmukh', 'Joshi', 'Aggarwal', 'Bose', 'Das', 'Mehta', 'Basu', 'Rao', 'Kulkarni', 'Pandey', 'Mishra', 'Yadav', 'Dubey']
    
    cities = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Pune']
    products = ['Personal Loan', 'Home Loan', 'Auto Loan', 'Credit Card']
    
    customers = []
    for i in range(100001, 100301):
        cid = f"CUSR-{i}"
        # Seed based on i to ensure the same customer ID always gets the same name across runs
        np.random.seed(i)
        name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        
        # Reset seed for general data generation consistency
        np.random.seed(i)
        city = np.random.choice(cities)
        prod = np.random.choice(products)
        income = np.random.randint(500000, 2500000)
        salary = income / 12
        credit = np.random.randint(400, 850)
        util = np.random.uniform(10, 95)
        savings_change = np.random.uniform(-50, 20)
        delay = np.random.randint(0, 25)
        loan_amt = np.random.randint(100000, 2000000)
        emi = loan_amt / np.random.choice([12, 24, 36, 60])
        
        # Initial score for seed
        score = int(round(15 + (delay * 2) + (util * 0.3)))
        lvl = 'Critical' if score >= 85 else 'High' if score >= 45 else 'Medium' if score >= 30 else 'Low'
        
        # Strategic Decision Indices (Persistence)
        ability = np.random.randint(20, 95)
        willingness = np.random.randint(30, 98)
        
        # Profile-specific overrides
        if score > 70:
            ability = np.random.randint(15, 50) 
            if np.random.random() > 0.5:
                ability = np.random.randint(60, 90)
                willingness = np.random.randint(10, 40)
        
        rare_type = "Normal"
        if ability < 40 and willingness > 70: rare_type = "Victim of Circumstance"
        elif ability > 60 and willingness < 40: rare_type = "Strategic Defaulter"

        # Suggested Action Logic (Duplicate from FeatureStore for seeding)
        action = "Standard Monitoring"
        if delay > 20: action = f"🚨 CRITICAL: Send Legal Notice to {name}"
        elif delay > 7: action = f"📞 Call {name}: Offer Salary Advance"
        elif util > 80: action = f"🔒 Freeze Card Limit ({int(util)}%)"

        customers.append((cid, name, city, prod, income, salary, credit, util, savings_change, delay, loan_amt, emi, score, lvl, action, ability, willingness, rare_type))

    cursor.executemany('''
        INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', customers)

    # Seed related data for a few key customers to show complex signals
    # We'll generate transactions, salary history etc for all, but more "stressful" for high risk ones
    
    print("Generating temporal signals (Salary, Transactions, Activity)...")
    
    all_transactions = []
    all_salaries = []
    all_activity = []
    
    for cid, name, city, prod, income, salary, credit, util, savings_change, delay, loan_amt, emi, score, lvl, action, ability, willingness, rare_type in customers:
        # Salary History (Last 6 months)
        for m in range(1, 7):
            m_delay = delay if m == 1 else np.random.randint(0, 5)
            # Signal 1: Salary reduction or delay
            m_amt = salary if m > 1 else salary * (0.85 if score > 70 else 1.0)
            all_salaries.append((cid, f"2025-{m:02d}", m_amt, m_delay, "Tech Corp"))
            
        # Transactions (Last 30 days)
        for d in range(1, 31):
            date = datetime.now() - timedelta(days=d)
            # Regular spends
            all_transactions.append((cid, date, np.random.randint(500, 5000), 'Grocery', 'Store', 'DEBIT'))
            
            # Distress Signals
            if score > 60:
                if np.random.random() > 0.8:
                    all_transactions.append((cid, date, np.random.randint(1000, 10000), 'Gambling', 'WinBet', 'DEBIT'))
                if np.random.random() > 0.9:
                    all_transactions.append((cid, date, 5000, 'Lending App', 'QuickCash', 'DEBIT'))
            
            # EMI Payment
            if d == 15:
                all_transactions.append((cid, date, emi, 'EMI', 'Bank', 'DEBIT'))
        
        # Activity
        for _ in range(np.random.randint(5, 50)):
            ts = datetime.now() - timedelta(minutes=np.random.randint(1, 43200))
            action = np.random.choice(['Login', 'Balance Check', 'EMI View', 'Loan Inquiry'], p=[0.5, 0.3, 0.1, 0.1])
            # Signal 9: Late night logins
            if score > 75 and np.random.random() > 0.7:
                ts = ts.replace(hour=np.random.randint(1, 4))
            all_activity.append((cid, ts, action, 'Android'))

    cursor.executemany('INSERT INTO transactions (customer_id, timestamp, amount, category, merchant, transaction_type) VALUES (?,?,?,?,?,?)', all_transactions)
    cursor.executemany('INSERT INTO salary_history (customer_id, month_year, amount, delay_days, employer) VALUES (?,?,?,?,?)', all_salaries)
    cursor.executemany('INSERT INTO app_activity (customer_id, timestamp, action, device) VALUES (?,?,?,?)', all_activity)

    conn.commit()
    print("Database seeding complete!")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    connection = setup_database()
    seed_data(connection)
    connection.close()
