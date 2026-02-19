import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    import bentoml
    print("Attempting to load LSTM model separately...")
    try:
        lstm = bentoml.pytorch.load_model("bank_pattern_lstm:latest")
        print("✅ LSTM Loaded successfully via bentoml.pytorch")
    except Exception as e:
        print(f"❌ LSTM Load (pytorch) failed: {e}")
        try:
             lstm = bentoml.torchscript.load_model("bank_pattern_lstm:latest")
             print("✅ LSTM Loaded successfully via bentoml.torchscript")
        except Exception as e2:
             print(f"❌ LSTM Load (torchscript) failed: {e2}")

    from backend.ml_engine import MLRiskEngine
    print("\nAttempting to initialize MLRiskEngine...")
    engine = MLRiskEngine()
    if engine.initialized:
        print("✅ MLRiskEngine initialized successfully!")
    else:
        print("❌ MLRiskEngine failed to initialize.")
except Exception as e:
    print(f"❌ Error during import/init: {e}")
