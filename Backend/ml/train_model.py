"""
train_model.py — Person 2's File 2

Generates 10,000 synthetic transactions, trains an XGBoost classifier,
evaluates it, and saves the trained model + SHAP explainer to disk.

The generated dataset contains realistic transaction metadata:
    transaction_id
    sender_account
    receiver_account
    transaction_type
    timestamp
    amount
    hour_of_day
    tx_count_7d
    kyc_verified
    label

The ML model continues to use these four features:
    amount
    hour_of_day
    tx_count_7d
    kyc_verified

Run this ONCE. It produces:
    ml/model.pkl
    ml/shap_explainer.pkl
    dataset/transactions.csv
"""

import os
import pickle
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from xgboost import XGBClassifier
import shap


fake = Faker("en_IN")

np.random.seed(42)


# ── Step 1: Generate synthetic dataset ───────────────────────────────────────

def generate_dataset(n_samples: int = 10_000) -> pd.DataFrame:
    """
    Produces realistic-looking synthetic transaction rows.

    The transaction metadata is synthetic and does not represent
    real customer or financial account information.

    About 15% of rows are deliberately crafted as positive/risk-pattern
    examples so the supervised model has examples to learn from.
    """

    rows = []

    transaction_types = [
        "transfer",
        "payment",
        "withdrawal",
        "deposit",
    ]

    start_date = datetime(2026, 1, 1)

    for i in range(n_samples):

        # ── Transaction identity ─────────────────────────────────────────────

        transaction_id = str(uuid.uuid4())

        sender_account = f"ACC{np.random.randint(10000, 99999)}"
        receiver_account = f"ACC{np.random.randint(10000, 99999)}"

        while receiver_account == sender_account:
            receiver_account = f"ACC{np.random.randint(10000, 99999)}"

        transaction_type = np.random.choice(
            transaction_types,
            p=[0.50, 0.30, 0.10, 0.10],
        )

        # Generate a timestamp across one year
        timestamp = start_date + timedelta(
            days=int(np.random.randint(0, 365)),
            hours=int(np.random.randint(0, 24)),
            minutes=int(np.random.randint(0, 60)),
            seconds=int(np.random.randint(0, 60)),
        )

        # ── Decide whether this is a positive/risk-pattern example ───────────

        is_violation = np.random.random() < 0.15

        if is_violation:

            # Inject one of 5 risk patterns
            pattern = np.random.choice(
                [
                    "large",
                    "structuring",
                    "off_hours",
                    "no_kyc",
                    "velocity",
                ]
            )

            if pattern == "large":

                amount = np.random.uniform(
                    1_000_000,
                    3_000_000,
                )

                hour = np.random.randint(0, 24)

                tx_count = np.random.randint(1, 10)

                kyc = True

            elif pattern == "structuring":

                amount = np.random.uniform(
                    800_000,
                    999_999,
                )

                hour = np.random.randint(0, 24)

                tx_count = np.random.randint(1, 8)

                kyc = True

            elif pattern == "off_hours":

                amount = np.random.uniform(
                    500_001,
                    900_000,
                )

                hour = np.random.choice(
                    list(range(0, 5)) + [23]
                )

                tx_count = np.random.randint(1, 6)

                kyc = True

            elif pattern == "no_kyc":

                amount = np.random.uniform(
                    50_001,
                    400_000,
                )

                hour = np.random.randint(6, 22)

                tx_count = np.random.randint(1, 5)

                kyc = False

            else:
                # High transaction velocity

                amount = np.random.uniform(
                    1_000,
                    50_000,
                )

                hour = np.random.randint(6, 22)

                tx_count = np.random.randint(21, 60)

                kyc = True

            label = 1

        else:

            # ── Normal transaction ───────────────────────────────────────────

            amount = np.random.exponential(
                scale=25_000
            )

            amount = min(
                amount,
                750_000
            )

            hour = np.random.randint(
                6,
                22
            )

            tx_count = np.random.randint(
                0,
                15
            )

            kyc = np.random.random() > 0.05

            label = 0

        # ── Store row ────────────────────────────────────────────────────────

        rows.append(
            {
                "transaction_id": transaction_id,
                "sender_account": sender_account,
                "receiver_account": receiver_account,
                "transaction_type": transaction_type,
                "timestamp": timestamp.isoformat(),

                # Existing ML features
                "amount": round(amount, 2),
                "hour_of_day": hour,
                "tx_count_7d": tx_count,
                "kyc_verified": int(kyc),

                # Training label
                "label": label,
            }
        )

    return pd.DataFrame(rows)


# ── Step 2: Train the model ──────────────────────────────────────────────────

def train_and_evaluate(df: pd.DataFrame):

    # These remain the four features used by the current ML model.
    features = [
        "amount",
        "hour_of_day",
        "tx_count_7d",
        "kyc_verified",
    ]

    X = df[features]

    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=5,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    # ── Evaluate ─────────────────────────────────────────────────────────────

    y_pred = model.predict(X_test)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred,
    ).ravel()

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    print("\n" + "=" * 50)
    print("         MODEL EVALUATION RESULTS")
    print("=" * 50)

    print(
        f"  Precision           : "
        f"{precision_score(y_test, y_pred) * 100:.1f}%"
    )

    print(
        f"  Recall              : "
        f"{recall_score(y_test, y_pred) * 100:.1f}%"
    )

    print(
        f"  F1 Score            : "
        f"{f1_score(y_test, y_pred):.3f}"
    )

    print(
        f"  False Positive Rate : "
        f"{fpr * 100:.1f}%"
    )

    print(
        f"  True Positives      : "
        f"{tp}   (positive examples correctly caught)"
    )

    print(
        f"  False Negatives     : "
        f"{fn}   (positive examples missed)"
    )

    print("=" * 50)
    print("  ✓ Model evaluation complete")
    print("=" * 50 + "\n")

    return model, X_test


# ── Step 3: Build SHAP explainer ─────────────────────────────────────────────

def build_shap_explainer(
    model,
    X_test: pd.DataFrame,
):

    explainer = shap.TreeExplainer(
        model
    )

    # Warm up with test data
    _ = explainer.shap_values(
        X_test.iloc[:5]
    )

    return explainer


# ── Step 4: Save both to disk ────────────────────────────────────────────────

def save_artifacts(
    model,
    explainer,
):

    os.makedirs(
        "ml",
        exist_ok=True,
    )

    with open(
        "ml/model.pkl",
        "wb",
    ) as f:

        pickle.dump(
            model,
            f
        )

    with open(
        "ml/shap_explainer.pkl",
        "wb",
    ) as f:

        pickle.dump(
            explainer,
            f
        )

    print(
        "  ✓ Saved ml/model.pkl"
    )

    print(
        "  ✓ Saved ml/shap_explainer.pkl"
    )

    print(
        "  → These two files are loaded by "
        "pipeline.py at runtime\n"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print(
        "\nStep 1/4 — Generating "
        "10,000 synthetic transactions..."
    )

    df = generate_dataset(
        10_000
    )

    violation_count = int(
        df["label"].sum()
    )

    normal_count = (
        len(df) - violation_count
    )

    print(
        f"  ✓ Generated {len(df):,} transactions"
    )

    print(
        f"  ✓ Risk-pattern examples : "
        f"{violation_count:,}"
    )

    print(
        f"  ✓ Normal examples       : "
        f"{normal_count:,}\n"
    )

    # Save generated dataset
    os.makedirs(
        "dataset",
        exist_ok=True,
    )

    df.to_csv(
        "dataset/transactions.csv",
        index=False,
    )

    print(
        "  ✓ Saved to: "
        "dataset/transactions.csv\n"
    )

    print(
        "Step 2/4 — Training XGBoost model..."
    )

    model, X_test = train_and_evaluate(
        df
    )

    print(
        "Step 3/4 — Building SHAP explainer..."
    )

    explainer = build_shap_explainer(
        model,
        X_test,
    )

    print(
        "  ✓ SHAP explainer ready\n"
    )

    print(
        "Step 4/4 — Saving model and "
        "explainer to disk..."
    )

    save_artifacts(
        model,
        explainer,
    )

    print(
        "All done! You now have "
        "ml/model.pkl and ml/shap_explainer.pkl"
    )

    print(
        "Next step: run pipeline.py to "
        "wire everything together.\n"
    )