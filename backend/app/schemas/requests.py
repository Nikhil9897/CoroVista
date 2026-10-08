"""
CoroVista Backend - Request Schemas
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class PatientDataPayload(BaseModel):
    """Raw clinical input features for a single patient."""
    patient: Dict[str, Any] = Field(
        ...,
        description="Dictionary mapping clinical feature names to values (e.g. Age, Sex, BMI, EF-TTE).",
        json_schema_extra={
            "example": {
                "Age": 62,
                "Sex": "Male",
                "Weight": 78,
                "Length": 172,
                "BMI": 26.37,
                "DM": 1,
                "HTN": 1,
                "Current Smoker": 0,
                "EX-Smoker": 1,
                "FH": 0,
                "Obesity": "Y",
                "CRF": "N",
                "CVA": "N",
                "Airway disease": "N",
                "Thyroid Disease": "N",
                "CHF": "N",
                "DLP": "Y",
                "BP": 135,
                "PR": 76,
                "Edema": 0,
                "Weak Peripheral Pulse": "N",
                "Lung rales": "N",
                "Systolic Murmur": "N",
                "Diastolic Murmur": "N",
                "Typical Chest Pain": 1,
                "Dyspnea": "N",
                "Function Class": 2,
                "Atypical": "N",
                "Nonanginal": "N",
                "LowTH Ang": "N",
                "Q Wave": 0,
                "St Elevation": 0,
                "St Depression": 1,
                "Tinversion": 1,
                "LVH": "N",
                "Poor R Progression": "N",
                "BBB": "N",
                "FBS": 126,
                "CR": 1.1,
                "TG": 195,
                "LDL": 142,
                "HDL": 38,
                "BUN": 18,
                "ESR": 14,
                "HB": 14.5,
                "K": 4.4,
                "Na": 140,
                "WBC": 7200,
                "Lymph": 30,
                "Neut": 65,
                "PLT": 230,
                "EF-TTE": 45,
                "Region RWMA": 1,
                "VHD": "Mild"
            }
        }
    )


class PredictionRequest(PatientDataPayload):
    """Request payload for multi-target coronary prediction."""
    pass


class ExplanationRequest(PatientDataPayload):
    """Request payload for single-target SHAP explanation."""
    target: str = Field(
        default="cath",
        description="Target to explain: 'cath' (overall CAD), 'lad', 'lcx', or 'rca'.",
        json_schema_extra={"example": "cath"},
    )


class AnalysisRequest(PatientDataPayload):
    """Request payload for combined four-target prediction and SHAP analysis."""
    pass
