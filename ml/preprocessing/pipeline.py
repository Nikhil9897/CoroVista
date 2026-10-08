"""
CoroVista - Leakage-Safe Preprocessing Pipeline
Stage 2: Machine Learning Foundation

This module constructs strict, leakage-safe scikit-learn preprocessing pipelines.
Key guarantees:
1. Automated Leakage Prevention: Fails immediately if any target column enters X.
2. Encapsulated inside CV: All statistical parameters (medians, scalers, encoders)
   are learned strictly inside training folds.
3. Deterministic Normalization: Fixes 'Fmale' typo, normalizes 'VHD' casing.
4. Benchmarking Support: Supports configurable categorical encoding (One-Hot vs Ordinal),
   numerical scaling (None vs StandardScaler vs RobustScaler),
   and controlled ablation switches (Region RWMA ablation, BMI collinearity ablation).
"""

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, RobustScaler, StandardScaler

from ml.preprocessing.feature_metadata import (
    FEATURE_PARTITIONS,
    TARGET_COLUMNS,
    ZERO_VARIANCE_COLUMNS,
    assert_no_target_leakage,
)


def load_dataset(file_path: Union[str, Path], sheet_name: str = "Sheet 1 - Table 1") -> pd.DataFrame:
    """Loads dataset from verified primary sheet."""
    return pd.read_excel(str(file_path), sheet_name=sheet_name)

# VHD Ordinal Mapping
VHD_ORDINAL_MAP = {
    "N": 0,
    "Normal": 0,
    "normal": 0,
    "mild": 1,
    "Mild": 1,
    "Moderate": 2,
    "moderate": 2,
    "Severe": 3,
    "severe": 3,
}

# Sex Binary Mapping
SEX_BINARY_MAP = {
    "Male": 1,
    "male": 1,
    "M": 1,
    "Fmale": 0,
    "Female": 0,
    "female": 0,
    "F": 0,
}


class LeakageGuardTransformer(BaseEstimator, TransformerMixin):
    """Fails loudly if any target column is present in the feature matrix."""

    def __init__(self, targets: Optional[List[str]] = None):
        self.targets = targets or TARGET_COLUMNS

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y=None):
        self._check_leakage(X)
        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray], y=None):
        self._check_leakage(X)
        return X

    def _check_leakage(self, X):
        if isinstance(X, pd.DataFrame):
            assert_no_target_leakage(X.columns.tolist())


class ClinicalFeatureCleaner(BaseEstimator, TransformerMixin):
    """
    Cleans raw clinical features deterministically:
    - Drops zero-variance features ('Exertional CP')
    - Maps 'Sex' ('Fmale' -> 0, 'Male' -> 1)
    - Maps binary strings ('Y' -> 1, 'N' -> 0)
    - Normalizes 'VHD' casing
    - Supports controlled ablation switches: drop_rwma, drop_bmi
    """

    def __init__(
        self,
        vhd_encoding: Literal["onehot", "ordinal"] = "onehot",
        drop_rwma: bool = False,
        drop_bmi: bool = False,
        drop_zero_variance: bool = True,
    ):
        self.vhd_encoding = vhd_encoding
        self.drop_rwma = drop_rwma
        self.drop_bmi = drop_bmi
        self.drop_zero_variance = drop_zero_variance
        self.feature_names_in_: List[str] = []
        self.columns_to_drop_: List[str] = []

    def fit(self, X: pd.DataFrame, y=None):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("ClinicalFeatureCleaner requires a pandas DataFrame input.")

        self.feature_names_in_ = X.columns.tolist()
        cols_to_drop = []
        if self.drop_zero_variance:
            for col in ZERO_VARIANCE_COLUMNS:
                if col in X.columns:
                    cols_to_drop.append(col)
        if self.drop_rwma and "Region RWMA" in X.columns:
            cols_to_drop.append("Region RWMA")
        if self.drop_bmi and "BMI" in X.columns:
            cols_to_drop.append("BMI")

        self.columns_to_drop_ = cols_to_drop
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("ClinicalFeatureCleaner requires a pandas DataFrame input.")

        X_clean = X.copy()

        # Drop targeted columns
        if self.columns_to_drop_:
            X_clean = X_clean.drop(columns=[c for c in self.columns_to_drop_ if c in X_clean.columns])

        # 1. Normalize 'Sex'
        if "Sex" in X_clean.columns:
            X_clean["Sex"] = X_clean["Sex"].map(SEX_BINARY_MAP)
            if X_clean["Sex"].isnull().any():
                # Fallback for unexpected string
                X_clean["Sex"] = X_clean["Sex"].fillna(0).astype(int)
            else:
                X_clean["Sex"] = X_clean["Sex"].astype(int)

        # 2. Normalize binary string features ('Y' -> 1, 'N' -> 0)
        for col in FEATURE_PARTITIONS["binary_string"]:
            if col in X_clean.columns and X_clean[col].dtype == "object":
                X_clean[col] = (
                    X_clean[col].astype(str).str.strip().str.upper().map({"Y": 1, "N": 0}).fillna(0).astype(int)
                )

        # 3. Normalize 'VHD'
        if "VHD" in X_clean.columns:
            if self.vhd_encoding == "ordinal":
                X_clean["VHD"] = X_clean["VHD"].map(VHD_ORDINAL_MAP).fillna(0).astype(int)
            else:
                # Standardize strings for One-Hot encoding
                vhd_norm_str = {
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
                X_clean["VHD"] = X_clean["VHD"].map(vhd_norm_str).fillna("Normal")

        # 4. Standardize 'BBB'
        if "BBB" in X_clean.columns:
            X_clean["BBB"] = X_clean["BBB"].astype(str).str.strip()

        return X_clean


def build_preprocessing_pipeline(
    vhd_encoding: Literal["onehot", "ordinal"] = "onehot",
    scaler_type: Literal["none", "standard", "robust"] = "none",
    drop_rwma: bool = False,
    drop_bmi: bool = False,
) -> Pipeline:
    """
    Constructs an end-to-end scikit-learn preprocessing Pipeline.

    Parameters:
    -----------
    vhd_encoding: 'onehot' (nominal) or 'ordinal' (ordered integers 0..3)
    scaler_type: 'none' (for tree models), 'standard' (StandardScaler), or 'robust' (RobustScaler)
    drop_rwma: bool, whether to drop 'Region RWMA' for ablation study
    drop_bmi: bool, whether to drop 'BMI' for multicollinearity ablation study
    """
    # 1. Determine active numerical columns
    active_num_cols = list(FEATURE_PARTITIONS["numerical"])
    if drop_rwma and "Region RWMA" in active_num_cols:
        active_num_cols.remove("Region RWMA")
    if drop_bmi and "BMI" in active_num_cols:
        active_num_cols.remove("BMI")

    # Add Function Class as numerical/ordinal
    active_num_cols.append("Function Class")

    # If VHD is ordinal, treat it as a numerical/ordinal integer
    if vhd_encoding == "ordinal":
        active_num_cols.append("VHD")

    # 2. Binary features (both integer and converted strings)
    active_bin_cols = list(FEATURE_PARTITIONS["binary_integer"]) + list(FEATURE_PARTITIONS["binary_string"])
    active_bin_cols.append("Sex")  # Converted to 0/1 by ClinicalFeatureCleaner

    # 3. Categorical columns for One-Hot Encoding
    categorical_cols = ["BBB"]
    if vhd_encoding == "onehot":
        categorical_cols.append("VHD")

    # Numerical Transformer
    num_steps: List[Tuple[str, BaseEstimator]] = [("imputer", SimpleImputer(strategy="median"))]
    if scaler_type == "standard":
        num_steps.append(("scaler", StandardScaler()))
    elif scaler_type == "robust":
        num_steps.append(("scaler", RobustScaler()))
    num_transformer = Pipeline(num_steps)

    # Binary Transformer (defensive most_frequent imputer)
    bin_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent"))
    ])

    # Categorical One-Hot Transformer
    cat_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False)),
    ])

    # ColumnTransformer
    column_processor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, active_num_cols),
            ("bin", bin_transformer, active_bin_cols),
            ("cat", cat_transformer, categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    # Full End-to-End Preprocessing Pipeline
    full_pipeline = Pipeline([
        ("leakage_guard", LeakageGuardTransformer()),
        (
            "cleaner",
            ClinicalFeatureCleaner(
                vhd_encoding=vhd_encoding,
                drop_rwma=drop_rwma,
                drop_bmi=drop_bmi,
                drop_zero_variance=True,
            ),
        ),
        ("processor", column_processor),
    ])

    return full_pipeline


def extract_features_and_targets(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
    """
    Separates feature matrix X from ground-truth target vectors.
    Strictly asserts no targets remain in X.
    """
    # Verify all targets exist
    for target in TARGET_COLUMNS:
        if target not in df.columns:
            raise KeyError(f"Target column '{target}' missing from input DataFrame.")

    # Target encodings (CAD/Stenotic -> 1, Normal -> 0)
    target_mappings = {
        "Cath": {"CAD": 1, "Normal": 0},
        "LAD": {"Stenotic": 1, "Normal": 0},
        "LCX": {"Stenotic": 1, "Normal": 0},
        "RCA": {"Stenotic": 1, "Normal": 0},
    }

    targets = {}
    for target, mapping in target_mappings.items():
        targets[target] = df[target].map(mapping).astype(int)

    # Feature matrix X: strictly exclude all 4 targets
    X = df.drop(columns=TARGET_COLUMNS).copy()
    assert_no_target_leakage(X.columns.tolist())

    return X, targets
