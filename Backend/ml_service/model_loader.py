# ============================================================
# FILE: ml_service/model_loader.py
# ============================================================
# Loads the REAL trained model + SHAP explainer and wraps them
# so the ml_service microservice returns real predictions
# instead of placeholder fake numbers.
# ============================================================

import os
import pickle


def load_model():
    path = "ml/model.pkl"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


def load_explainer():
    path = "ml/shap_explainer.pkl"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Explainer not found at {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


try:
    _model = load_model()
    _explainer = load_explainer()
    print("  Real ML model and SHAP explainer loaded.")
except FileNotFoundError as e:
    print(f"  WARNING: {e}")
    _model = _explainer = None


class FraudDetectionModel:
    """
    Wraps the real trained pipeline (rule engine + XGBoost + SHAP)
    so ml_service/main.py can call it exactly as before, but now
    it returns real predictions instead of fake placeholder ones.
    """

    def predict(self, transaction: dict) -> dict:
        from ml.pipeline import analyze_transaction

        tx_data = {
            "amount": transaction.get("amount", 0),
            "hour_of_day": transaction.get("hour_of_day", 12),
            "tx_count_7d": transaction.get("tx_count_7d", 1),
            "kyc_verified": transaction.get("kyc_verified", True),
        }
        result = analyze_transaction(tx_data)
        return result
