import bentoml
import numpy as np
import pandas as pd
import torch

def verify_models():
    print("Verifying trained models...")
    
    # 1. XGBoost
    try:
        print("Loading XGBoost...")
        xgb_model = bentoml.xgboost.load_model("bank_risk_xgb:latest")
        # Dummy input (6 features)
        X = pd.DataFrame([
            [5, -10, 80, 0, 0, 0],
            [20, -50, 95, 2, 5, 1000]
        ], columns=['salary_delay_days', 'savings_change_pct', 'credit_utilization',
                    'failed_debits', 'lending_app_txns', 'gambling_amt'])
        preds = xgb_model.predict_proba(X)
        print(f"XGBoost Predictions (Success): {preds[:, 1]}")
    except Exception as e:
        print(f"XGBoost Failed: {e}")

    # 2. LightGBM
    try:
        print("Loading LightGBM...")
        lgb_model = bentoml.lightgbm.load_model("bank_risk_lgbm:latest")
        preds = lgb_model.predict(X)
        print(f"LightGBM Predictions (Success): {preds}")
    except Exception as e:
        print(f"LightGBM Failed: {e}")

    # 3. LSTM
    try:
        print("Loading LSTM...")
        lstm_model = bentoml.torchscript.load_model("bank_pattern_lstm:latest")
        # Dummy sequence (Batch=2, Seq=14, Feat=1)
        seq = torch.randn(2, 14, 1)
        out = lstm_model(seq)
        print(f"LSTM Predictions (Success): {out.detach().numpy().ravel()}")
    except Exception as e:
        print(f"LSTM Failed: {e}")

if __name__ == "__main__":
    verify_models()
