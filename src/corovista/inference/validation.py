"""
CoroVista - Input Feature Validation & Normalization Service
Leak-Safe Preprocessing & Categorical Cleaning Contracts

Validates patient input records before inference:
1. Target Leakage Prevention: Strictly rejects 'Cath', 'LAD', 'LCX', 'RCA'.
2. Required Feature Completeness: Ensures all eligible clinical features are present.
3. Categorical Normalization:
   - 'Fmale' -> 'Female'
   - Inconsistent VHD casing -> 'Normal', 'Mild', 'Moderate', 'Severe'
   - Binary string variants ('Yes'/'No', 'Y'/'N', 1/0)
4. Numerical Validation: Validates numerical coercibility while distinguishing
   dataset replication validation from flexible simulator ranges.
"""

from typing import Any, Dict, List, Set, Union
import numpy as np
import pandas as pd

from ml.preprocessing.feature_metadata import (
    ELIGIBLE_FEATURES,
    TARGET_COLUMNS,
    ZERO_VARIANCE_COLUMNS,
)

# Canonical normalization maps
SEX_NORMALIZATION_MAP = {
    "Male": "Male",
    "male": "Male",
    "M": "Male",
    "Fmale": "Female",
    "Female": "Female",
    "female": "Female",
    "F": "Female",
}

VHD_NORMALIZATION_MAP = {
    "N": "Normal",
    "Normal": "Normal",
    "normal": "Normal",
    "mild": "Mild",
    "Mild": "Mild",
    "Moderate": "Moderate",
    "moderate": "Moderate",
    "Severe": "Severe",
    "severe": "Severe",
}

BINARY_STRING_MAP = {
    "Y": "Y", "YES": "Y", "1": "Y", 1: "Y", True: "Y",
    "N": "N", "NO": "N", "0": "N", 0: "N", False: "N",
}

FORBIDDEN_TARGET_NAMES: Set[str] = {
    "Cath", "LAD", "LCX", "RCA",
    "cath", "lad", "lcx", "rca",
    "CATH",
}


def validate_and_normalize_patient_input(
    patient_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    allow_missing_zero_variance: bool = True,
) -> pd.DataFrame:
    """
    Validates and standardizes a single patient record into a 1-row DataFrame.

    Parameters:
    -----------
    patient_data: Dictionary, Series, or DataFrame containing patient clinical features.
    allow_missing_zero_variance: If True, automatically populates 'Exertional CP' with 'N'.

    Returns:
    --------
    pd.DataFrame: 1-row DataFrame with normalized features ready for pipeline.
    """
    # 1. Convert input to standard dictionary
    if isinstance(patient_data, pd.DataFrame):
        if len(patient_data) == 0:
            raise ValueError("Input DataFrame is empty.")
        raw_dict = patient_data.iloc[0].to_dict()
    elif isinstance(patient_data, pd.Series):
        raw_dict = patient_data.to_dict()
    elif isinstance(patient_data, dict):
        raw_dict = dict(patient_data)
    else:
        raise TypeError(f"Unsupported input type for patient data: {type(patient_data)}")

    # 2. Strict Target Leakage Check
    leaked_targets = [col for col in raw_dict.keys() if col in FORBIDDEN_TARGET_NAMES]
    if leaked_targets:
        raise ValueError(
            f"TARGET LEAKAGE DETECTED! Input contains ground truth target column(s): {leaked_targets}. "
            f"Models must predict these values; they must never receive them as inputs."
        )

    # 3. Handle zero-variance feature ('Exertional CP')
    if "Exertional CP" not in raw_dict and allow_missing_zero_variance:
        raw_dict["Exertional CP"] = "N"

    # 4. Required Features Check
    missing_features = [f for f in ELIGIBLE_FEATURES if f not in raw_dict]
    if missing_features:
        raise ValueError(
            f"Missing required clinical feature(s): {missing_features}. "
            f"All 54 eligible predictive features must be provided."
        )

    norm_dict: Dict[str, Any] = {}

    # 5. Categorical Normalization: Sex
    sex_val = str(raw_dict["Sex"]).strip()
    if sex_val not in SEX_NORMALIZATION_MAP:
        raise ValueError(
            f"Invalid value for 'Sex': '{sex_val}'. Expected one of {list(SEX_NORMALIZATION_MAP.keys())}."
        )
    norm_dict["Sex"] = SEX_NORMALIZATION_MAP[sex_val]

    # 6. Categorical Normalization: VHD
    vhd_val = str(raw_dict["VHD"]).strip()
    if vhd_val not in VHD_NORMALIZATION_MAP:
        raise ValueError(
            f"Invalid value for 'VHD': '{vhd_val}'. Expected one of {list(VHD_NORMALIZATION_MAP.keys())}."
        )
    norm_dict["VHD"] = VHD_NORMALIZATION_MAP[vhd_val]

    # 7. Categorical Normalization: BBB
    bbb_val = str(raw_dict["BBB"]).strip()
    if bbb_val not in ["N", "LBBB", "RBBB"]:
        raise ValueError(f"Invalid value for 'BBB': '{bbb_val}'. Expected 'N', 'LBBB', or 'RBBB'.")
    norm_dict["BBB"] = bbb_val

    # 8. Numeric Coercion & Validation
    numeric_features = [
        "Age", "Weight", "Length", "BMI", "BP", "PR", "FBS", "CR", "TG", "LDL",
        "HDL", "BUN", "ESR", "HB", "K", "Na", "WBC", "Lymph", "Neut", "PLT",
        "EF-TTE", "Region RWMA", "Function Class", "DM", "HTN", "Current Smoker",
        "EX-Smoker", "FH", "Edema", "Typical Chest Pain", "Q Wave", "St Elevation",
        "St Depression", "Tinversion"
    ]

    for col in numeric_features:
        val = raw_dict[col]
        try:
            norm_dict[col] = float(val) if col in ["BMI", "CR", "HDL", "HB", "K"] else int(round(float(val)))
        except (ValueError, TypeError):
            raise ValueError(f"Feature '{col}' must be numeric, got: {val!r}")

    # 9. Binary String Normalization ('Y'/'N')
    binary_str_features = [
        "Obesity", "CRF", "CVA", "Airway disease", "Thyroid Disease", "CHF", "DLP",
        "Weak Peripheral Pulse", "Lung rales", "Systolic Murmur", "Diastolic Murmur",
        "Dyspnea", "Atypical", "Nonanginal", "LowTH Ang", "LVH", "Poor R Progression",
        "Exertional CP"
    ]

    for col in binary_str_features:
        val = raw_dict.get(col, "N")
        val_upper = str(val).strip().upper()
        if val_upper in BINARY_STRING_MAP:
            norm_dict[col] = BINARY_STRING_MAP[val_upper]
        elif val in [0, 1]:
            norm_dict[col] = "Y" if val == 1 else "N"
        else:
            raise ValueError(f"Feature '{col}' must be binary ('Y'/'N' or 1/0), got: {val!r}")

    # 10. Return strictly ordered 1-row DataFrame matching training schema
    # (Exertional CP included; will be dropped cleanly by pipeline's cleaner step)
    feature_order = list(ELIGIBLE_FEATURES)
    if "Exertional CP" not in feature_order:
        feature_order.append("Exertional CP")

    df_out = pd.DataFrame([norm_dict])[feature_order]
    return df_out
