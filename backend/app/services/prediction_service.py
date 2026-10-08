"""
CoroVista Backend - Prediction Service
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

from typing import Any, Dict
from backend.app.core.errors import InvalidInputError, ModelUnavailableError
from backend.app.schemas.responses import PredictionResponse, TargetPredictionItem
from src.corovista.inference.predictor import predict_patient
from src.corovista.inference.schemas import PatientInferenceResponse


def get_patient_predictions(patient_data: Dict[str, Any]) -> PredictionResponse:
    """
    Executes multi-target prediction using the Stage 3 verified inference engine.

    Parameters:
    -----------
    patient_data: Raw dictionary of patient clinical features.

    Returns:
    --------
    PredictionResponse: Structured predictions for Cath, LAD, LCX, and RCA.
    """
    try:
        response: PatientInferenceResponse = predict_patient(patient_data)
    except ValueError as e:
        raise InvalidInputError(message=str(e))
    except FileNotFoundError as e:
        raise ModelUnavailableError(message=f"Model artifact unavailable: {str(e)}")

    predictions_dict = {
        "cath": TargetPredictionItem(
            probability=response.cath.probability,
            prediction=response.cath.prediction,
            threshold=response.cath.threshold,
            model_family=response.cath.model_family,
            calibration=response.cath.calibration,
        ),
        "lad": TargetPredictionItem(
            probability=response.lad.probability,
            prediction=response.lad.prediction,
            threshold=response.lad.threshold,
            model_family=response.lad.model_family,
            calibration=response.lad.calibration,
        ),
        "lcx": TargetPredictionItem(
            probability=response.lcx.probability,
            prediction=response.lcx.prediction,
            threshold=response.lcx.threshold,
            model_family=response.lcx.model_family,
            calibration=response.lcx.calibration,
        ),
        "rca": TargetPredictionItem(
            probability=response.rca.probability,
            prediction=response.rca.prediction,
            threshold=response.rca.threshold,
            model_family=response.rca.model_family,
            calibration=response.rca.calibration,
        ),
    }

    return PredictionResponse(predictions=predictions_dict)
