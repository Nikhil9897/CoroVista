"""
CoroVista Backend - Prediction & Patient Analysis Routes
Multi-Target Inference Endpoints
"""

from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.schemas.requests import AnalysisRequest, PredictionRequest
from backend.app.schemas.responses import (
    AnalysisResponse,
    ExplanationResponse,
    PredictionResponse,
)
from backend.app.services.explanation_service import get_patient_explanation
from backend.app.services.prediction_service import get_patient_predictions

router = APIRouter(tags=["Prediction & Analysis"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Multi-Target Coronary Risk Prediction",
    description=(
        "Performs deterministic multi-target inference on patient clinical features. "
        "Returns continuous risk probabilities and thresholded classifications for "
        "overall CAD (Cath), LAD, LCX, and RCA stenosis."
    ),
)
def predict(request: PredictionRequest) -> PredictionResponse:
    """Computes predictions across all 4 targets for a single patient."""
    return get_patient_predictions(request.patient)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Comprehensive Patient Assessment (Prediction + 4-Target SHAP)",
    description=(
        "Primary dashboard analysis endpoint. Evaluates all four models and extracts "
        "local SHAP model-score explanations (top drivers and full feature ranking) "
        "along with mandatory clinical and 3D visualization disclaimers."
    ),
)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Orchestrates multi-target prediction and comprehensive SHAP explanations."""
    predictions_res = get_patient_predictions(request.patient)

    targets = ["cath", "lad", "lcx", "rca"]
    explanations_dict = {}
    for t in targets:
        exp_res = get_patient_explanation(request.patient, target=t)
        explanations_dict[t] = exp_res

    return AnalysisResponse(
        predictions=predictions_res.predictions,
        explanations=explanations_dict,
        clinical_disclaimer=settings.CLINICAL_DISCLAIMER,
        visualization_note=settings.VISUALIZATION_NOTE,
    )
