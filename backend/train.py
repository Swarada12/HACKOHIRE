import pandas as pd
import numpy as np
import xgboost as xgb
import bentoml
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

print("Generating synthetic banking data...")

# ==========================================
# 1. Generate Synthetic Customer Risk Data
# ==========================================
# Features: Salary Delay, Savings Change %, Credit Util, Failed Debits, Lending App Txns, Gambling Amt
def generate_risk_data(n=5000):
    np.random.seed(42)
    
    # Safe customers (80%)
    n_safe = int(n * 0.80)
    safe = pd.DataFrame({
        'salary_delay_days': np.random.exponential(0.5, n_safe), 
        'savings_change_pct': np.random.normal(10, 5, n_safe), 
        'credit_utilization': np.random.beta(2, 8, n_safe) * 100,
        'failed_debits': np.random.poisson(0.05, n_safe),
        'lending_app_txns': np.random.poisson(0.05, n_safe),
        'gambling_amt': np.random.exponential(50, n_safe),
        'target': 0
    })
    
    # Risky customers (20%) - Divided into 4 Personas
    n_risky = n - n_safe
    n_per = n_risky // 4
    
    # Persona 1: Liquidity Crunch (Salary Delay focus)
    p1 = pd.DataFrame({
        'salary_delay_days': np.random.gamma(8, 2, n_per), # High delay
        'savings_change_pct': np.random.normal(-5, 5, n_per),
        'credit_utilization': np.random.beta(2, 5, n_per) * 100,
        'failed_debits': np.random.poisson(0.2, n_per),
        'lending_app_txns': np.random.poisson(0.1, n_per),
        'gambling_amt': np.random.exponential(100, n_per),
        'target': 1
    })
    
    # Persona 2: Over-Leverage (Credit Util focus)
    p2 = pd.DataFrame({
        'salary_delay_days': np.random.exponential(1, n_per),
        'savings_change_pct': np.random.normal(-10, 10, n_per),
        'credit_utilization': np.random.uniform(85, 98, n_per), # Maxed out
        'failed_debits': np.random.poisson(0.5, n_per),
        'lending_app_txns': np.random.poisson(0.5, n_per),
        'gambling_amt': np.random.exponential(200, n_per),
        'target': 1
    })
    
    # Persona 3: Behavioral Drift (Gambling/Apps focus)
    p3 = pd.DataFrame({
        'salary_delay_days': np.random.exponential(1, n_per),
        'savings_change_pct': np.random.normal(-5, 10, n_per),
        'credit_utilization': np.random.beta(3, 3, n_per) * 100,
        'failed_debits': np.random.poisson(0.2, n_per),
        'lending_app_txns': np.random.poisson(5, n_per), # High loan apps
        'gambling_amt': np.random.uniform(10000, 50000, n_per), # High gambling
        'target': 1
    })
    
    # Persona 4: Cash Flow Failure (Bounces/Savings drop)
    p4 = pd.DataFrame({
        'salary_delay_days': np.random.exponential(1, n_per),
        'savings_change_pct': np.random.normal(-45, 15, n_per), # Massive dump
        'credit_utilization': np.random.beta(4, 4, n_per) * 100,
        'failed_debits': np.random.poisson(4, n_per), # Continuous bounces
        'lending_app_txns': np.random.poisson(1, n_per),
        'gambling_amt': np.random.exponential(100, n_per),
        'target': 1
    })
    
    df = pd.concat([safe, p1, p2, p3, p4]).sample(frac=1).reset_index(drop=True)
    return df

df = generate_risk_data()
X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training XGBoost on {len(X_train)} samples...")

# Train XGBoost
import lightgbm as lgb

# ... XGBoost training ...
model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

# Evaluates XGBoost
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred)
print(f"XGBoost Test Accuracy: {acc:.4f}, AUC: {auc:.4f}")

# Save XGBoost to BentoML
print("Saving XGBoost model to BentoML model store...")
bentoml.xgboost.save_model("bank_risk_xgb", model)
print("Saved: bank_risk_xgb")

# ==========================================
# 1.5 Train LightGBM Model
# ==========================================
print(f"Training LightGBM on {len(X_train)} samples...")
lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    learning_rate=0.1,
    num_leaves=31,
    objective='binary'
)
lgb_model.fit(X_train, y_train)

# Evaluate LightGBM
y_pred_lgb = lgb_model.predict(X_test)
acc_lgb = accuracy_score(y_test, y_pred_lgb)
auc_lgb = roc_auc_score(y_test, y_pred_lgb)
print(f"LightGBM Test Accuracy: {acc_lgb:.4f}, AUC: {auc_lgb:.4f}")

# Save LightGBM to BentoML
print("Saving LightGBM model to BentoML model store...")
bentoml.lightgbm.save_model("bank_risk_lgbm", lgb_model)
print("Saved: bank_risk_lgbm")


# ==========================================
# 2. Train LSTM Pattern Model (PyTorch)
# ==========================================
# Task: Detect anomaly in 14-day transaction sequence (e.g. sudden drop)

# Simple LSTM Model
class LSTMPredictor(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=32, output_dim=1):
        super(LSTMPredictor, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        lstm_out, _ = self.lstm(x)
        # Take last time step
        last_step = lstm_out[:, -1, :]
        out = self.fc(last_step)
        return self.sigmoid(out)

# Mock training for simplicity
pattern_model = LSTMPredictor()
pattern_model.eval()

# Create a sample input for tracing
dummy_input = torch.randn(1, 14, 1)

# Use TorchScript for better portability in BentoML
traced_model = torch.jit.trace(pattern_model, dummy_input)

print("Saving LSTM (TorchScript) model to BentoML...")
bentoml.torchscript.save_model(
    "bank_pattern_lstm",
    traced_model,
    signatures={"__call__": {"batchable": True}}
)
print("Saved: bank_pattern_lstm")

print("Done! Models ready for serving.")
