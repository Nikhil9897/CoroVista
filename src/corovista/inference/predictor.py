"""
CoroVista - Multi-Target Predictor Engine
Stage 3: Inference Verification & Explainability

Executes deterministic multi-target inference on validated patient data:
- Evaluates Cath, LAD, LCX, RCA pipelines independently.
- Strictly separates continuous predicted risk probability and discrete thresholded prediction.
- Guarantees target-specific label mapping ('CAD'/'Normal' for Cath; 'Stenotic'/'Normal' for vessels).
"""

from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd

from src.corovista.inference.loader import load_all_models, load_model_pipeline
from src.corovista.inference.schemas import (
    PatientInferenceResponse,
    TargetPrediction,
    TARGET_LABEL_MAP,
)
from src.corovista.inference.validation import validate_and_normalize_patient_input


def predict_patient(
    patient_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    return_dict: bool = False,
) -> Union[PatientInferenceResponse, Dict[str, Dict[str, Any]]]:
    """
    Performs inference across all four coronary targets for a single patient record.

    Parameters:
    -----------
    patient_data: Raw feature dictionary, Series, or 1-row DataFrame.
    return_dict: If True, returns pure Python dictionary matching JSON API specification.

    Returns:
    --------
    PatientInferenceResponse or Dict[str, Dict[str, Any]]: Structured four-target prediction.
    """
    # 1. Validate and normalize input schema & prevent target leakage
    clean_df = validate_and_normalize_patient_input(patient_data)

    # 2. Load all model pipelines
    models = load_all_models()

    predictions = {}
    for target_key in ["cath", "lad", "lcx", "rca"]:
        model_info = models[target_key]
        pipeline = model_info["pipeline"]
        threshold = model_info["threshold"]
        model_family = model_info["model_family"]
        calibration = model_info["calibration"]

        # Run pipeline predict_proba (includes preprocessing steps inside pipeline)
        raw_prob_array = pipeline.predict_proba(clean_df)
        prob = float(raw_prob_array[0, 1])

        # Apply target-specific decision threshold
        is_positive = int(prob >= threshold)
        class_label = TARGET_LABEL_MAP[target_key][is_positive]

        predictions[target_key] = TargetPrediction(
            probability=round(prob, 4),
            prediction=class_label,
            threshold=threshold,
            model_family=model_family,
            calibration=calibration,
        )

    response = PatientInferenceResponse(
        cath=predictions["cath"],
        lad=predictions["lad"],
        lcx=predictions["lcx"],
        rca=predictions["rca"],
    )

    if return_dict:
        return response.to_dict()
    return response
