import sys
import os
# Add current directory to path to import backend
sys.path.append(os.getcwd())

from backend.ml_engine import MLRiskEngine
from backend.feature_store import FeatureStore
import pandas as pd
import torch
import torch.nn as nn

# Define LSTMPredictor for the environment
class LSTMPredictor(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=32, output_dim=1):
        super(LSTMPredictor, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_step = lstm_out[:, -1, :]
        out = self.fc(last_step)
        return self.sigmoid(out)

def count_critical_ai():
    print("Initializing AI/ML Engine...")
    engine = MLRiskEngine()
    store = FeatureStore()
    
    if not engine.initialized:
        print("Error: AI Engine failed to initialize models.")
        return

    print("Fetching all customers from database...")
    conn = store.get_conn()
    cids = pd.read_sql_query("SELECT customer_id FROM customers", conn)['customer_id'].tolist()
    conn.close()
    
    total = len(cids)
    print(f"Total customers to evaluate: {total}")
    
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    print("Evaluating...")
    for i, cid in enumerate(cids):
        detailed = store.get_customer_detailed(cid)
        if not detailed: continue
        
        result = engine.predict_ensemble(detailed['features'])
        score = result['fusion_score']
        
        if score >= 85:
            critical_count += 1
        elif score >= 45:
            high_count += 1
        elif score >= 30:
            medium_count += 1
        else:
            low_count += 1
            
        if (i+1) % 50 == 0:
            print(f"  Processed {i+1}/{total}...")

    print("\n--- AI Engine Evaluation Summary ---")
    print(f"Total Evaluated: {total}")
    print(f"Critical Users: {critical_count}")
    print(f"High Risk Users: {high_count}")
    print(f"Medium Risk Users: {medium_count}")
    print(f"Low Risk Users: {low_count}")
    print("------------------------------------")

if __name__ == "__main__":
    count_critical_ai()
