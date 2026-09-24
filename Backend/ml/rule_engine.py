"""
rule_engine.py — Person 2's File 1

Rule-based compliance and risk checks for Indian fintech transactions.

Important:
These checks distinguish between:
1. Compliance-related conditions that may require review, and
2. Risk indicators that do NOT by themselves prove a legal violation.

The transaction dataset is synthetic and contains only:
amount, hour_of_day, tx_count_7d, kyc_verified.
Therefore, the rules do not claim facts that cannot be established
from these fields.
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
    Takes a transaction dictionary and returns compliance/risk findings.

    Transaction dict keys:
        amount           — transaction amount in INR
        hour_of_day      — hour transaction happened (0–23)
        tx_count_7d      — transactions from the account in last 7 days
        kyc_verified     — True/False, KYC status of the sender
        sender_account   — account ID string
        receiver_account — account ID string

    Important:
        A finding returned here does not automatically establish that
        a transaction is legally prohibited or that money laundering
        has occurred.
    """

    findings = []

    amount = transaction.get("amount", 0)
    hour = transaction.get("hour_of_day", 12)
    tx_count = transaction.get("tx_count_7d", 0)
    kyc_verified = transaction.get("kyc_verified", True)

    # ── Rule 1: Large Transaction Risk ──────────────────────────────────────
    #
    # The dataset does not tell us whether a transaction is cash,
    # whether it belongs to a reportable category, or whether the
    # relevant aggregation/reporting conditions are satisfied.
    #
    # Therefore, ₹10 lakh is treated as a risk/review threshold,
    # NOT as an automatic FIU-IND reporting violation.

    if amount >= 1_000_000:
        findings.append(RuleViolation(
            rule_id="R001",
            rule_name="Large Transaction — Enhanced Review",
            regulation_source=(
                "PMLA 2002 and applicable AML reporting requirements"
            ),
            description=(
                f"Transaction amount ₹{amount:,.0f} is a high-value transaction "
                "and should be reviewed against the applicable AML reporting "
                "and record-keeping requirements. The available transaction "
                "data does not establish that an FIU-IND report is automatically "
                "required."
            ),
            severity="HIGH"
        ))

    # ── Rule 2: Possible Structuring Risk ───────────────────────────────────
    #
    # A single transaction between ₹8 lakh and ₹10 lakh cannot establish
    # structuring. Structuring requires evidence of a pattern or intent.
    #
    # We therefore flag the amount as a review indicator only.

    if 800_000 <= amount < 1_000_000:
        findings.append(RuleViolation(
            rule_id="R002",
            rule_name="Near-Threshold Transaction Risk",
            regulation_source=(
                "PMLA 2002 — AML/CFT monitoring and suspicious transaction "
                "assessment"
            ),
            description=(
                f"Transaction of ₹{amount:,.0f} falls within a high-value "
                "near-threshold range. This may warrant review for possible "
                "structuring when considered together with transaction history "
                "and other customer activity. This transaction alone does not "
                "prove structuring."
            ),
            severity="HIGH"
        ))

    # ── Rule 3: Unusual-Time High-Value Transaction ──────────────────────────
    #
    # The dataset shows that overnight transactions are strongly associated
    # with the synthetic suspicious class. However, unusual transaction time
    # is a risk indicator, not by itself a regulatory violation.

    if amount > 500_000 and (hour < 5 or hour >= 23):
        findings.append(RuleViolation(
            rule_id="R003",
            rule_name="Unusual-Time High-Value Transaction",
            regulation_source=(
                "RBI KYC/AML and fraud-risk monitoring framework"
            ),
            description=(
                f"High-value transaction of ₹{amount:,.0f} occurred at "
                f"{hour:02d}:00. An unusual transaction time can be used as "
                "a monitoring signal and should be assessed together with "
                "customer history and other risk indicators."
            ),
            severity="MEDIUM"
        ))

    # ── Rule 4: KYC Compliance Risk ─────────────────────────────────────────
    #
    # RBI's KYC Master Direction contains requirements concerning KYC,
    # customer due diligence and restrictions/monitoring in cases of
    # non-compliance.
    #
    # Our dataset only tells us whether KYC is marked verified.
    # It does NOT contain enough information to establish the exact
    # circumstances of a legally restricted account.

    if not kyc_verified:
        findings.append(RuleViolation(
            rule_id="R004",
            rule_name="KYC Compliance Risk",
            regulation_source=(
                "RBI Master Direction – Know Your Customer (KYC)"
            ),
            description=(
                "The account is marked as not KYC-verified. The transaction "
                "should be reviewed against the applicable Customer Due "
                "Diligence and account-operation requirements. The available "
                "data does not establish a specific transaction-value "
                "prohibition."
            ),
            severity="HIGH"
        ))

    # ── Rule 5: Unusual Transaction Velocity ────────────────────────────────
    #
    # The dataset uses tx_count_7d as a behavioural feature.
    # More than 20 transactions is a project-defined anomaly threshold,
    # NOT a universal RBI legal threshold.

    if tx_count > 20:
        findings.append(RuleViolation(
            rule_id="R005",
            rule_name="Unusual Transaction Velocity",
            regulation_source=(
                "RBI fraud-risk monitoring principles"
            ),
            description=(
                f"Account recorded {tx_count} transactions in the last "
                "7 days. This exceeds the project's behavioural monitoring "
                "threshold and may indicate unusual activity requiring review. "
                "It is not, by itself, evidence of layering, fraud, or a "
                "regulatory violation."
            ),
            severity="MEDIUM"
        ))

    # ── Rule 6: Round-Number Risk Indicator ─────────────────────────────────
    #
    # Round transaction amounts can be useful as an AML/fraud risk signal,
    # but the amount alone does not establish suspicious activity.

    if amount >= 100_000 and amount % 100_000 == 0:
        findings.append(RuleViolation(
            rule_id="R006",
            rule_name="Round-Number Transaction Risk",
            regulation_source=(
                "AML/CFT transaction-monitoring risk indicators"
            ),
            description=(
                f"Transaction amount ₹{amount:,.0f} is an exact round-number "
                "amount. This can be used as a behavioural risk indicator "
                "when combined with other transaction characteristics, but "
                "does not by itself establish suspicious activity."
            ),
            severity="LOW"
        ))

    return findings


# ── Self-test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    test_cases = [
        (
            "Large transaction (₹12L)",
            {
                "amount": 1_200_000,
                "hour_of_day": 10,
                "tx_count_7d": 2,
                "kyc_verified": True
            },
            ["R001"]
        ),
        (
            "Near-threshold transaction (₹9.5L)",
            {
                "amount": 950_000,
                "hour_of_day": 14,
                "tx_count_7d": 3,
                "kyc_verified": True
            },
            ["R002"]
        ),
        (
            "High-value transaction at unusual time (₹6L at 2am)",
            {
                "amount": 600_000,
                "hour_of_day": 2,
                "tx_count_7d": 1,
                "kyc_verified": True
            },
            ["R003"]
        ),
        (
            "KYC compliance risk",
            {
                "amount": 100_000,
                "hour_of_day": 11,
                "tx_count_7d": 2,
                "kyc_verified": False
            },
            ["R004"]
        ),
        (
            "High transaction velocity",
            {
                "amount": 5_000,
                "hour_of_day": 9,
                "tx_count_7d": 25,
                "kyc_verified": True
            },
            ["R005"]
        ),
        (
            "Round-number transaction",
            {
                "amount": 500_000,
                "hour_of_day": 15,
                "tx_count_7d": 1,
                "kyc_verified": True
            },
            ["R006"]
        ),
    ]

    all_passed = True

    for desc, tx, expected_ids in test_cases:
        findings = check_rules(tx)
        found_ids = [finding.rule_id for finding in findings]

        passed = all(rule_id in found_ids for rule_id in expected_ids)

        status = "[PASS]" if passed else "[FAIL]"

        if not passed:
            all_passed = False

        print(f"{status} {desc}")

        for finding in findings:
            print(
                f"       → {finding.rule_id}: "
                f"{finding.rule_name} ({finding.severity})"
            )

    print()

    if all_passed:
        print("All tests passed ✓")
    else:
        print("Some tests FAILED — check above")