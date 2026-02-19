from backend.ml_engine import MLRiskEngine
import pandas as pd
import numpy as np
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

def test_engine():
    print("--- ML ENGINE INTEGRATION TEST ---")
    print("Initializing MLRiskEngine...")
    engine = MLRiskEngine()
    
    if not engine.initialized:
        print("Engine failed to initialize. Please check model store.")
        return

    print("Engine initialized successfully with Real AIML Models.")
    
    test_cases = [
        {
            "name": "High Risk Customer",
            "features": {
                't_current_salary_delay': 15,
                'f_savings_change_pct': -50,
                'f_credit_utilization': 92,
                't_auto_debit_fail_count': 3,
                'b_loan_inquiry_count': 6,
                'distress_spend_ratio': 0.2,
                'f_monthly_salary': 45000
            }
        },
        {
            "name": "Low Risk Customer",
            "features": {
                't_current_salary_delay': 0,
                'f_savings_change_pct': 5,
                'f_credit_utilization': 20,
                't_auto_debit_fail_count': 0,
                'b_loan_inquiry_count': 0,
                'distress_spend_ratio': 0.01,
                'f_monthly_salary': 100000
            }
        }
    ]

    for case in test_cases:
        print(f"\nTesting: {case['name']}")
        result = engine.predict_ensemble(case['features'])
        print(f"  Fusion Score: {result['fusion_score']}")
        print(f"  Confidence: {result['confidence_score']}")
        print(f"  Scores: {result['agent_scores']}")
        print(f"  Reasoning: {list(result['agent_reasoning'].values())[0][0]}...") # First reason of first agent

if __name__ == "__main__":
    test_engine()
