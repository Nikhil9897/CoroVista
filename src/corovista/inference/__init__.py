"""
CoroVista Inference Package
Stage 3: Inference Verification & Explainability
"""

from src.corovista.inference.loader import (
    clear_model_cache,
    load_all_models,
    load_model_pipeline,
)
from src.corovista.inference.predictor import predict_patient
from src.corovista.inference.schemas import (
    PatientInferenceResponse,
    TargetPrediction,
    TARGET_LABEL_MAP,
)
from src.corovista.inference.validation import validate_and_normalize_patient_input

__all__ = [
    "predict_patient",
    "load_all_models",
    "load_model_pipeline",
    "clear_model_cache",
    "validate_and_normalize_patient_input",
    "PatientInferenceResponse",
    "TargetPrediction",
    "TARGET_LABEL_MAP",
]
