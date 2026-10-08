"""
CoroVista Backend - Explanation Service
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

from typing import Any, Dict
from backend.app.core.errors import InvalidInputError, InvalidTargetError, ModelUnavailableError
from backend.app.schemas.responses import (
    ExplanationResponse,
    FeatureContributionItem,
)
from src.corovista.explainability.patient_explanations import (
    explain_patient,
    top_negative_contributors,
    top_positive_contributors,
)

VALID_TARGETS = {"cath", "lad", "lcx", "rca"}


def get_patient_explanation(
    patient_data: Dict[str, Any],
    target: str = "cath",
    max_features: int = 57,
) -> ExplanationResponse:
    """
    Computes patient-level SHAP explanation for a specified coronary target.

    Parameters:
    -----------
    patient_data: Dictionary of patient clinical features.
    target: One of 'cath', 'lad', 'lcx', 'rca'.
    max_features: Maximum number of ranked feature items to return.

    Returns:
    --------
    ExplanationResponse: Structured explanation payload.
    """
    t_clean = target.lower().strip()
    if t_clean not in VALID_TARGETS:
        raise InvalidTargetError(target=target)

    try:
        raw_explanation = explain_patient(patient_data, target=t_clean, max_features=max_features)
    except ValueError as e:
        raise InvalidInputError(message=str(e))
    except FileNotFoundError as e:
        raise ModelUnavailableError(message=f"Model artifact unavailable: {str(e)}")

    features = [
        FeatureContributionItem(
            feature=f["feature"],
            label=f["label"],
            value=f["value"],
            shap_value=f["shap_value"],
            direction=f["direction"],
        )
        for f in raw_explanation["features"]
    ]

    raw_pos = top_positive_contributors(raw_explanation, n=5)
    pos_items = [
        FeatureContributionItem(
            feature=f["feature"],
            label=f["label"],
            value=f["value"],
            shap_value=f["shap_value"],
            direction=f["direction"],
        )
        for f in raw_pos
    ]

    raw_neg = top_negative_contributors(raw_explanation, n=5)
    neg_items = [
        FeatureContributionItem(
            feature=f["feature"],
            label=f["label"],
            value=f["value"],
            shap_value=f["shap_value"],
            direction=f["direction"],
        )
        for f in raw_neg
    ]

    calibration_disclosure = (
        raw_explanation.get("calibration_note")
        or raw_explanation.get("calibration_disclosure")
        or "SHAP values explain the underlying predictive model score (log-odds/margin); probability calibration is applied separately to determine the final visual risk probability."
    )

    return ExplanationResponse(
        target=t_clean,
        explanation_space=raw_explanation["explanation_space"],
        calibration_disclosure=calibration_disclosure,
        base_value=raw_explanation["base_value"],
        features=features,
        positive_contributors=pos_items,
        negative_contributors=neg_items,
    )
