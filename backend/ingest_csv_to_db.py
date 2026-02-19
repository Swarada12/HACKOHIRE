import sqlite3
import pandas as pd
import os
import shutil

DB_PATH = os.path.join(os.getcwd(), 'bank_risk.db')
if 'backend' not in os.getcwd():
    DB_PATH = os.path.join(os.getcwd(), 'backend', 'bank_risk.db')

def setup_tables(conn):
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
    # 2. Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            timestamp DATETIME,
            amount REAL,
            category TEXT,
            merchant TEXT,
            transaction_type TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    # 3. Salary History
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
    # 4. App Activity
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            timestamp DATETIME,
            action TEXT,
            device TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    # 5. Utility Payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utility_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            bill_date DATETIME,
            payment_date DATETIME,
            amount REAL,
            category TEXT,
            days_past_due INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    conn.commit()

def ingest_data():
    if os.path.exists(DB_PATH):
        print(f"Removing existing DB at {DB_PATH}")
        os.remove(DB_PATH)
    
    print(f"Creating new DB at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    setup_tables(conn)
    cursor = conn.cursor()

    print("Ingesting Customers...")
    df_c = pd.read_csv("customers_core.csv")
    # Mapping columns to DB schema
    # DB columns: customer_id, name, city, product_type, annual_income, monthly_salary, credit_score, credit_utilization, savings_change_pct, current_salary_delay_days, loan_amount, monthly_emi, risk_score, risk_level, suggested_action, ability_score, willingness_score, rare_case_type
    
    customers_data = []
    for _, row in df_c.iterrows():
        customers_data.append((
            row['customer_id'], row['name'], row['city'], row['product_type'], 
            row['annual_income'], row['monthly_salary'], row['credit_score'], 
            row['credit_utilization'], row['savings_change_pct'], row['current_salary_delay_days'],
            row['loan_amount'], row['monthly_emi'], row['risk_score'], row['risk_level'],
            row['suggested_action'], row['ability_score'], row['willingness_score'], row['rare_case_type']
        ))
    
    cursor.executemany('''
        INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', customers_data)
    
    print("Ingesting Salary History...")
    df_s = pd.read_csv("salary_history.csv")
    salary_data = []
    for _, row in df_s.iterrows():
        salary_data.append((row['customer_id'], row['month_year'], row['amount'], row['delay_days'], row['employer']))
    cursor.executemany('INSERT INTO salary_history (customer_id, month_year, amount, delay_days, employer) VALUES (?,?,?,?,?)', salary_data)
    
    print("Ingesting Payment History (Transactions)...")
    df_p = pd.read_csv("payment_history.csv")
    pay_data = []
    for _, row in df_p.iterrows():
        pay_data.append((row['customer_id'], row['timestamp'], row['amount'], row['category'], row['merchant'], row['transaction_type']))
    cursor.executemany('INSERT INTO transactions (customer_id, timestamp, amount, category, merchant, transaction_type) VALUES (?,?,?,?,?,?)', pay_data)

    print("Ingesting App Activity...")
    df_a = pd.read_csv("app_activity.csv")
    act_data = []
    for _, row in df_a.iterrows():
        act_data.append((row['customer_id'], row['timestamp'], row['action'], row['device']))
    cursor.executemany('INSERT INTO app_activity (customer_id, timestamp, action, device) VALUES (?,?,?,?)', act_data)

    print("Ingesting Utility Payments...")
    if os.path.exists("utility_payments.csv"):
        df_u = pd.read_csv("utility_payments.csv")
        util_data = []
        for _, row in df_u.iterrows():
            util_data.append((row['customer_id'], row['bill_date'], row['payment_date'], row['amount'], row['category'], row['days_past_due']))
        cursor.executemany('INSERT INTO utility_payments (customer_id, bill_date, payment_date, amount, category, days_past_due) VALUES (?,?,?,?,?,?)', util_data)

    conn.commit()
    conn.close()
    print("Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()
