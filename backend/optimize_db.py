import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'bank_risk.db')
if 'backend' not in os.getcwd():
    DB_PATH = os.path.join(os.getcwd(), 'backend', 'bank_risk.db')

def optimize_database():
    print(f"Optimizing database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Transactions Indices
    print("Creating indices for transactions...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_cust ON transactions(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_cat ON transactions(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_type ON transactions(transaction_type)")
        print("✓ Transaction indices created.")
    except Exception as e:
        print(f"Error creating transaction indices: {e}")

    # 2. Customers Index
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cust_id ON customers(customer_id)")
        print("✓ Customer indices created.")
    except Exception as e:
        print(f"Error creating customer indices: {e}")

    conn.commit()
    conn.close()
    print("Optimization Complete!")

if __name__ == "__main__":
    optimize_database()
