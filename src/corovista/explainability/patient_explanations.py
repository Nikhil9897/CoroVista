"""
CoroVista - Patient-Level SHAP Explanation Service
Patient Risk Attribution in Log-Odds Space

Generates structured, human-interpretable patient explanations for any of the four targets:
- Top positive contributors (factors elevating risk)
- Top negative contributors (factors protective or lowering risk)
- Human-readable clinical labels and units
- Explicit disclosure of explanation space (log-odds / model score)
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from src.corovista.explainability.explainers import get_target_explainer
from src.corovista.explainability.feature_mapping import get_human_label
from src.corovista.inference.validation import validate_and_normalize_patient_input


def explain_patient(
    patient_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    target: str = "cath",
    max_features: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Computes a localized, ranked SHAP explanation for an individual patient.

    Parameters:
    -----------
    patient_data: Raw patient clinical feature dictionary or record.
    target: One of 'cath', 'lad', 'lcx', 'rca' (case-insensitive).
    max_features: Optional limit on the number of returned feature items (defaults to all 57).

    Returns:
    --------
    Dict[str, Any]: JSON-compatible explanation dictionary structured for frontend cards.
    """
    t_clean = target.lower().strip()
    clean_df = validate_and_normalize_patient_input(patient_data)

    explainer = get_target_explainer(t_clean)
    shap_vals_matrix, base_value = explainer.explain(clean_df)

    shap_vals = shap_vals_matrix[0]
    feature_names = explainer.feature_names
    transformed_row = explainer.transform_features(clean_df)[0]

    feature_items: List[Dict[str, Any]] = []

    for idx, f_name in enumerate(feature_names):
        val = float(shap_vals[idx])
        feature_val = float(transformed_row[idx])
        direction = "positive" if val >= 0 else "negative"

        feature_items.append({
            "feature": f_name,
            "label": get_human_label(f_name),
            "value": round(feature_val, 3),
            "shap_value": round(val, 4),
            "abs_shap": abs(val),
            "direction": direction,
        })

    # Sort strictly by absolute impact descending
    feature_items.sort(key=lambda x: x["abs_shap"], reverse=True)

    # Clean internal sort key
    for item in feature_items:
        del item["abs_shap"]

    if max_features is not None and max_features > 0:
        feature_items = feature_items[:max_features]

    return {
        "target": t_clean,
        "explanation_space": explainer.explanation_space,
        "calibration_note": (
            "SHAP values explain the underlying predictive model score (log-odds/margin); "
            "probability calibration is applied separately to determine the final visual risk probability."
        ),
        "base_value": round(float(base_value), 4),
        "model_family": explainer.model_family,
        "calibration_method": explainer.calibration_method,
        "features": feature_items,
    }


def top_positive_contributors(
    explanation_result: Dict[str, Any],
    n: int = 5,
) -> List[Dict[str, Any]]:
    """Filters top positive contributors (factors elevating stenosis risk)."""
    pos = [f for f in explanation_result["features"] if f["shap_value"] > 0]
    pos.sort(key=lambda x: x["shap_value"], reverse=True)
    return pos[:n]


def top_negative_contributors(
    explanation_result: Dict[str, Any],
    n: int = 5,
) -> List[Dict[str, Any]]:
    """Filters top negative contributors (factors reducing / protective against stenosis risk)."""
    neg = [f for f in explanation_result["features"] if f["shap_value"] < 0]
    neg.sort(key=lambda x: x["shap_value"])  # Most negative first
    return neg[:n]
