"""
Unit and integration tests for CoroVista Dataset Audit & Schema Validation.

Tests cover:
- Dataset loading and sheet selection
- Schema validation
- Target existence and value domain
- Leakage prevention (target exclusion from X)
- Missing-value detection
- Constant and near-constant feature detection
- Target distribution calculation
- Feature inventory generation
- Audit reports generation
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.audit_dataset import (
    TARGET_COLUMNS,
    audit_data_quality,
    audit_leakage,
    audit_targets,
    build_feature_inventory,
    get_feature_category,
    inspect_workbook,
    load_dataset,
    run_audit,
)

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")
REPORTS_DIR = Path("data/reports")


@pytest.fixture(scope="session")
def raw_df():
    """Session fixture loading the primary dataset."""
    assert RAW_DATA_PATH.exists(), f"Raw dataset not found at {RAW_DATA_PATH}"
    return load_dataset(RAW_DATA_PATH, sheet_name="Sheet 1 - Table 1")


# 1. Dataset Loading & Sheet Selection
def test_workbook_inspection():
    meta = inspect_workbook(RAW_DATA_PATH)
    assert "Sheet 1 - Table 1" in meta["sheet_names"]
    assert "Sheet1" in meta["sheet_names"]
    assert meta["primary_sheet"] == "Sheet 1 - Table 1"
    assert meta["sheets_info"]["Sheet1"]["is_empty_of_data"] is True
    assert meta["sheets_info"]["Sheet1"]["data_rows"] == 0
    assert meta["sheets_info"]["Sheet1"]["max_columns"] == 100
    assert meta["sheets_info"]["Sheet 1 - Table 1"]["is_empty_of_data"] is False
    assert meta["sheets_info"]["Sheet 1 - Table 1"]["data_rows"] == 303
    assert meta["sheets_info"]["Sheet 1 - Table 1"]["max_columns"] == 59


def test_dataset_loading_shape(raw_df):
    assert raw_df.shape == (303, 59), f"Expected (303, 59), got {raw_df.shape}"
    assert len(raw_df) == 303
    assert len(raw_df.columns) == 59


# 2. Schema Validation
def test_schema_validation(raw_df):
    assert raw_df.columns.is_unique, "Duplicate column names detected"
    expected_sample_cols = [
        "Age", "Sex", "BMI", "DM", "HTN", "BP", "PR", "Typical Chest Pain",
        "Q Wave", "FBS", "CR", "TG", "LDL", "HDL", "EF-TTE", "Region RWMA",
        "LAD", "LCX", "RCA", "Cath"
    ]
    for col in expected_sample_cols:
        assert col in raw_df.columns, f"Expected column {col} missing from schema"


# 3. Target Existence & Domain
def test_target_existence(raw_df):
    for target in TARGET_COLUMNS:
        assert target in raw_df.columns, f"Target column '{target}' missing"
        unique_vals = set(raw_df[target].unique())
        assert len(unique_vals) == 2, f"Target '{target}' should be binary, got {unique_vals}"

    assert set(raw_df["Cath"].unique()) == {"CAD", "Normal"}
    assert set(raw_df["LAD"].unique()) == {"Stenotic", "Normal"}
    assert set(raw_df["LCX"].unique()) == {"Stenotic", "Normal"}
    assert set(raw_df["RCA"].unique()) == {"Stenotic", "Normal"}


# 4. Target Distribution Calculation
def test_target_distribution_calculation(raw_df):
    targets_audit = audit_targets(raw_df)
    for target in TARGET_COLUMNS:
        assert target in targets_audit
        t_data = targets_audit[target]
        assert t_data["positive_count"] + t_data["negative_count"] == 303
        assert t_data["imbalance_ratio"] is not None

    # Specific counts verification
    assert targets_audit["Cath"]["positive_count"] == 216
    assert targets_audit["Cath"]["negative_count"] == 87
    assert targets_audit["Cath"]["positive_percentage"] == 71.29

    assert targets_audit["LAD"]["positive_count"] == 177
    assert targets_audit["LAD"]["negative_count"] == 126

    assert targets_audit["LCX"]["positive_count"] == 119
    assert targets_audit["LCX"]["negative_count"] == 184

    assert targets_audit["RCA"]["positive_count"] == 114
    assert targets_audit["RCA"]["negative_count"] == 189


# 5. Leakage Prevention
def test_leakage_prevention(raw_df):
    leakage_res = audit_leakage(raw_df)
    assert set(leakage_res["mandatory_excluded_targets"]) == set(TARGET_COLUMNS)

    # Simulate creation of model input matrix X
    feature_matrix_cols = [c for c in raw_df.columns if c not in TARGET_COLUMNS]
    assert len(feature_matrix_cols) == 55
    for target in TARGET_COLUMNS:
        assert target not in feature_matrix_cols, f"Leakage detected: {target} found in features!"


# 6. Missing-Value Detection
def test_missing_value_detection(raw_df):
    quality = audit_data_quality(raw_df)
    assert quality["total_missing"] == 0, f"Expected 0 missing values, got {quality['total_missing']}"
    assert quality["missing_by_column"] == {}

    # Synthetic test to verify detection logic when nulls exist
    synthetic_df = raw_df.copy()
    synthetic_df.loc[0, "Age"] = np.nan
    synthetic_df.loc[1, "BP"] = np.nan
    synthetic_quality = audit_data_quality(synthetic_df)
    assert synthetic_quality["total_missing"] == 2
    assert synthetic_quality["missing_by_column"] == {"Age": 1, "BP": 1}


# 7. Constant & Near-Constant Feature Detection
def test_constant_feature_detection(raw_df):
    quality = audit_data_quality(raw_df)
    const_feats = [c["feature"] for c in quality["constant_features"]]
    assert "Exertional CP" in const_feats, "Exertional CP was not detected as constant"
    assert len(quality["constant_features"]) == 1

    # Check near-constant features (CHF has only 1 positive)
    near_const_feats = [c["feature"] for c in quality["near_constant_features"]]
    assert "CHF" in near_const_feats
    assert "LowTH Ang" in near_const_feats


# 8. Known Categorical Issues Detection
def test_known_categorical_issues(raw_df):
    quality = audit_data_quality(raw_df)
    issues_by_feat = {issue["feature"]: issue for issue in quality["categorical_issues"]}
    assert "Sex" in issues_by_feat
    assert issues_by_feat["Sex"]["original_value"] == "Fmale"
    assert "Female" in issues_by_feat["Sex"]["proposed_transformation"]

    assert "VHD" in issues_by_feat


# 9. Feature Inventory Generation
def test_feature_inventory_generation(raw_df):
    inventory = build_feature_inventory(raw_df)
    assert len(inventory) == 59
    assert list(inventory.columns) == [
        "Feature Name",
        "Data Type",
        "Category",
        "Missing Count",
        "Unique Count",
        "Example Values",
        "Potential Issue",
        "Model Eligibility",
    ]

    # Verify eligibility categorization
    eligibility_counts = inventory["Model Eligibility"].value_counts().to_dict()
    assert eligibility_counts["Excluded (Target)"] == 4
    assert eligibility_counts["Excluded (Zero Variance)"] == 1
    assert eligibility_counts["Eligible"] == 54

    # Verify category assignments
    categories = set(inventory["Category"].unique())
    assert {"Demographic", "Clinical Examination", "ECG", "Laboratory", "Echocardiographic", "Target"}.issubset(categories)


# 10. Audit Artifacts Generation
def test_audit_artifacts_generated(tmp_path):
    audit_data = run_audit(RAW_DATA_PATH, tmp_path)
    assert (tmp_path / "dataset_audit.json").exists()
    assert (tmp_path / "dataset_audit.md").exists()
    assert (tmp_path / "feature_inventory.csv").exists()

    # Validate JSON content
    with open(tmp_path / "dataset_audit.json", "r", encoding="utf-8") as f:
        loaded_json = json.load(f)
    assert "workbook_metadata" in loaded_json
    assert "quality_audit" in loaded_json
    assert "targets_audit" in loaded_json
    assert "leakage_audit" in loaded_json
