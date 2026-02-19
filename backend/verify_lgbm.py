"""Verify LightGBM fix: full ensemble scores for sample customers."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from feature_store import FeatureStore
from ml_engine import MLRiskEngine

fs = FeatureStore()
eng = MLRiskEngine()

# Test a few customers
test_ids = ['CUSR-100001', 'CUSR-100002', 'CUSR-100080', 'CUSR-100005']
for cid in test_ids:
    d = fs.get_customer_detailed(cid)
    if not d: continue
    f = d['features']
    ml = eng.predict_ensemble(f, customer_id=cid)
    a = ml['agent_scores']
    print(f"{f.get('name','?')} ({cid}): Fusion={ml['fusion_score']} | XGB={a['xgboost_risk']} LGB={a['lightgbm_risk']} LSTM={a['lstm_pattern']}")
