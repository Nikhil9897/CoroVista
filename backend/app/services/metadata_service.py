"""
CoroVista Backend - Metadata Service
Feature & Model Registry Metadata Provider
"""

from typing import Any, Dict, List, Optional
from backend.app.core.errors import ModelUnavailableError
from backend.app.schemas.responses import (
    FeatureMetadataItem,
    FeatureRange,
    FeaturesResponse,
    ModelMetadataItem,
    ModelsResponse,
)
from ml.preprocessing.feature_metadata import (
    ELIGIBLE_FEATURES,
    FEATURE_REGISTRY,
    TARGET_COLUMNS,
)
from src.corovista.explainability.feature_mapping import get_human_label
from src.corovista.inference.loader import load_all_models
from src.corovista.inference.schemas import TARGET_LABEL_MAP

# Canonical project categories
CATEGORY_MAP: Dict[str, str] = {
    # Demographic
    "Age": "Demographic",
    "Weight": "Demographic",
    "Length": "Demographic",
    "Sex": "Demographic",
    "BMI": "Demographic",

    # Symptoms / Examination
    "DM": "Symptoms / Examination",
    "HTN": "Symptoms / Examination",
    "Current Smoker": "Symptoms / Examination",
    "EX-Smoker": "Symptoms / Examination",
    "FH": "Symptoms / Examination",
    "Obesity": "Symptoms / Examination",
    "CRF": "Symptoms / Examination",
    "CVA": "Symptoms / Examination",
    "Airway disease": "Symptoms / Examination",
    "Thyroid Disease": "Symptoms / Examination",
    "CHF": "Symptoms / Examination",
    "DLP": "Symptoms / Examination",
    "BP": "Symptoms / Examination",
    "PR": "Symptoms / Examination",
    "Edema": "Symptoms / Examination",
    "Weak Peripheral Pulse": "Symptoms / Examination",
    "Lung rales": "Symptoms / Examination",
    "Systolic Murmur": "Symptoms / Examination",
    "Diastolic Murmur": "Symptoms / Examination",
    "Typical Chest Pain": "Symptoms / Examination",
    "Dyspnea": "Symptoms / Examination",
    "Function Class": "Symptoms / Examination",
    "Atypical": "Symptoms / Examination",
    "Nonanginal": "Symptoms / Examination",
    "Exertional CP": "Symptoms / Examination",
    "LowTH Ang": "Symptoms / Examination",

    # ECG
    "Q Wave": "ECG",
    "St Elevation": "ECG",
    "St Depression": "ECG",
    "Tinversion": "ECG",
    "LVH": "ECG",
    "Poor R Progression": "ECG",
    "BBB": "ECG",

    # Laboratory / Echo
    "FBS": "Laboratory / Echo",
    "CR": "Laboratory / Echo",
    "TG": "Laboratory / Echo",
    "LDL": "Laboratory / Echo",
    "HDL": "Laboratory / Echo",
    "BUN": "Laboratory / Echo",
    "ESR": "Laboratory / Echo",
    "HB": "Laboratory / Echo",
    "K": "Laboratory / Echo",
    "Na": "Laboratory / Echo",
    "WBC": "Laboratory / Echo",
    "Lymph": "Laboratory / Echo",
    "Neut": "Laboratory / Echo",
    "PLT": "Laboratory / Echo",
    "EF-TTE": "Laboratory / Echo",
    "Region RWMA": "Laboratory / Echo",
    "VHD": "Laboratory / Echo",
}

# Medically plausible simulator input ranges (distinct from observed dataset ranges)
SIMULATOR_RANGES: Dict[str, FeatureRange] = {
    "Age": FeatureRange(min=18.0, max=100.0, step=1.0),
    "Weight": FeatureRange(min=30.0, max=200.0, step=1.0),
    "Length": FeatureRange(min=120.0, max=220.0, step=1.0),
    "BMI": FeatureRange(min=14.0, max=60.0, step=0.1),
    "BP": FeatureRange(min=70.0, max=240.0, step=1.0),
    "PR": FeatureRange(min=40.0, max=180.0, step=1.0),
    "FBS": FeatureRange(min=40.0, max=500.0, step=1.0),
    "CR": FeatureRange(min=0.2, max=15.0, step=0.1),
    "TG": FeatureRange(min=20.0, max=1000.0, step=1.0),
    "LDL": FeatureRange(min=20.0, max=400.0, step=1.0),
    "HDL": FeatureRange(min=10.0, max=120.0, step=1.0),
    "BUN": FeatureRange(min=4.0, max=150.0, step=1.0),
    "ESR": FeatureRange(min=1.0, max=120.0, step=1.0),
    "HB": FeatureRange(min=5.0, max=22.0, step=0.1),
    "K": FeatureRange(min=2.0, max=8.0, step=0.1),
    "Na": FeatureRange(min=110.0, max=160.0, step=1.0),
    "WBC": FeatureRange(min=1000.0, max=30000.0, step=100.0),
    "Lymph": FeatureRange(min=5.0, max=90.0, step=1.0),
    "Neut": FeatureRange(min=10.0, max=95.0, step=1.0),
    "PLT": FeatureRange(min=20.0, max=1000.0, step=1.0),
    "EF-TTE": FeatureRange(min=10.0, max=80.0, step=1.0),
    "Region RWMA": FeatureRange(min=0.0, max=4.0, step=1.0),
    "Function Class": FeatureRange(min=0.0, max=3.0, step=1.0),
}


def get_models_metadata() -> ModelsResponse:
    """
    Returns public metadata for the four locked prediction models.
    Does NOT leak internal filesystem paths.
    """
    try:
        models = load_all_models()
    except Exception as e:
        raise ModelUnavailableError(message=f"Model artifacts unavailable: {str(e)}")

    items: List[ModelMetadataItem] = []
    target_order = ["cath", "lad", "lcx", "rca"]

    for target in target_order:
        info = models[target]
        model_family = info.get("model_family", "Unknown")
        calibration = info.get("calibration", "uncalibrated")
        is_calibrated = calibration in ["sigmoid", "isotonic"]
        calib_label = "Platt/Sigmoid" if is_calibrated else "Uncalibrated"
        threshold = float(info.get("threshold", 0.5))

        pos_label = TARGET_LABEL_MAP[target][1]
        neg_label = TARGET_LABEL_MAP[target][0]

        items.append(
            ModelMetadataItem(
                target=target,
                model=model_family,
                calibrated=is_calibrated,
                calibration=calib_label,
                threshold=threshold,
                positive_label=pos_label,
                negative_label=neg_label,
                explanation_space="log-odds (model score)",
                version="1.0.0",
            )
        )

    return ModelsResponse(models=items)


def get_features_metadata() -> FeaturesResponse:
    """
    Returns clinical feature metadata registry for the Patient Simulator UI.
    Explicitly excludes target columns (Cath, LAD, LCX, RCA).
    """
    items: List[FeatureMetadataItem] = []

    for name in ELIGIBLE_FEATURES:
        if name in TARGET_COLUMNS:
            continue

        raw_meta = FEATURE_REGISTRY.get(name)
        category = CATEGORY_MAP.get(name, "Symptoms / Examination")
        label = get_human_label(name)

        # Classify data type & allowed values
        if name == "Sex":
            f_type = "categorical"
            allowed_vals = ["Male", "Female"]
        elif name == "VHD":
            f_type = "categorical"
            allowed_vals = ["Normal", "Mild", "Moderate", "Severe"]
        elif name == "BBB":
            f_type = "categorical"
            allowed_vals = ["N", "LBBB", "RBBB"]
        elif name in [
            "DM", "HTN", "Current Smoker", "EX-Smoker", "FH", "Edema",
            "Typical Chest Pain", "Q Wave", "St Elevation", "St Depression",
            "Tinversion",
        ]:
            f_type = "binary"
            allowed_vals = ["0", "1"]
        elif name in [
            "Obesity", "CRF", "CVA", "Airway disease", "Thyroid Disease",
            "CHF", "DLP", "Weak Peripheral Pulse", "Lung rales", "Systolic Murmur",
            "Diastolic Murmur", "Dyspnea", "Atypical", "Nonanginal", "LowTH Ang",
            "LVH", "Poor R Progression", "Exertional CP"
        ]:
            f_type = "binary"
            allowed_vals = ["Y", "N"]
        else:
            f_type = "numeric"
            allowed_vals = None

        observed_range = raw_meta.observed_range_or_values if raw_meta else None
        description = raw_meta.source_description if raw_meta else label
        sim_range = SIMULATOR_RANGES.get(name)

        items.append(
            FeatureMetadataItem(
                machine_name=name,
                human_readable_label=label,
                type=f_type,
                category=category,
                allowed_values=allowed_vals,
                dataset_observed_range=observed_range,
                simulator_validation_range=sim_range,
                is_required=True,
                description=description,
            )
        )

    return FeaturesResponse(features=items, total_features=len(items))
