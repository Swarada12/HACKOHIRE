"""
Train XGBoost, LightGBM, and LSTM using real customer data from the feature store.
Ensures model outputs vary per customer and are truly from the trained models.

Usage:
  cd backend && python train_from_db.py
  # Then restart BentoML: py -m bentoml serve service:BankRiskService --port 8000
"""
import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import xgboost as xgb
import lightgbm as lgb
import bentoml

# Add backend to path so we can import feature_store
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_store import FeatureStore

TABULAR_COLUMNS = [
    'salary_delay_days', 'savings_change_pct', 'credit_utilization',
    'failed_debits', 'lending_app_txns', 'gambling_amt'
]

def safe_num(val, default=0.0):
    try:
        if val is None: return default
        return float(val)
    except:
        return default

def build_row_from_features(f):
    """Build one row of X (6 cols) from feature-store dict. Matches ml_engine._prepare_features_for_tabular."""
    if f is None: f = {}
    monthly_salary = safe_num(f.get('f_monthly_salary') or f.get('monthly_salary'), 50000)
    distress_ratio = safe_num(f.get('distress_spend_ratio'))
    gambling_amt = distress_ratio * monthly_salary if monthly_salary else 0
    salary_delay = safe_num(f.get('t_current_salary_delay') or f.get('current_salary_delay_days'))
    savings_pct = safe_num(f.get('f_savings_change_pct') or f.get('savings_change_pct'))
    credit_util = safe_num(f.get('f_credit_utilization') or f.get('credit_utilization'))
    failed_debits = safe_num(f.get('t_auto_debit_fail_count') or f.get('failed_debits'))
    lending_txns = safe_num(f.get('b_loan_inquiry_count') or f.get('lending_app_txns'))
    return {
        'salary_delay_days': min(30, max(0, salary_delay)),
        'savings_change_pct': min(50, max(-80, savings_pct)),
        'credit_utilization': min(100, max(0, credit_util)),
        'failed_debits': min(20, max(0, failed_debits)),
        'lending_app_txns': min(50, max(0, lending_txns)),
        'gambling_amt': min(100000, max(0, gambling_amt)),
    }

def row_to_lstm_sequence(row):
    """Build (14, 1) sequence from one row. Same formula as ml_engine._features_to_lstm_sequence."""
    salary_delay = float(row.get('salary_delay_days', 0))
    savings_pct = float(row.get('savings_change_pct', 0))
    credit_util = float(row.get('credit_utilization', 0))
    failed_debits = float(row.get('failed_debits', 0))
    lending_txns = float(row.get('lending_app_txns', 0))
    gambling_amt = float(row.get('gambling_amt', 0))
    base = (
        (salary_delay / 15.0 - 0.5) * 0.35
        + (savings_pct / 100.0) * 0.25
        + (credit_util / 100.0 - 0.5) * 0.25
        + min(1.0, failed_debits / 5.0) * 0.1
        + min(1.0, lending_txns / 10.0) * 0.05
        + min(1.0, gambling_amt / 50000.0) * 0.1
    )
    seq = np.zeros((14, 1), dtype=np.float32)
    for i in range(14):
        seq[i, 0] = np.clip(base * (0.85 + 0.02 * i) + (i - 7) * 0.02, -2.0, 2.0)
    return seq

def load_training_data_from_db():
    """Load X (6 cols) and y (binary risk) from feature store + customers DB."""
    store = FeatureStore()
    conn = store.get_conn()
    try:
        df = pd.read_sql_query("SELECT customer_id, risk_score FROM customers", conn)
    finally:
        conn.close()
    if df.empty:
        print("No customers in DB. Run setup_db.py first.")
        return None, None, None

    rows = []
    targets = []
    for _, r in df.iterrows():
        cid = r['customer_id']
        risk_score = safe_num(r.get('risk_score'), 0)
        detailed = store.get_customer_detailed(cid)
        if not detailed:
            continue
        feats = detailed.get('features', {})
        core = detailed.get('core', {})
        row = build_row_from_features(feats)
        rows.append(row)
        # Binary target: risky if risk_score >= 45 (align with High/Critical)
        targets.append(1 if risk_score >= 45 else 0)

    X = pd.DataFrame(rows, columns=TABULAR_COLUMNS)
    y = np.array(targets, dtype=np.int64)
    print(f"Loaded {len(X)} customers from DB. Risk distribution: {np.bincount(y)}")
    return X, y, rows

def augment_synthetic_if_needed(X, y, min_samples=400):
    """If we have too few samples, add synthetic data with same schema and mixed labels."""
    if len(X) >= min_samples:
        return X, y
    n_add = min_samples - len(X)
    print(f"Augmenting with {n_add} synthetic samples...")
    np.random.seed(42)
    # Mix of safe (0) and risky (1)
    n_risk = n_add // 2
    n_safe = n_add - n_risk
    synthetic = []
    targets = []
    for _ in range(n_safe):
        synthetic.append({
            'salary_delay_days': np.random.exponential(0.5),
            'savings_change_pct': np.random.normal(10, 5),
            'credit_utilization': np.random.beta(2, 8) * 100,
            'failed_debits': np.random.poisson(0.05),
            'lending_app_txns': np.random.poisson(0.05),
            'gambling_amt': np.random.exponential(50),
        })
        targets.append(0)
    for _ in range(n_risk):
        synthetic.append({
            'salary_delay_days': np.random.gamma(4, 2),
            'savings_change_pct': np.random.normal(-20, 15),
            'credit_utilization': np.random.uniform(50, 98),
            'failed_debits': np.random.poisson(1),
            'lending_app_txns': np.random.poisson(0.5),
            'gambling_amt': np.random.exponential(5000),
        })
        targets.append(1)
    X_syn = pd.DataFrame(synthetic, columns=TABULAR_COLUMNS)
    y_syn = np.array(targets)
    X = pd.concat([X, X_syn], ignore_index=True)
    y = np.concatenate([y, y_syn])
    return X, y

class LSTMPredictor(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=32, output_dim=1):
        super(LSTMPredictor, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_step = lstm_out[:, -1, :]
        return self.sigmoid(self.fc(last_step))

def main():
    print("Loading training data from DB (feature store)...")
    X, y, rows = load_training_data_from_db()
    if X is None or len(X) == 0:
        return
    X, y = augment_synthetic_if_needed(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # ----- XGBoost -----
    print("Training XGBoost on", len(X_train), "samples...")
    xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, use_label_encoder=False, eval_metric='logloss')
    xgb_model.fit(X_train, y_train)
    yp = xgb_model.predict(X_test)
    print(f"XGBoost Test Accuracy: {accuracy_score(y_test, yp):.4f}, AUC: {roc_auc_score(y_test, xgb_model.predict_proba(X_test)[:, 1]):.4f}")
    bentoml.xgboost.save_model("bank_risk_xgb", xgb_model)
    print("Saved: bank_risk_xgb")

    # ----- LightGBM -----
    print("Training LightGBM...")
    lgb_model = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, num_leaves=31, objective='binary')
    lgb_model.fit(X_train, y_train)
    yp_lgb = lgb_model.predict(X_test)
    print(f"LightGBM Test Accuracy: {accuracy_score(y_test, yp_lgb):.4f}, AUC: {roc_auc_score(y_test, lgb_model.predict_proba(X_test)[:, 1]):.4f}")
    bentoml.lightgbm.save_model("bank_risk_lgbm", lgb_model)
    print("Saved: bank_risk_lgbm")

    # ----- LSTM (trained on sequences from same 6 features) -----
    print("Building LSTM sequences and training...")
    seqs_train = np.array([row_to_lstm_sequence(row) for row in X_train.to_dict('records')], dtype=np.float32)  # (N, 14, 1)
    seqs_test = np.array([row_to_lstm_sequence(row) for row in X_test.to_dict('records')], dtype=np.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    lstm_model = LSTMPredictor()
    opt = torch.optim.Adam(lstm_model.parameters(), lr=0.01)
    criterion = nn.BCELoss()
    dataset = torch.utils.data.TensorDataset(torch.from_numpy(seqs_train), y_train_t)
    loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
    lstm_model.train()
    for epoch in range(40):
        for batch_x, batch_y in loader:
            opt.zero_grad()
            out = lstm_model(batch_x)
            loss = criterion(out, batch_y)
            loss.backward()
            opt.step()
    lstm_model.eval()
    with torch.no_grad():
        pred = lstm_model(torch.from_numpy(seqs_test)).numpy().ravel()
    pred_bin = (pred >= 0.5).astype(int)
    print(f"LSTM Test Accuracy: {accuracy_score(y_test, pred_bin):.4f}, AUC: {roc_auc_score(y_test, pred):.4f}")

    traced = torch.jit.trace(lstm_model, torch.from_numpy(seqs_test[:1]))
    bentoml.torchscript.save_model("bank_pattern_lstm", traced, signatures={"__call__": {"batchable": True}})
    print("Saved: bank_pattern_lstm")

    print("Done. Restart BentoML server to use new models.")

if __name__ == "__main__":
    main()
