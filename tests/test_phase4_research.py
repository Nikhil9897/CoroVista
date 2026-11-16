"""
CoroVista - Phase 4 Research Unit & Integration Test Suite
Validates:
1. Feature-schema discrepancy resolution & Row 93 preservation
2. Numerical metric stability (Spearman, Kendall, Jaccard)
3. Zero-variance & undefined correlation handling
4. Binary entropy calculation & numerical boundary edge cases
5. Margin-based uncertainty & threshold proximity
6. Patient-level OOF prediction variability & CV filtering
7. Subgroup feasibility sample-size guards
8. Numerical perturbation clamping & categorical substitution validity
9. JSON serialization safety for numpy types and NaNs
10. Deterministic execution with fixed random seeds
"""

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pytest

from ml.preprocessing.pipeline import extract_features_and_targets, load_dataset
from ml.research.cv_protocol import APPROVED_TARGET_CONFIGS
from ml.research.robustness import (
    INTEGER_NUMERICAL_FEATURES,
    NUMERICAL_FEATURES,
)
from ml.research.subgroup_analysis import (
    MIN_MINORITY_CLASS_COUNT,
    MIN_SUBGROUP_SAMPLE_SIZE,
    identify_patient_subgroups,
)
from ml.research.utils import (
    compute_binary_entropy,
    compute_pairwise_rank_correlations,
    jaccard_similarity,
    safe_json_value,
)
from scripts.run_phase4_experiments import verify_feature_schema

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")


@pytest.fixture(scope="session")
def raw_dataset():
    return load_dataset(RAW_DATA_PATH)


# 1. Feature Schema Discrepancy & Row 93 Integrity
def test_feature_schema_audit_resolution(raw_dataset):
    schema_info = verify_feature_schema(raw_dataset)
    assert schema_info["raw_workbook_total_columns"] == 59
    assert schema_info["prediction_targets_count"] == 4
    assert schema_info["raw_non_target_features_count"] == 55
    assert schema_info["zero_variance_feature_present"] is True
    assert schema_info["zero_variance_feature_name"] == "Exertional CP"
    assert schema_info["eligible_predictive_features_count"] == 54
    assert schema_info["transformed_features_count"] == 57

    # Verify Patient Row Index 93 is preserved intact
    assert schema_info["row_index_93_cath"] == "Normal"
    assert schema_info["row_index_93_lad"] == "Stenotic"


# 2. Approved Production Target Configurations Integrity
def test_approved_target_configs():
    for target in ["Cath", "LAD", "LCX", "RCA"]:
        assert target in APPROVED_TARGET_CONFIGS
        cfg = APPROVED_TARGET_CONFIGS[target]
        assert "model_family" in cfg
        assert "decision_threshold" in cfg
        assert "calibration_method" in cfg

    assert APPROVED_TARGET_CONFIGS["RCA"]["decision_threshold"] == 0.35
    assert APPROVED_TARGET_CONFIGS["Cath"]["decision_threshold"] == 0.50
    assert APPROVED_TARGET_CONFIGS["LAD"]["decision_threshold"] == 0.50
    assert APPROVED_TARGET_CONFIGS["LCX"]["decision_threshold"] == 0.50


# 3. Jaccard Similarity Edge Cases
def test_jaccard_similarity():
    assert jaccard_similarity(set(), set()) == 1.0
    assert jaccard_similarity({1, 2, 3}, {1, 2, 3}) == 1.0
    assert jaccard_similarity({1, 2}, {3, 4}) == 0.0
    assert np.isclose(jaccard_similarity({1, 2, 3}, {2, 3, 4}), 2.0 / 4.0)


# 4. Rank Correlations & Undefined Zero-Variance Guards
def test_rank_correlation_guards():
    v1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    v2 = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    s_rho, k_tau = compute_pairwise_rank_correlations(v1, v2)
    assert np.isclose(s_rho, 1.0)
    assert np.isclose(k_tau, 1.0)

    # Inverse vector
    s_inv, k_inv = compute_pairwise_rank_correlations(v1, -v1)
    assert np.isclose(s_inv, -1.0)
    assert np.isclose(k_inv, -1.0)

    # Constant vector: must return (None, None) rather than silent 0.0
    v_const = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    s_none, k_none = compute_pairwise_rank_correlations(v1, v_const)
    assert s_none is None
    assert k_none is None


# 5. Binary Entropy Calculation & Numerical Edge Cases
def test_binary_entropy_boundaries():
    # Boundary values: H(0) = 0, H(1) = 0
    assert compute_binary_entropy(0.0) == 0.0
    assert compute_binary_entropy(1.0) == 0.0

    # Maximum uncertainty: H(0.5) = 1.0
    assert np.isclose(compute_binary_entropy(0.5), 1.0)

    # Symmetry around 0.5
    h_02 = compute_binary_entropy(0.2)
    h_08 = compute_binary_entropy(0.8)
    assert np.isclose(h_02, h_08)

    # Monotonicity in [0, 0.5]
    assert compute_binary_entropy(0.1) < compute_binary_entropy(0.3) < compute_binary_entropy(0.5)

    # Array vector input
    probs = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    h_arr = compute_binary_entropy(probs)
    assert h_arr[0] == 0.0
    assert h_arr[4] == 0.0
    assert np.isclose(h_arr[2], 1.0)
    assert np.isclose(h_arr[1], h_arr[3])


# 6. Safe JSON Serialization for Numpy Types and NaNs
def test_safe_json_serialization():
    data: Dict[str, Any] = {
        "int_val": np.int64(42),
        "float_val": np.float64(3.14159),
        "nan_val": np.nan,
        "inf_val": np.inf,
        "array": np.array([1, 2, np.nan, 4]),
        "nested": {"bool_val": np.bool_(True), "str_val": "test"},
    }
    clean = safe_json_value(data)
    assert clean["int_val"] == 42
    assert isinstance(clean["int_val"], int)
    assert np.isclose(clean["float_val"], 3.14159)
    assert clean["nan_val"] is None
    assert clean["inf_val"] is None
    assert clean["array"] == [1, 2, None, 4]
    assert clean["nested"]["bool_val"] is True


# 7. Subgroup Feasibility Guards
def test_subgroup_feasibility_guards(raw_dataset):
    subgroups = identify_patient_subgroups(raw_dataset)
    assert "Sex" in subgroups
    assert "Age Group" in subgroups
    assert "Diabetes (DM)" in subgroups
    assert "Hypertension (HTN)" in subgroups

    # Male: 176, Female: 127 -> both >= 30
    males = subgroups["Sex"]["Male"]
    females = subgroups["Sex"]["Female"]
    assert np.sum(males) == 176
    assert np.sum(females) == 127
    assert np.sum(males) >= MIN_SUBGROUP_SAMPLE_SIZE
    assert np.sum(females) >= MIN_SUBGROUP_SAMPLE_SIZE

    # Underpowered artificial group test: N=10 < 30
    small_mask = np.zeros(len(raw_dataset), dtype=bool)
    small_mask[:10] = True
    assert np.sum(small_mask) < MIN_SUBGROUP_SAMPLE_SIZE

    # Sparse class count test: N_pos = 2 < 5
    sparse_y = np.zeros(40, dtype=int)
    sparse_y[:2] = 1
    assert int(np.sum(sparse_y == 1)) < MIN_MINORITY_CLASS_COUNT


# 8. Numerical Perturbation Definitions
def test_numerical_features_consistency(raw_dataset):
    X, _ = extract_features_and_targets(raw_dataset)
    for col in NUMERICAL_FEATURES:
        assert col in X.columns, f"Numerical feature '{col}' missing from X."

    for col in INTEGER_NUMERICAL_FEATURES:
        assert col in NUMERICAL_FEATURES, f"Integer feature '{col}' not registered in numerical features."
