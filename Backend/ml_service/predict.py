from fastapi import APIRouter

from ml_service.schemas import PredictionRequest, PredictionResponse

from ml_service.model_loader import model
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict transaction risk"
)
def predict(request: PredictionRequest):
    """
    Temporary prediction endpoint.

    This placeholder will be replaced with the trained ML model
    during the next stage.
    """
    result = model.predict(request)

    return PredictionResponse(**result)

     