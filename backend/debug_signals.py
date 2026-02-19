"""Quick debug: check what signals the ML model produces for High-risk customers."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from feature_store import FeatureStore
from ml_engine import MLRiskEngine
import sqlite3

fs = FeatureStore()
eng = MLRiskEngine()

conn = sqlite3.connect('bank_risk.db')
c = conn.cursor()
c.execute("""SELECT customer_id, name, risk_score, current_salary_delay_days, 
             credit_utilization, savings_change_pct 
             FROM customers WHERE risk_level='High' LIMIT 8""")
rows = c.fetchall()
conn.close()

for cid, name, score, delay, util, savings in rows:
    d = fs.get_customer_detailed(cid)
    if not d:
        print(f"  {name}: NO DETAILED DATA")
        continue
    features = d['features']
    ml = eng.predict_ensemble(features, customer_id=cid)
    reasoning = ml.get('agent_reasoning', {})
    
    # Same filter as service.py
    sigs = []
    for domain, reasons in reasoning.items():
        for r in reasons:
            if ("Flag" in r or "Insight" in r) and "stable" not in r.lower() and "normal range" not in r.lower() and "acceptable" not in r.lower():
                sigs.append(r)
    
    print(f"\n{name} ({cid}) | DB: score={score}, delay={delay}, util={util:.0f}%, savings={savings:.0f}%")
    print(f"  ML Fusion: {ml['fusion_score']} | Signals: {len(sigs)}")
    for domain, reasons in reasoning.items():
        for r in reasons:
            marker = "✅ INCLUDED" if r in sigs else "❌ FILTERED"
            print(f"    [{domain}] {marker}: {r}")
