"""
evaluate_ablation.py — real per-component ablation (Table IV)
Run: python -m ml.evaluate_ablation
"""
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from ml.rule_engine import check_rules

FEATURES = ["amount", "hour_of_day", "tx_count_7d", "kyc_verified"]

def metrics(y_true, y_pred, label):
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"{label:30s} P={p:.3f}  R={r:.3f}  F1={f1:.3f}  FPR={fpr:.3f}")

def main():
    df = pd.read_csv("dataset/transactions.csv")
    X = df[FEATURES]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    test_df = df.loc[X_test.index].copy()

    with open("ml/model.pkl", "rb") as f:
        model = pickle.load(f)

    ml_pred = model.predict(X_test)
    ml_prob = model.predict_proba(X_test)[:, 1]

    rule_pred = []
    high_sev_pred = []
    for _, row in test_df.iterrows():
        tx = {
            "amount": row["amount"], "hour_of_day": row["hour_of_day"],
            "tx_count_7d": row["tx_count_7d"], "kyc_verified": bool(row["kyc_verified"]),
        }
        v = check_rules(tx)
        rule_pred.append(1 if len(v) > 0 else 0)
        high_sev_pred.append(1 if any(x.severity == "HIGH" for x in v) else 0)

    combined_full = [1 if (r or m) else 0 for r, m in zip(rule_pred, ml_pred)]
    combined_high_only = [1 if (h or m) else 0 for h, m in zip(high_sev_pred, ml_pred)]
    ml_only_thresh07 = [1 if p >= 0.7 else 0 for p in ml_prob]

    print("=== TABLE IV — ABLATION (REAL) ===")
    metrics(y_test, rule_pred, "Rule engine only (all severities)")
    metrics(y_test, ml_pred, "XGBoost only (default 0.5 thresh)")
    metrics(y_test, ml_only_thresh07, "XGBoost only (thresh 0.7)")
    metrics(y_test, combined_full, "Full system (rule ANY + ML)")
    metrics(y_test, combined_high_only, "Ablation: HIGH-severity rules only + ML")

if __name__ == "__main__":
    main()