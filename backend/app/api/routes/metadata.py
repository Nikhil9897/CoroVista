"""
CoroVista Backend - Metadata Routes
Features & Model Architecture Endpoints
"""

from fastapi import APIRouter
from backend.app.schemas.responses import FeaturesResponse, ModelsResponse
from backend.app.services.metadata_service import get_features_metadata, get_models_metadata

router = APIRouter(tags=["Metadata"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="Model Inventory & Threshold Metadata",
    description=(
        "Returns architecture, calibration status, decision thresholds, and positive/negative "
        "class labels for all four locked prediction models (Cath, LAD, LCX, RCA)."
    ),
)
def get_models() -> ModelsResponse:
    """Returns metadata for the four locked prediction models."""
    return get_models_metadata()


@router.get(
    "/features",
    response_model=FeaturesResponse,
    summary="Clinical Feature Registry for Patient Simulator",
    description=(
        "Returns the clinical feature registry with machine names, human-readable labels, units, "
        "clinical domains, observed cohort ranges, and simulator input validation ranges. "
        "Target columns are strictly excluded."
    ),
)
def get_features() -> FeaturesResponse:
    """Returns clinical feature registry for Patient Simulator."""
    return get_features_metadata()
