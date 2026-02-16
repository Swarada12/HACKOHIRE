import bentoml
import xgboost as xgb
import numpy as np

# Create a dummy runner to test
try:
    # Create valid dummy model first? Or just use existing logic
    # We'll just mock a runner object or use existing model if available
    # Assuming bank_risk_xgb exists from training
    risk_runner = bentoml.xgboost.get("bank_risk_xgb:latest").to_runner()
    
    print("Testing @bentoml.service(runners=[...])")
    @bentoml.service(name="test_runners", runners=[risk_runner])
    class TestRunnerService:
        pass
    print("Success with runners in decorator")
except Exception as e:
    print(f"Failed with runners in decorator: {e}")
