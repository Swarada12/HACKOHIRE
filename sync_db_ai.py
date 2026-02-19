import sys
import os
import sqlite3
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

def sync_database_with_ai():
    print("🚀 STARTING SYSTEM-WIDE AI SYNC...")
    engine = MLRiskEngine()
    store = FeatureStore()
    
    if not engine.initialized:
        print("❌ Error: AI Engine failed to initialize models.")
        return

    conn = store.get_conn()
    cursor = conn.cursor()
    
    # Fetch all customers
    print("📡 Fetching customers from Enterprise DB...")
    customers_df = pd.read_sql_query("SELECT customer_id FROM customers", conn)
    cids = customers_df['customer_id'].tolist()
    total = len(cids)
    print(f"📊 Found {total} customers to sync.")
    
    print("🧠 Propagating Real AI Scores to Database...")
    
    for i, cid in enumerate(cids):
        # 1. Get real features
        detailed = store.get_customer_detailed(cid)
        if not detailed: continue
        
        # 2. Run Ensemble Inference
        result = engine.predict_ensemble(detailed['features'])
        score = int(result['fusion_score'])
        
        # 3. Classify Level
        level = "Critical" if score >= 85 else "High" if score >= 45 else "Medium" if score >= 30 else "Low"
        
        # 4. Update Database
        cursor.execute("""
            UPDATE customers 
            SET risk_score = ?, risk_level = ? 
            WHERE customer_id = ?
        """, (score, level, cid))
        
        if (i+1) % 50 == 0:
            print(f"  ✅ Synced {i+1}/{total} profiles...")

    conn.commit()
    print("\n🎉 SYNC COMPLETE!")
    
    # Print new distribution from DB
    print("\n--- New Database Risk Distribution ---")
    dist = pd.read_sql_query("SELECT risk_level, COUNT(*) as count FROM customers GROUP BY risk_level", conn)
    print(dist)
    print("---------------------------------------")
    
    conn.close()

if __name__ == "__main__":
    sync_database_with_ai()
