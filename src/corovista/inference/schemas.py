"""
CoroVista - Inference Data Contracts & Schemas
Core Inference Types & Threshold Contracts

Defines standardized data contracts for multi-target patient inference:
- Overall CAD (Cath): CAD vs Normal
- Vessel-level Stenosis: LAD, LCX, RCA (Stenotic vs Normal)
- Guarantees strict separation of continuous predicted risk probability
  and discrete classification thresholding.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

# Dataset standard target labels
TARGET_LABEL_MAP: Dict[str, Dict[int, str]] = {
    "cath": {1: "CAD", 0: "Normal"},
    "lad": {1: "Stenotic", 0: "Normal"},
    "lcx": {1: "Stenotic", 0: "Normal"},
    "rca": {1: "Stenotic", 0: "Normal"},
}

TARGET_KEY_MAP: Dict[str, str] = {
    "Cath": "cath",
    "LAD": "lad",
    "LCX": "lcx",
    "RCA": "rca",
}


class TargetPrediction(BaseModel):
    """Prediction outcome for a single coronary target."""
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Continuous predicted stenosis / CAD probability (controls 3D visual risk intensity).",
    )
    prediction: str = Field(
        ...,
        description="Discrete classification label ('CAD'/'Normal' or 'Stenotic'/'Normal').",
    )
    threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Decision threshold applied to probability to determine class label.",
    )
    model_family: Optional[str] = Field(
        default=None,
        description="Underlying predictive model family (e.g., 'XGBoost', 'LogisticRegression').",
    )
    calibration: Optional[str] = Field(
        default=None,
        description="Probability calibration method applied ('sigmoid' or 'uncalibrated').",
    )


class PatientInferenceResponse(BaseModel):
    """Complete four-target prediction response for a patient record."""
    cath: TargetPrediction = Field(..., description="Overall Coronary Artery Disease diagnosis.")
    lad: TargetPrediction = Field(..., description="Left Anterior Descending stenosis status.")
    lcx: TargetPrediction = Field(..., description="Left Circumflex stenosis status.")
    rca: TargetPrediction = Field(..., description="Right Coronary Artery stenosis status.")

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Converts response to exact API contract dictionary."""
        return {
            "cath": self.cath.model_dump(),
            "lad": self.lad.model_dump(),
            "lcx": self.lcx.model_dump(),
            "rca": self.rca.model_dump(),
        }
