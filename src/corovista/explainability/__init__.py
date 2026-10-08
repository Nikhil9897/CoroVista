"""
CoroVista Explainability Package
Stage 3: Inference Verification & Explainability
"""

from src.corovista.explainability.explainers import (
    TargetExplainer,
    get_target_explainer,
)
from src.corovista.explainability.feature_mapping import (
    FEATURE_LABEL_MAP,
    get_feature_description,
    get_human_label,
)
from src.corovista.explainability.global_explanations import compute_global_explanations
from src.corovista.explainability.patient_explanations import (
    explain_patient,
    top_negative_contributors,
    top_positive_contributors,
)

__all__ = [
    "explain_patient",
    "compute_global_explanations",
    "get_target_explainer",
    "TargetExplainer",
    "get_human_label",
    "get_feature_description",
    "FEATURE_LABEL_MAP",
    "top_positive_contributors",
    "top_negative_contributors",
]
