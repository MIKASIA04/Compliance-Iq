"""
rule_engine.py — Person 2's File 1
Hard-coded legal rule checker for Indian fintech compliance.
Each rule maps directly to an RBI/PMLA regulation.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class RuleViolation:
    rule_id: str
    rule_name: str
    regulation_source: str
    description: str
    severity: str  # "HIGH", "MEDIUM", "LOW"


def check_rules(transaction: dict) -> List[RuleViolation]:
    """
    Takes a transaction dictionary and returns a list of rule violations.

    Transaction dict keys:
        amount          — transaction amount in INR (e.g. 980000)
        hour_of_day     — hour transaction happened (0–23)
        tx_count_7d     — how many transactions this account made in last 7 days
        kyc_verified    — True/False, is the sender KYC verified?
        sender_account  — account ID string
        receiver_account— account ID string
    """
    violations = []
    amount = transaction.get("amount", 0)
    hour = transaction.get("hour_of_day", 12)
    tx_count = transaction.get("tx_count_7d", 0)
    kyc_verified = transaction.get("kyc_verified", True)

    # ── Rule 1: Large Cash Transaction ──────────────────────────────────────
    # PMLA 2002 / RBI Master Direction: transactions ≥ ₹10 lakh must be
    # reported to the Financial Intelligence Unit (FIU-IND).
    if amount >= 1_000_000:
        violations.append(RuleViolation(
            rule_id="R001",
            rule_name="Large Cash Transaction Threshold",
            regulation_source="PMLA 2002 — Section 12, FIU-IND Reporting",
            description=f"Transaction amount ₹{amount:,.0f} meets or exceeds the ₹10 lakh "
                        "mandatory reporting threshold. Must be reported to FIU-IND within 7 days.",
            severity="HIGH"
        ))

    # ── Rule 2: Structuring (Smurfing) ───────────────────────────────────────
    # Breaking large transactions into smaller ones just below ₹10 lakh to
    # avoid reporting — this is illegal under PMLA 2002 Section 3.
    if 800_000 <= amount < 1_000_000:
        violations.append(RuleViolation(
            rule_id="R002",
            rule_name="Possible Structuring / Smurfing",
            regulation_source="PMLA 2002 — Section 3 (Money Laundering Offence)",
            description=f"Transaction of ₹{amount:,.0f} is suspiciously close to but below the "
                        "₹10 lakh reporting threshold. Pattern suggests deliberate structuring to "
                        "avoid AML reporting obligations.",
            severity="HIGH"
        ))

    # ── Rule 3: Off-hours High-Value Transaction ─────────────────────────────
    # RBI guidelines flag high-value transactions during unusual hours
    # (midnight to 5am) as elevated risk.
    if amount > 500_000 and (hour < 5 or hour >= 23):
        violations.append(RuleViolation(
            rule_id="R003",
            rule_name="Off-Hours High-Value Transaction",
            regulation_source="RBI Digital Payments Security Controls — Annex 3",
            description=f"₹{amount:,.0f} transacted at {hour:02d}:00 hours. High-value transactions "
                        "between 11pm–5am require enhanced monitoring under RBI fraud prevention norms.",
            severity="MEDIUM"
        ))

    # ── Rule 4: KYC Non-Compliance ───────────────────────────────────────────
    # RBI Master Direction on KYC 2016 (updated 2023): no transactions above
    # ₹50,000 for accounts that have not completed full KYC.
    if not kyc_verified and amount > 50_000:
        violations.append(RuleViolation(
            rule_id="R004",
            rule_name="KYC Non-Compliant Transaction",
            regulation_source="RBI Master Direction on KYC — 2016 (amended 2023), Section 16",
            description=f"Account is not KYC-verified but attempted a ₹{amount:,.0f} transaction. "
                        "Transactions above ₹50,000 are prohibited for non-KYC accounts.",
            severity="HIGH"
        ))

    # ── Rule 5: Velocity / Rapid Fire Transactions ───────────────────────────
    # More than 20 transactions in 7 days from the same account is flagged
    # as unusual velocity — possible account takeover or layering.
    if tx_count > 20:
        violations.append(RuleViolation(
            rule_id="R005",
            rule_name="Unusual Transaction Velocity",
            regulation_source="RBI Fraud Risk Management Guidelines 2023 — Section 4.2",
            description=f"Account made {tx_count} transactions in the last 7 days, exceeding the "
                        "20-transaction velocity threshold. Possible layering or account compromise.",
            severity="MEDIUM"
        ))

    # ── Rule 6: Round-Number Suspicion ───────────────────────────────────────
    # Exact round numbers (e.g. ₹500,000.00) are a common AML red flag —
    # real transactions rarely end in exactly 0,000.
    if amount >= 100_000 and amount % 100_000 == 0:
        violations.append(RuleViolation(
            rule_id="R006",
            rule_name="Suspicious Round-Number Amount",
            regulation_source="FATF Recommendation 20 — Suspicious Transaction Reporting",
            description=f"₹{amount:,.0f} is a suspiciously round number. Round-value transactions "
                        "are a recognised red flag under FATF guidance and RBI AML norms.",
            severity="LOW"
        ))

    return violations


# ── Self-test: run this file directly to verify all 6 rules work ─────────────
if __name__ == "__main__":
    test_cases = [
        # (description, transaction, should_trigger_rule_ids)
        ("Large cash (₹12L)", {"amount": 1_200_000, "hour_of_day": 10, "tx_count_7d": 2, "kyc_verified": True}, ["R001"]),
        ("Structuring (₹9.5L)", {"amount": 950_000, "hour_of_day": 14, "tx_count_7d": 3, "kyc_verified": True}, ["R002"]),
        ("Off-hours (₹6L at 2am)", {"amount": 600_000, "hour_of_day": 2, "tx_count_7d": 1, "kyc_verified": True}, ["R003"]),
        ("KYC fail (₹1L no KYC)", {"amount": 100_000, "hour_of_day": 11, "tx_count_7d": 2, "kyc_verified": False}, ["R004"]),
        ("High velocity (25 tx)", {"amount": 5_000, "hour_of_day": 9, "tx_count_7d": 25, "kyc_verified": True}, ["R005"]),
        ("Round number (₹5L)", {"amount": 500_000, "hour_of_day": 15, "tx_count_7d": 1, "kyc_verified": True}, ["R006"]),
    ]

    all_passed = True
    for desc, tx, expected_ids in test_cases:
        violations = check_rules(tx)
        found_ids = [v.rule_id for v in violations]
        passed = all(rid in found_ids for rid in expected_ids)
        status = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f"{status} {desc}")
        for v in violations:
            print(f"       → {v.rule_id}: {v.rule_name} ({v.severity})")

    print()
    print("All tests passed ✓" if all_passed else "Some tests FAILED — check above")
