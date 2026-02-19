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
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
import xgboost as xgb
import lightgbm as lgb
import bentoml

# Add backend to path so we can import feature_store
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_store import FeatureStore
from ml_engine import LSTMPredictor

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
    """Load X (6 cols) and y (binary risk) from feature store + customers DB using optimized BULK QUERY."""
    store = FeatureStore()
    conn = store.get_conn()
    try:
        # Optimized Bulk Query: Joins customers with signals to avoid N+1 problem
        # We need to aggregate transactions/utility/salary to get the features
        query = """
        SELECT 
            c.customer_id, 
            c.risk_score,
            c.monthly_salary,
            c.current_salary_delay_days, 
            c.savings_change_pct, 
            c.credit_utilization,
            COALESCE(t_stats.failed_debits, 0) as failed_debits_count,
            COALESCE(t_stats.lending_txns, 0) as lending_app_txns,
            COALESCE(t_stats.gambling_amt, 0) as gambling_amt
        FROM customers c
        LEFT JOIN (
            SELECT 
                customer_id,
                SUM(CASE WHEN transaction_type='EMI_BOUNCE' THEN 1 ELSE 0 END) as failed_debits,
                SUM(CASE WHEN category='Lending App' THEN 1 ELSE 0 END) as lending_txns,
                SUM(CASE WHEN category='Gambling' THEN amount ELSE 0 END) as gambling_amt
            FROM transactions 
            GROUP BY customer_id
        ) t_stats ON c.customer_id = t_stats.customer_id
        """
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    if df.empty:
        print("No customers in DB. Run setup_db.py first.")
        return None, None, None

    rows = []
    targets = []
    rng = np.random.default_rng(42)
    
    # Vectorized / Bulk processing
    # Handle NULLs
    df['gambling_amt'] = df['gambling_amt'].fillna(0)
    df['monthly_salary'] = df['monthly_salary'].fillna(50000)
    
    total_rows = len(df)
    for i, (_, r) in enumerate(df.iterrows()):
        if i % 100 == 0:
            print(f"Processing Customer Data: {i}/{total_rows}", end='\r')

        # Feature Mapping matches ml_engine logic
        # 'salary_delay_days', 'savings_change_pct', 'credit_utilization', 'failed_debits', 'lending_app_txns', 'gambling_amt'
        
        row = {
            'salary_delay_days': min(30, max(0, float(r['current_salary_delay_days'] or 0))),
            'savings_change_pct': min(50, max(-80, float(r['savings_change_pct'] or 0))),
            'credit_utilization': min(100, max(0, float(r['credit_utilization'] or 0))),
            'failed_debits': min(20, max(0, float(r['failed_debits_count'] or 0))),
            'lending_app_txns': min(50, max(0, float(r['lending_app_txns'] or 0))),
            'gambling_amt': min(100000, max(0, float(r['gambling_amt'] or 0))),
        }
        
        rows.append(row)
        # --- ENTERPRISE-REALISTIC LABELING (NO TARGET LEAKAGE) ---
        # Treat risk_score as proxy probability-of-default (PD), then sample label.
        rs = float(r['risk_score'] or 0)
        pd_prob = min(0.99, max(0.01, rs / 100.0))
        targets.append(1 if rng.random() < pd_prob else 0)
    
    print(f"Processing Customer Data: {total_rows}/{total_rows} - Complete!      ")

    X = pd.DataFrame(rows, columns=TABULAR_COLUMNS)
    y = np.array(targets, dtype=np.int64)
    print(f"Loaded {len(X)} customers from DB (Optimized). Risk distribution: {np.bincount(y)}")
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



def main():
    print("Loading training data from DB (feature store)...")
    X, y, rows = load_training_data_from_db()
    if X is None or len(X) == 0:
        return
    X, y = augment_synthetic_if_needed(X, y)
    # Split: train / calibration / test
    X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_cal, y_train, y_cal = train_test_split(X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full)

    # ----- XGBoost -----
    print("Training XGBoost on", len(X_train), "samples...")
    xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, use_label_encoder=False, eval_metric='logloss')
    xgb_model.fit(X_train, y_train)
    # Calibrate probabilities (banking PD requirement)
    xgb_cal = CalibratedClassifierCV(xgb_model, method="sigmoid", cv="prefit")
    xgb_cal.fit(X_cal, y_cal)
    xgb_p = xgb_cal.predict_proba(X_test)[:, 1]
    yp = (xgb_p >= 0.5).astype(int)
    print(f"XGBoost(cal) Test Accuracy: {accuracy_score(y_test, yp):.4f}, AUC: {roc_auc_score(y_test, xgb_p):.4f}")
    bentoml.xgboost.save_model("bank_risk_xgb", xgb_model)
    bentoml.sklearn.save_model("bank_risk_xgb_cal", xgb_cal)
    print("Saved: bank_risk_xgb")
    print("Saved: bank_risk_xgb_cal")

    # ----- LightGBM -----
    print("Training LightGBM...")
    lgb_model = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, num_leaves=31, objective='binary')
    lgb_model.fit(X_train, y_train)
    lgb_cal = CalibratedClassifierCV(lgb_model, method="sigmoid", cv="prefit")
    lgb_cal.fit(X_cal, y_cal)
    lgb_p = lgb_cal.predict_proba(X_test)[:, 1]
    yp_lgb = (lgb_p >= 0.5).astype(int)
    print(f"LightGBM(cal) Test Accuracy: {accuracy_score(y_test, yp_lgb):.4f}, AUC: {roc_auc_score(y_test, lgb_p):.4f}")
    bentoml.lightgbm.save_model("bank_risk_lgbm", lgb_model)
    bentoml.sklearn.save_model("bank_risk_lgbm_cal", lgb_cal)
    print("Saved: bank_risk_lgbm")
    print("Saved: bank_risk_lgbm_cal")

    # ----- LSTM (trained on sequences from same 6 features) -----
    print("Building LSTM sequences and training...")
    seqs_train = np.array([row_to_lstm_sequence(row) for row in X_train.to_dict('records')], dtype=np.float32)  # (N, 14, 1)
    seqs_cal = np.array([row_to_lstm_sequence(row) for row in X_cal.to_dict('records')], dtype=np.float32)
    seqs_test = np.array([row_to_lstm_sequence(row) for row in X_test.to_dict('records')], dtype=np.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    y_cal_t = torch.tensor(y_cal, dtype=torch.float32).unsqueeze(1)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    lstm_model = LSTMPredictor()
    opt = torch.optim.Adam(lstm_model.parameters(), lr=0.01)
    criterion = nn.BCELoss()
    dataset = torch.utils.data.TensorDataset(torch.from_numpy(seqs_train), y_train_t)
    loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
    lstm_model.train()
    for epoch in range(8):
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

    # Save LSTM as generic picklable model (works better for custom classes than deprecated bentoml.pytorch)
    bentoml.picklable_model.save_model("bank_pattern_lstm", lstm_model)
    print("Saved: bank_pattern_lstm (picklable_model)")

    # ----- Fusion model (stacking) -----
    print("Training fusion (stacked logistic regression) on calibrated agent outputs...")
    # Train on calibration split outputs to avoid leakage
    xgb_cal_p = xgb_cal.predict_proba(X_cal)[:, 1]
    lgb_cal_p = lgb_cal.predict_proba(X_cal)[:, 1]
    with torch.no_grad():
        lstm_cal_p = lstm_model(torch.from_numpy(seqs_cal)).numpy().ravel()
        lstm_test_p = lstm_model(torch.from_numpy(seqs_test)).numpy().ravel()

    Z_cal = np.column_stack([xgb_cal_p, lgb_cal_p, lstm_cal_p])
    fusion = LogisticRegression(max_iter=200)
    fusion.fit(Z_cal, y_cal)

    xgb_test_p = xgb_cal.predict_proba(X_test)[:, 1]
    lgb_test_p = lgb_cal.predict_proba(X_test)[:, 1]
    Z_test = np.column_stack([xgb_test_p, lgb_test_p, lstm_test_p])
    fusion_p = fusion.predict_proba(Z_test)[:, 1]
    fusion_bin = (fusion_p >= 0.5).astype(int)
    print(f"Fusion Test Accuracy: {accuracy_score(y_test, fusion_bin):.4f}, AUC: {roc_auc_score(y_test, fusion_p):.4f}")
    bentoml.sklearn.save_model("bank_risk_fusion", fusion)
    print("Saved: bank_risk_fusion")

    print("Done. Restart BentoML server to use new models.")

if __name__ == "__main__":
    main()
