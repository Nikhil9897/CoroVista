"""
CoroVista Backend - Response Schemas
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==========================================
# 1. Health & Status
# ==========================================
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status ('ok', 'degraded')")
    service: str = Field(default="corovista-api", description="Service identifier")
    version: str = Field(..., description="API software version")
    models_loaded: bool = Field(..., description="Whether all four model artifacts are initialized")


# ==========================================
# 2. Model Metadata
# ==========================================
class ModelMetadataItem(BaseModel):
    target: str = Field(..., description="Target name ('cath', 'lad', 'lcx', 'rca')")
    model: str = Field(..., description="Machine learning algorithm family (e.g., 'XGBoost', 'LogisticRegression')")
    calibrated: bool = Field(..., description="Whether probability calibration is applied")
    calibration: str = Field(..., description="Calibration method (e.g., 'Platt/Sigmoid', 'Uncalibrated')")
    threshold: float = Field(..., description="Decision threshold applied to risk probability")
    positive_label: str = Field(..., description="Class name for positive classification ('CAD' or 'Stenotic')")
    negative_label: str = Field(..., description="Class name for negative classification ('Normal')")
    explanation_space: str = Field(..., description="Mathematical space in which SHAP attributions operate")
    version: Optional[str] = Field(default="1.0.0", description="Model artifact version")


class ModelsResponse(BaseModel):
    models: List[ModelMetadataItem] = Field(..., description="List of final locked models")


# ==========================================
# 3. Clinical Feature Metadata
# ==========================================
class FeatureRange(BaseModel):
    min: float = Field(..., description="Minimum permitted input value")
    max: float = Field(..., description="Maximum permitted input value")
    step: Optional[float] = Field(default=1.0, description="Recommended UI input step")


class FeatureMetadataItem(BaseModel):
    machine_name: str = Field(..., description="Internal variable name (e.g. 'EF-TTE', 'Sex')")
    human_readable_label: str = Field(..., description="Clinical title with units (e.g. 'Ejection Fraction (% Echo)')")
    type: str = Field(..., description="Data type category: 'numeric', 'binary', or 'categorical'")
    category: str = Field(..., description="Clinical category: 'Demographic', 'Symptoms / Examination', 'ECG', 'Laboratory / Echo'")
    allowed_values: Optional[List[str]] = Field(default=None, description="Permitted string options if categorical")
    dataset_observed_range: Optional[str] = Field(default=None, description="Observed values in Z-Alizadeh Sani cohort")
    simulator_validation_range: Optional[FeatureRange] = Field(default=None, description="Permissible input bounds for simulator")
    is_required: bool = Field(default=True, description="Whether the feature is strictly required")
    description: Optional[str] = Field(default=None, description="Clinical significance and measurement notes")


class FeaturesResponse(BaseModel):
    features: List[FeatureMetadataItem] = Field(..., description="Clinical feature registry for Patient Simulator")
    total_features: int = Field(..., description="Total count of eligible features")


# ==========================================
# 4. Target Prediction
# ==========================================
class TargetPredictionItem(BaseModel):
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Continuous predicted stenosis/CAD probability (drives 3D risk visualization).",
    )
    prediction: str = Field(
        ...,
        description="Binary decision label ('CAD'/'Normal' for Cath; 'Stenotic'/'Normal' for vessels).",
    )
    threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Decision threshold applied to probability.",
    )
    model_family: Optional[str] = Field(default=None, description="Model algorithm")
    calibration: Optional[str] = Field(default=None, description="Probability calibration method")


class PredictionResponse(BaseModel):
    predictions: Dict[str, TargetPredictionItem] = Field(
        ...,
        description="Dictionary containing prediction items for 'cath', 'lad', 'lcx', and 'rca'.",
    )


# ==========================================
# 5. SHAP Explanation
# ==========================================
class FeatureContributionItem(BaseModel):
    feature: str = Field(..., description="Feature variable name")
    label: str = Field(..., description="Human-readable clinical label and unit")
    value: float = Field(..., description="Patient's actual or transformed feature value")
    shap_value: float = Field(..., description="Local SHAP attribution score (in log-odds / model margin space)")
    direction: str = Field(..., description="'positive' (elevates risk) or 'negative' (protective/lowers risk)")


class ExplanationResponse(BaseModel):
    target: str = Field(..., description="Target artery/diagnosis explained ('cath', 'lad', 'lcx', 'rca')")
    explanation_space: str = Field(default="log-odds (model score)", description="Mathematical space of SHAP values")
    calibration_disclosure: str = Field(..., description="Calibration relationship statement")
    base_value: float = Field(..., description="Cohort expected value in model margin space")
    features: List[FeatureContributionItem] = Field(..., description="All feature contributions ranked by absolute SHAP")
    positive_contributors: List[FeatureContributionItem] = Field(..., description="Top drivers elevating risk")
    negative_contributors: List[FeatureContributionItem] = Field(..., description="Top protective/risk-reducing factors")


# ==========================================
# 6. Combined Patient Analysis
# ==========================================
class AnalysisResponse(BaseModel):
    predictions: Dict[str, TargetPredictionItem] = Field(..., description="Predictions for all 4 targets")
    explanations: Dict[str, ExplanationResponse] = Field(..., description="SHAP explanations for all 4 targets")
    clinical_disclaimer: str = Field(..., description="Clinical safety and educational use notice")
    visualization_note: str = Field(..., description="Boundary notice: predicted risk vs 3D physical coordinates")
