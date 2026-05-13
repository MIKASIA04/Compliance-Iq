# ============================================================
# FILE: backend/seed_data.py
# ============================================================
#
# WHAT IS THIS FILE?
# ------------------
# This script creates realistic demo data in your database
# so Person 3 has actual alerts to display on the dashboard.
#
# Without this, the dashboard would be empty and Person 3
# cannot test their UI components with real data.
#
# HOW TO RUN:
# -----------
# Make sure the server is NOT running (stop uvicorn first).
# Make sure (.venv) is active.
# From the backend/ folder, run:
#     python seed_data.py
#
# You should see:
#     Seeding database with demo transactions...
#     [1/8] HIGH RISK — Submitted (alert created: abc123)
#     [2/8] MEDIUM RISK — Submitted (alert created: def456)
#     ...
#     Done! 6 alerts created. 2 clean transactions.
#
# After running, restart your server:
#     uvicorn app.main:app --reload
#
# Then visit GET /alerts in /docs — you should see 6 alerts.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import uuid

from app.database import SessionLocal, Base, engine, Transaction, Alert, User
from app.main import hash_password

# Create tables if not exists
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def create_transaction_and_alert(
    sender, receiver, amount, hour, tx_count_7d, kyc_verified,
    risk_level, violation_type, regulation_cited, explanation,
    days_ago=0
):
    """
    Helper function: creates one Transaction row and one Alert row.
    This simulates what the API would do when a transaction is flagged.
    """
    tx = Transaction(
        id=str(uuid.uuid4()),
        sender_account=sender,
        receiver_account=receiver,
        amount=amount,
        transaction_type="transfer",
        hour_of_day=hour,
        tx_count_7d=tx_count_7d,
        kyc_verified=kyc_verified,
        status="flagged",
        risk_score=0.91 if risk_level == "high" else 0.65,
        submitted_at=datetime.utcnow() - timedelta(days=days_ago, hours=2),
        checked_at=datetime.utcnow() - timedelta(days=days_ago, hours=2),
    )
    db.add(tx)
    db.flush()  # Get the tx.id without committing

    alert = Alert(
        id=str(uuid.uuid4()),
        transaction_id=tx.id,
        risk_level=risk_level,
        violation_type=violation_type,
        regulation_cited=regulation_cited,
        ai_explanation=explanation,
        # Store SHAP features as JSON string for the frontend chart
        shap_features_json='[{"feature":"amount","value":' + str(amount) + ',"shap_value":0.412,"impact":"increases_risk"},{"feature":"tx_count_7d","value":' + str(tx_count_7d) + ',"shap_value":0.283,"impact":"increases_risk"},{"feature":"hour_of_day","value":' + str(hour) + ',"shap_value":0.187,"impact":"increases_risk"},{"feature":"kyc_verified","value":' + str(0 if not kyc_verified else 1) + ',"shap_value":-0.118,"impact":"decreases_risk"}]',
        status="open",
        created_at=datetime.utcnow() - timedelta(days=days_ago, hours=1),
    )
    db.add(alert)
    db.commit()
    return alert.id


def create_clean_transaction(sender, receiver, amount, hour, days_ago=0):
    """Creates a clean (non-flagged) transaction."""
    tx = Transaction(
        id=str(uuid.uuid4()),
        sender_account=sender,
        receiver_account=receiver,
        amount=amount,
        transaction_type="transfer",
        hour_of_day=hour,
        tx_count_7d=1,
        kyc_verified=True,
        status="clean",
        risk_score=0.04,
        submitted_at=datetime.utcnow() - timedelta(days=days_ago),
        checked_at=datetime.utcnow() - timedelta(days=days_ago),
    )
    db.add(tx)
    db.commit()


print("Seeding database with demo transactions...")
print()

# ── DEMO TRANSACTION 1: HIGH RISK — Structuring + KYC bypass ────────────────
alert_id = create_transaction_and_alert(
    sender="ACC10234",
    receiver="ACC98712",
    amount=980000,
    hour=2,
    tx_count_7d=4,
    kyc_verified=False,
    risk_level="high",
    violation_type="Structuring + KYC Bypass",
    regulation_cited="PMLA 2002 — Section 3 + RBI KYC MD 2023 — Section 16(3)",
    explanation=(
        "COMPLIANCE ALERT — HIGH RISK\n\n"
        "Summary: Transfer of ₹9,80,000 from ACC10234 to unverified account "
        "ACC98712 flagged for possible structuring and KYC bypass.\n\n"
        "Violation Detail: The amount (₹9,80,000) is 98% of the ₹10,00,000 "
        "mandatory reporting threshold, consistent with deliberate structuring "
        "under PMLA 2002, Section 3. The receiving account has not completed "
        "KYC, triggering enhanced due diligence under RBI KYC Master Direction "
        "2023, Section 16(3). Transfer was initiated at 02:00 hrs, which is "
        "behaviourally unusual for legitimate business transactions.\n\n"
        "Required Action: (1) Initiate enhanced due diligence on ACC98712 "
        "within 24 hours. (2) File a Suspicious Transaction Report with "
        "FIU-IND within 7 working days per PMLA Rule 7."
    ),
    days_ago=0,
)
print(f"[1/8] HIGH RISK — Structuring + KYC Bypass (alert: {alert_id[:8]}...)")

# ── DEMO TRANSACTION 2: HIGH RISK — Large overnight transfer ─────────────────
alert_id = create_transaction_and_alert(
    sender="ACC77432",
    receiver="ACC19283",
    amount=2500000,
    hour=3,
    tx_count_7d=2,
    kyc_verified=False,
    risk_level="high",
    violation_type="Suspicious Overnight Transfer",
    regulation_cited="PMLA 2002 — Rule 7 + RBI Fraud Risk Management Circular",
    explanation=(
        "COMPLIANCE ALERT — HIGH RISK\n\n"
        "Summary: Transfer of ₹25,00,000 at 03:00 hrs to an unverified account.\n\n"
        "Violation Detail: This high-value transfer initiated between midnight "
        "and 4am is classified as behaviourally unusual under PMLA Rule 7. "
        "The receiving account (ACC19283) has not completed KYC verification, "
        "additionally violating RBI KYC Master Direction 2023 Section 16(3).\n\n"
        "Required Action: Freeze transaction pending enhanced due diligence. "
        "File STR with FIU-IND within 7 working days."
    ),
    days_ago=0,
)
print(f"[2/8] HIGH RISK — Overnight Transfer (alert: {alert_id[:8]}...)")

# ── DEMO TRANSACTION 3: HIGH RISK — Pattern structuring ──────────────────────
alert_id = create_transaction_and_alert(
    sender="ACC55501",
    receiver="ACC34421",
    amount=750000,
    hour=11,
    tx_count_7d=5,
    kyc_verified=True,
    risk_level="high",
    violation_type="Pattern Structuring",
    regulation_cited="PMLA 2002 — Section 3 + FATF Recommendation 16",
    explanation=(
        "COMPLIANCE ALERT — HIGH RISK\n\n"
        "Summary: Sender ACC55501 has made 5 large transfers this week, "
        "suggesting systematic structuring to avoid reporting thresholds.\n\n"
        "Violation Detail: The frequency of transactions (5 in 7 days), "
        "each above ₹5,00,000, is consistent with the multi-transaction "
        "structuring pattern defined under PMLA 2002 Section 3 and flagged "
        "by FATF Recommendation 16.\n\n"
        "Required Action: Review full transaction history for ACC55501. "
        "File STR with FIU-IND if structuring is confirmed."
    ),
    days_ago=1,
)
print(f"[3/8] HIGH RISK — Pattern Structuring (alert: {alert_id[:8]}...)")

# ── DEMO TRANSACTION 4: MEDIUM RISK — Mandatory reporting threshold ───────────
alert_id = create_transaction_and_alert(
    sender="ACC11111",
    receiver="ACC22222",
    amount=1500000,
    hour=14,
    tx_count_7d=1,
    kyc_verified=True,
    risk_level="medium",
    violation_type="PMLA Mandatory Reporting",
    regulation_cited="PMLA 2002 — Rule 7",
    explanation=(
        "COMPLIANCE ALERT — MEDIUM RISK\n\n"
        "Summary: Transfer of ₹15,00,000 meets the PMLA mandatory reporting "
        "threshold requiring an STR filing.\n\n"
        "Violation Detail: Transactions at or above ₹10,00,000 must be "
        "reported to FIU-IND within 7 working days under PMLA 2002 Rule 7. "
        "This is an informational alert — not necessarily suspicious, but "
        "action is legally required.\n\n"
        "Required Action: File Suspicious Transaction Report with FIU-IND "
        "within 7 working days."
    ),
    days_ago=1,
)
print(f"[4/8] MEDIUM RISK — Mandatory Reporting (alert: {alert_id[:8]}...)")

# ── DEMO TRANSACTION 5: MEDIUM RISK — KYC bypass smaller amount ──────────────
alert_id = create_transaction_and_alert(
    sender="ACC33901",
    receiver="ACC78234",
    amount=620000,
    hour=16,
    tx_count_7d=2,
    kyc_verified=False,
    risk_level="medium",
    violation_type="KYC Enhanced Due Diligence",
    regulation_cited="RBI KYC Master Direction 2023 — Section 16(3)",
    explanation=(
        "COMPLIANCE ALERT — MEDIUM RISK\n\n"
        "Summary: Transfer of ₹6,20,000 to an unverified account requiring "
        "enhanced due diligence.\n\n"
        "Violation Detail: Per RBI KYC Master Direction 2023 Section 16(3), "
        "transactions above ₹5,00,000 to accounts without completed KYC "
        "require Enhanced Due Diligence before processing.\n\n"
        "Required Action: Complete KYC verification for ACC78234 before "
        "processing this transaction."
    ),
    days_ago=2,
)
print(f"[5/8] MEDIUM RISK — KYC Bypass (alert: {alert_id[:8]}...)")

# ── DEMO TRANSACTION 6: HIGH RISK — Already resolved (for demo purposes) ─────
alert_id = create_transaction_and_alert(
    sender="ACC99001",
    receiver="ACC12300",
    amount=970000,
    hour=1,
    tx_count_7d=3,
    kyc_verified=False,
    risk_level="high",
    violation_type="Structuring + Overnight",
    regulation_cited="PMLA 2002 — Section 3",
    explanation=(
        "COMPLIANCE ALERT — HIGH RISK\n\n"
        "Summary: ₹9,70,000 transfer at 01:00 hrs to unverified account, "
        "3rd such transfer this week.\n\n"
        "Violation Detail: Multiple indicators of structuring and suspicious "
        "behaviour detected.\n\n"
        "Required Action: Enhanced due diligence and STR filing required."
    ),
    days_ago=3,
)
# Mark this one as resolved so the dashboard shows a mix of statuses
db.query(Alert).filter(Alert.id == alert_id).update({
    "status": "resolved",
    "resolved_at": datetime.utcnow() - timedelta(days=2),
    "resolution_notes": "Verified with customer. Legitimate salary advance. Closed."
})
db.commit()
print(f"[6/8] HIGH RISK — Resolved example (alert: {alert_id[:8]}...)")

# ── DEMO TRANSACTION 7: CLEAN — Normal transfer ───────────────────────────────
create_clean_transaction("ACC55555", "ACC66666", 25000, 15, days_ago=0)
print(f"[7/8] CLEAN — Small normal transfer")

# ── DEMO TRANSACTION 8: CLEAN — Larger but legitimate ────────────────────────
create_clean_transaction("ACC77777", "ACC88888", 450000, 10, days_ago=1)
print(f"[8/8] CLEAN — Larger verified transfer")

db.close()

print()
print("=" * 50)
print("Done! Seeded:")
print("  6 flagged alerts (5 open, 1 resolved)")
print("  2 clean transactions")
print()
print("Now restart your server and test:")
print("  GET /alerts         → should show 5 open alerts")
print("  GET /dashboard/summary → should show counts")
print("=" * 50)
