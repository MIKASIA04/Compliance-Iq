from fastapi import FastAPI
from ml_service.predict import router as prediction_router
app = FastAPI(
    title="ComplianceIQ ML Service",
    description="Machine Learning Prediction Service",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "ComplianceIQ ML Service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
app.include_router(prediction_router)