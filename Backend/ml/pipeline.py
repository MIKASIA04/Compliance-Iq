"""
pipeline.py — Person 2's File 3 (THE MOST IMPORTANT FILE)
This is the brain of the entire system.

It takes one transaction dictionary and returns a complete analysis:
  - Rule violations (from rule_engine.py)
  - ML risk score + probability (from model.pkl)
  - SHAP explanation: why did the model flag this? (from shap_explainer.pkl)
  - A plain-English alert summary

Person 1's main.py imports and calls: analyze_transaction(tx_dict)
That is the ONLY integration point. One function in, one result out.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Optional

# Import our rule engine from the same folder
from ml.rule_engine import check_rules, RuleViolation


# ── Load models once at startup (not on every request) ───────────────────────

_model = None
_explainer = None

def _load_models():
    """Load model.pkl and shap_explainer.pkl from disk. Called once."""
    global _model, _explainer

    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    explainer_path = os.path.join(os.path.dirname(__file__), "shap_explainer.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            "ml/model.pkl not found.\n"
            "Run this command first:  python ml/train_model.py"
        )

    with open(model_path, "rb") as f:
        _model = pickle.load(f)

    with open(explainer_path, "rb") as f:
        _explainer = pickle.load(f)


# ── SHAP explanation helper ───────────────────────────────────────────────────

FEATURE_LABELS = {
    "amount":       "Transaction Amount",
    "hour_of_day":  "Time of Day",
    "tx_count_7d":  "Transaction Frequency (7d)",
    "kyc_verified": "KYC Status",
}

def _get_shap_explanation(transaction_df: pd.DataFrame) -> list[dict]:
    """
    Returns top 3 features that drove the ML model's decision.
    Each item: { feature_name, display_name, value, contribution, direction }
    """
    shap_values = _explainer.shap_values(transaction_df)

    # shap_values shape: (1, 4) — one row, four features
    row_shap = shap_values[0] if len(shap_values.shape) > 1 else shap_values

    features = transaction_df.columns.tolist()
    explanations = []

    for i, feat in enumerate(features):
        contrib = float(row_shap[i])
        explanations.append({
            "feature_name": feat,
            "display_name": FEATURE_LABELS.get(feat, feat),
            "value": float(transaction_df[feat].iloc[0]),
            "contribution": round(abs(contrib), 4),
            "direction": "increases_risk" if contrib > 0 else "decreases_risk",
        })

    # Sort by absolute contribution, highest first
    explanations.sort(key=lambda x: x["contribution"], reverse=True)
    return explanations[:3]  # Return top 3 only


# ── Risk level helper ─────────────────────────────────────────────────────────

def _risk_level(probability: float, rule_violations: list) -> str:
    high_severity_rules = [v for v in rule_violations if v.severity == "HIGH"]
    if probability >= 0.7 or len(high_severity_rules) >= 1:
        return "HIGH"
    elif probability >= 0.4 or len(rule_violations) >= 1:
        return "MEDIUM"
    else:
        return "LOW"


# ── Plain-English alert summary ───────────────────────────────────────────────

def _build_summary(transaction: dict, risk_level: str,
                   rule_violations: list, shap_top3: list) -> str:
    amount = transaction.get("amount", 0)
    kyc = transaction.get("kyc_verified", True)
    tx_count = transaction.get("tx_count_7d", 0)
    hour = transaction.get("hour_of_day", 12)

    if not rule_violations and risk_level == "LOW":
        return (f"Transaction of ₹{amount:,.0f} processed normally. "
                "No regulatory flags or anomalies detected.")

    lines = [f"⚠ {risk_level} RISK ALERT — Transaction of ₹{amount:,.0f}\n"]

    if rule_violations:
        lines.append("Regulatory violations detected:")
        for v in rule_violations:
            lines.append(f"  • [{v.rule_id}] {v.rule_name}")
            lines.append(f"    Source: {v.regulation_source}")
            lines.append(f"    Detail: {v.description}")

    if shap_top3:
        lines.append("\nML model flagged this transaction because:")
        for item in shap_top3:
            direction_text = "↑ raises risk" if item["direction"] == "increases_risk" else "↓ lowers risk"
            lines.append(f"  • {item['display_name']} = {item['value']} ({direction_text})")

    lines.append("\nRecommended action: " + (
        "Escalate to Compliance Officer immediately and file STR with FIU-IND within 24 hours."
        if risk_level == "HIGH"
        else "Review manually before processing. Document findings."
    ))

    return "\n".join(lines)


# ── PUBLIC API — the one function Person 1 calls ──────────────────────────────

def analyze_transaction(transaction: dict) -> dict:
    """
    Main entry point. Takes a transaction dict, returns full analysis.

    Input dict keys:
        sender_account   (str)
        receiver_account (str)
        amount           (float)  — INR
        hour_of_day      (int)    — 0 to 23
        tx_count_7d      (int)    — transactions in last 7 days
        kyc_verified     (bool)

    Returns dict:
        risk_level         "HIGH" | "MEDIUM" | "LOW"
        ml_probability     float 0–1 (model's confidence it's suspicious)
        rule_violations    list of violation dicts
        shap_explanation   list of top-3 feature contributions
        summary            plain-English alert text
        flagged            bool — True if any issue found
    """
    global _model, _explainer
    if _model is None:
        _load_models()

    # 1. Rule-based check
    violations = check_rules(transaction)

    # 2. ML model check
    features = ["amount", "hour_of_day", "tx_count_7d", "kyc_verified"]
    tx_df = pd.DataFrame([{
        "amount":       transaction.get("amount", 0),
        "hour_of_day":  transaction.get("hour_of_day", 12),
        "tx_count_7d":  transaction.get("tx_count_7d", 0),
        "kyc_verified": int(transaction.get("kyc_verified", True)),
    }])[features]

    ml_prob = float(_model.predict_proba(tx_df)[0][1])  # probability of being suspicious

    # 3. Risk level (combines rules + ML)
    risk = _risk_level(ml_prob, violations)

    # 4. SHAP explanation
    shap_top3 = _get_shap_explanation(tx_df)

    # 5. Plain-English summary
    summary = _build_summary(transaction, risk, violations, shap_top3)

    return {
        "risk_level":       risk,
        "ml_probability":   round(ml_prob, 4),
        "rule_violations": [
            {
                "rule_id":           v.rule_id,
                "rule_name":         v.rule_name,
                "regulation_source": v.regulation_source,
                "description":       v.description,
                "severity":          v.severity,
            }
            for v in violations
        ],
        "shap_explanation": shap_top3,
        "summary":          summary,
        "flagged":          risk in ("HIGH", "MEDIUM") or len(violations) > 0,
    }


# ── Quick self-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing pipeline.py — running 3 sample transactions...\n")

    samples = [
        {
            "name": "Suspicious structuring transaction",
            "tx": {
                "sender_account": "ACC10234",
                "receiver_account": "ACC98712",
                "amount": 980_000,
                "hour_of_day": 2,
                "tx_count_7d": 4,
                "kyc_verified": False,
            }
        },
        {
            "name": "Normal everyday transaction",
            "tx": {
                "sender_account": "ACC55001",
                "receiver_account": "ACC77832",
                "amount": 12_500,
                "hour_of_day": 14,
                "tx_count_7d": 3,
                "kyc_verified": True,
            }
        },
        {
            "name": "Large transaction at odd hour",
            "tx": {
                "sender_account": "ACC30019",
                "receiver_account": "ACC44210",
                "amount": 1_500_000,
                "hour_of_day": 3,
                "tx_count_7d": 25,
                "kyc_verified": True,
            }
        },
    ]

    for sample in samples:
        print(f"{'─'*55}")
        print(f"TEST: {sample['name']}")
        result = analyze_transaction(sample["tx"])
        print(f"  Risk Level    : {result['risk_level']}")
        print(f"  ML Probability: {result['ml_probability']:.1%}")
        print(f"  Flagged       : {result['flagged']}")
        print(f"  Rule Violations: {len(result['rule_violations'])}")
        print(f"  Top SHAP Feature: {result['shap_explanation'][0]['display_name']}")
        print()

    print("Pipeline test complete ✓")
