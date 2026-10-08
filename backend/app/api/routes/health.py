"""
CoroVista Backend - Health Route
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

from fastapi import APIRouter, Response, status
from backend.app.core.config import settings
from backend.app.schemas.responses import HealthResponse
from src.corovista.inference.loader import load_all_models

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health & Model Status",
    description="Verifies API service status and confirms availability of all four serialized model pipelines.",
)
def get_health(response: Response) -> HealthResponse:
    """Verifies that the API service is operational and models are initialized."""
    try:
        models = load_all_models()
        all_loaded = len(models) == 4 and all(k in models for k in ["cath", "lad", "lcx", "rca"])
    except Exception:
        all_loaded = False

    if not all_loaded:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(
            status="degraded",
            service="corovista-api",
            version=settings.API_VERSION,
            models_loaded=False,
        )

    return HealthResponse(
        status="ok",
        service="corovista-api",
        version=settings.API_VERSION,
        models_loaded=True,
    )
