import httpx

ML_SERVICE_URL = "http://127.0.0.1:8001/predict"


async def call_ml_pipeline(transaction_data: dict) -> dict:
    """
    Sends a transaction to the ML Service and returns its prediction.
    """

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                ML_SERVICE_URL,
                json=transaction_data,
            )

            response.raise_for_status()
            return response.json()

    except Exception as e:
        return {
            "risk_level": "UNKNOWN",
            "ml_probability": 0.0,
            "rule_violations": [],
            "shap_explanation": [],
            "summary": f"ML Service unavailable: {str(e)}",
            "flagged": False,
        }