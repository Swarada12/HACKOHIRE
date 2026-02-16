import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_realtime_data(num_records=10000):
    print(f"Generating {num_records} records of realistic banking data...")
    
    # 1. Generate Customer Base
    customer_ids = [f"CUST-{1000+i}" for i in range(num_records)]
    
    # Names
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Diya", "Saanvi", "Ananya", "Aadhya", "Kiara", "Pari", "Riya", "Anvi", "Myra", "Sarah"]
    last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Bhatia", "Mehta", "Jain", "Saxena", "Agarwal", "Singh", "Patel", "Reddy", "Nair", "Rao", "Kumar"]
    names = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(num_records)]
    
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
    product_types = ["Home Loan", "Personal Loan", "Credit Card", "Auto Loan", "Education Loan"]
    
    # IDs
    aadhar_base = np.random.randint(1000, 9999, size=(num_records, 3))
    aadhars = [f"{r[0]}-{r[1]}-{r[2]}" for r in aadhar_base]
    
    pan_chars = "ABCDE"
    pan_nums = np.random.randint(1000, 9999, size=num_records)
    pans = [f"{random.choice(pan_chars)}{random.choice(pan_chars)}{random.choice(pan_chars)}P{random.choice(pan_chars)}{n}A" for n in pan_nums]
    
    # 2. Financial Metrics (Realistic Distributions)
    
    # Monthly Salary: Log-normal distribution (most earn 30k-80k, some earn 200k+)
    salaries = np.random.lognormal(mean=10.8, sigma=0.6, size=num_records).astype(int)
    salaries = np.clip(salaries, 15000, 500000)
    
    # Loan Amounts: Correlated with salary
    loan_amounts = (salaries * np.random.uniform(5, 20, size=num_records)).astype(int)
    
    # Risk Indicators
    # Skewed so most are safe
    salary_delays = np.random.choice([0, 1, 2, 5, 10, 20], size=num_records, p=[0.7, 0.15, 0.08, 0.04, 0.02, 0.01])
    savings_changes = np.random.normal(5, 15, size=num_records) # Avg +5% growth
    credit_utils = np.random.beta(2, 5, size=num_records) * 100
    
    # Timestamp (Simulating stream over last 30 days for trends)
    base_time = datetime.now()
    timestamps = [base_time - timedelta(minutes=random.randint(0, 43200)) for _ in range(num_records)]
    timestamps.sort()
    
    # Create DataFrame
    df = pd.DataFrame({
        "timestamp": timestamps,
        "customer_id": customer_ids,
        "name": names,
        "aadhar_no": aadhars,
        "pan_no": pans,
        "city": [random.choice(cities) for _ in range(num_records)],
        "product_type": [random.choice(product_types) for _ in range(num_records)],
        "monthly_salary": salaries,
        "loan_amount": loan_amounts,
        "current_salary_delay_days": salary_delays,
        "savings_change_pct": np.round(savings_changes, 2),
        "credit_utilization": np.round(credit_utils, 2),
        "transaction_type": np.random.choice(["CREDIT", "DEBIT", "TRANSFER", "KyC_UPDATE", "LOAN_EMI"], size=num_records),
        "amount": np.where(np.random.random(size=num_records) > 0.5, 
                           np.random.randint(100, 50000, size=num_records), 
                           np.random.randint(100, 2000, size=num_records))
    })
    
    # Save to CSV
    filename = "realtime_banking_data.csv"
    df.to_csv(filename, index=False)
    print(f"Successfully saved {filename}")
    return df

if __name__ == "__main__":
    generate_realtime_data()
