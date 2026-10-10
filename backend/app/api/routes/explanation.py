"""
CoroVista Backend - Explanation Route
SHAP Feature Attribution Endpoint
"""

from fastapi import APIRouter
from backend.app.schemas.requests import ExplanationRequest
from backend.app.schemas.responses import ExplanationResponse
from backend.app.services.explanation_service import get_patient_explanation

router = APIRouter(tags=["Explainability"])


@router.post(
    "/explain",
    response_model=ExplanationResponse,
    summary="Patient-Level SHAP Feature Attribution",
    description=(
        "Computes localized feature importance in model log-odds (margin) space for a "
        "specified target (cath, lad, lcx, rca). Returns ranked feature attributions, "
        "top risk-elevating positive drivers, and top protective negative drivers."
    ),
)
def explain(request: ExplanationRequest) -> ExplanationResponse:
    """Computes patient-level SHAP explanation for the requested target."""
    return get_patient_explanation(patient_data=request.patient, target=request.target)
