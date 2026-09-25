"""
evaluate_baselines.py — generates real B1/B2/Combined metrics (Table III)
and per-violation-type breakdown (Table V) on the actual held-out test split.

Run from Backend/ as:  python -m ml.evaluate_baselines
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from ml.rule_engine import check_rules
from ml.pipeline import analyze_transaction, _load_models

FEATURES = ["amount", "hour_of_day", "tx_count_7d", "kyc_verified"]

def metrics(y_true, y_pred, label):
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"{label:20s} P={p:.3f}  R={r:.3f}  F1={f1:.3f}  FPR={fpr:.3f}  TP={tp} FP={fp} FN={fn} TN={tn}")
    return p, r, f1, fpr

def main():
    df = pd.read_csv("dataset/transactions.csv")

    X = df[FEATURES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    test_df = df.loc[X_test.index].copy()  # keep 'pattern' column aligned to test rows

    _load_models()

    # ── B1: Rule engine only ──
    b1_pred = []
    for _, row in test_df.iterrows():
        tx = {
            "amount": row["amount"],
            "hour_of_day": row["hour_of_day"],
            "tx_count_7d": row["tx_count_7d"],
            "kyc_verified": bool(row["kyc_verified"]),
        }
        violations = check_rules(tx)
        b1_pred.append(1 if len(violations) > 0 else 0)

    # ── B2: XGBoost only ──
    import pickle
    with open("ml/model.pkl", "rb") as f:
        model = pickle.load(f)
    b2_pred = model.predict(X_test)

    # ── Combined system (rules + ML, via real pipeline) ──
    combined_pred = []
    for _, row in test_df.iterrows():
        tx = {
            "amount": row["amount"],
            "hour_of_day": row["hour_of_day"],
            "tx_count_7d": row["tx_count_7d"],
            "kyc_verified": bool(row["kyc_verified"]),
        }
        result = analyze_transaction(tx)
        combined_pred.append(1 if result["flagged"] else 0)

    print("\n=== TABLE III — DETECTION PERFORMANCE (REAL) ===")
    metrics(y_test, b1_pred, "B1 - Rule only")
    metrics(y_test, b2_pred, "B2 - XGBoost only")
    metrics(y_test, combined_pred, "Combined (rules+ML)")

    # ── Table V: per-violation-type ──
    print("\n=== TABLE V — PER-VIOLATION-TYPE PERFORMANCE (REAL, combined system) ===")
    test_df["combined_pred"] = combined_pred
    test_df["y_true"] = y_test.values

    for pattern in ["large", "structuring", "off_hours", "no_kyc", "velocity"]:
        subset = test_df[(test_df["pattern"] == pattern) | (test_df["pattern"] == "normal")]
        y_sub = (subset["pattern"] == pattern).astype(int)
        pred_sub = subset["combined_pred"]
        p = precision_score(y_sub, pred_sub, zero_division=0)
        r = recall_score(y_sub, pred_sub, zero_division=0)
        n = int((test_df["pattern"] == pattern).sum())
        print(f"{pattern:15s} P={p:.3f}  R={r:.3f}  (n={n} test examples)")

if __name__ == "__main__":
    main()