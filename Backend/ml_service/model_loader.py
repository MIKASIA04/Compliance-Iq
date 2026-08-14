"""
Temporary model loader.

This is a placeholder ML model.

It returns responses in the same format expected by
the ComplianceIQ backend. Later this can be replaced
with a real trained model loaded via joblib/pickle.
"""


class FraudDetectionModel:

    def predict(self, transaction):
        """
        Simulate ML prediction.

        Returns:
            risk_level
            ml_probability
            rule_violations
            shap_explanation
            summary
            flagged
        """

        # Use the same field your backend sends
        kyc_verified = getattr(transaction, "kyc_verified", True)

        if transaction.amount > 500000 and not kyc_verified:
            return {
                "risk_level": "HIGH",
                "ml_probability": 0.92,
                "rule_violations": [
                    {
                        "rule_id": "ML001",
                        "rule_name": "High Value Unverified Transaction",
                        "regulation_source": "RBI KYC Master Direction",
                        "description": "High-value transfer involving an unverified account.",
                        "severity": "HIGH",
                    }
                ],
                "shap_explanation": [
                    {
                        "feature_name": "amount",
                        "display_name": "Transaction Amount",
                        "value": transaction.amount,
                        "contribution": 0.82,
                        "direction": "increases_risk",
                    },
                    {
                        "feature_name": "kyc_verified",
                        "display_name": "KYC Status",
                        "value": int(kyc_verified),
                        "contribution": 0.64,
                        "direction": "increases_risk",
                    },
                ],
                "summary": (
                    "High-value transaction involving an "
                    "unverified account. Manual review recommended."
                ),
                "flagged": True,
            }

        return {
            "risk_level": "LOW",
            "ml_probability": 0.15,
            "rule_violations": [],
            "shap_explanation": [
                {
                    "feature_name": "amount",
                    "display_name": "Transaction Amount",
                    "value": transaction.amount,
                    "contribution": 0.12,
                    "direction": "decreases_risk",
                }
            ],
            "summary": "No significant fraud indicators detected.",
            "flagged": False,
        }


model = FraudDetectionModel()