from typing import Dict, List

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float
    transaction_type: str
    hour_of_day: int
    tx_count_7d: int
    kyc_verified: bool


class PredictionResponse(BaseModel):
    risk_level: str
    ml_probability: float
    rule_violations: List[Dict]
    shap_explanation: List[Dict]
    summary: str
    flagged: bool