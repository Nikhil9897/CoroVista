"""
CoroVista - Research Utilities & Serialization Helpers
Provides robust numerical metric calculations, safe JSON conversion,
and plotting configuration for Phase 4 experiments.
"""

import json
import os
from typing import Any, Dict, Optional, Set, Tuple, Union

import numpy as np
from scipy import stats

# Configure matplotlib temporary directory defensively
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
import matplotlib.pyplot as plt  # noqa: E402


def setup_plot_style() -> None:
    """Applies clean publication styling to matplotlib figures."""
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#e0e0e0"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.alpha"] = 0.7


def safe_json_value(val: Any) -> Any:
    """Recursively converts numpy types, NaNs, and infinities into JSON-safe primitives."""
    if val is None:
        return None
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    if isinstance(val, str):
        return val
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (float, np.floating)):
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)
    if isinstance(val, np.ndarray):
        return [safe_json_value(x) for x in val.tolist()]
    if isinstance(val, dict):
        return {str(k): safe_json_value(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [safe_json_value(x) for x in val]
    return str(val)


def save_json(data: Dict[str, Any], filepath: Any) -> None:
    """Saves dictionary to JSON safely handling numpy types."""
    clean_data = safe_json_value(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2)


def jaccard_similarity(set_a: Set[Any], set_b: Set[Any]) -> float:
    """Computes Jaccard similarity index between two sets."""
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    if union == 0:
        return 0.0
    return float(intersection / union)


def compute_pairwise_rank_correlations(
    vector_a: np.ndarray, vector_b: np.ndarray
) -> Tuple[Optional[float], Optional[float]]:
    """
    Computes Spearman rank correlation and Kendall Tau between two feature vectors.
    Returns (None, None) if either vector has zero variance (constant attributions),
    preventing silent false zeros.
    """
    a = np.asarray(vector_a, dtype=float)
    b = np.asarray(vector_b, dtype=float)

    if len(a) != len(b) or len(a) < 2:
        return None, None

    # Check for zero variance / constant vectors
    if np.allclose(a, a[0]) or np.allclose(b, b[0]):
        return None, None

    # Spearman rank correlation
    try:
        spearman_res = stats.spearmanr(a, b)
        spearman_rho = float(spearman_res.statistic)
        if np.isnan(spearman_rho):
            spearman_rho = None
    except Exception:
        spearman_rho = None

    # Kendall Tau rank correlation
    try:
        kendall_res = stats.kendalltau(a, b)
        kendall_tau = float(kendall_res.statistic)
        if np.isnan(kendall_tau):
            kendall_tau = None
    except Exception:
        kendall_tau = None

    return spearman_rho, kendall_tau


def compute_binary_entropy(p: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Computes normalized binary entropy H(p) = -p log2(p) - (1-p) log2(1-p).
    Safely handles boundary values p=0.0 and p=1.0 where H(p) = 0.0.
    Output is in [0.0, 1.0].
    """
    p_arr = np.clip(np.asarray(p, dtype=float), 1e-12, 1.0 - 1e-12)
    h = -p_arr * np.log2(p_arr) - (1.0 - p_arr) * np.log2(1.0 - p_arr)

    # Clean exact boundaries
    if isinstance(p, (float, int)):
        if p <= 0.0 or p >= 1.0:
            return 0.0
        return float(h)

    p_orig = np.asarray(p)
    h[p_orig <= 0.0] = 0.0
    h[p_orig >= 1.0] = 0.0
    return h
