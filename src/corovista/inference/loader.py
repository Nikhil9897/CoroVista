"""
CoroVista - Model Pipeline & Metadata Loader Service
Stage 3: Inference Verification & Explainability

Manages cached loading and validation of serialized model artifacts:
- CAD: models/cad/
- LAD: models/lad/
- LCX: models/lcx/
- RCA: models/rca/
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib
from sklearn.pipeline import Pipeline

TARGET_DIR_MAP: Dict[str, str] = {
    "cath": "cad",
    "lad": "lad",
    "lcx": "lcx",
    "rca": "rca",
}

_MODEL_CACHE: Dict[str, Tuple[Pipeline, Dict[str, Any]]] = {}


def load_model_pipeline(
    target: str,
    models_root: Optional[Path] = None,
    force_reload: bool = False,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Loads and caches a serialized model pipeline and its training metadata.

    Parameters:
    -----------
    target: One of 'cath', 'lad', 'lcx', 'rca' (case-insensitive).
    models_root: Optional base path to models directory (defaults to 'models').
    force_reload: If True, bypasses memory cache and reloads from disk.

    Returns:
    --------
    Tuple[Pipeline, Dict[str, Any]]: The fitted scikit-learn pipeline and metadata dictionary.
    """
    t_clean = target.lower().strip()
    if t_clean not in TARGET_DIR_MAP:
        raise ValueError(f"Unknown target '{target}'. Valid targets are: {list(TARGET_DIR_MAP.keys())}")

    if not force_reload and t_clean in _MODEL_CACHE:
        return _MODEL_CACHE[t_clean]

    root = models_root or Path("models")
    dir_name = TARGET_DIR_MAP[t_clean]
    target_dir = root / dir_name

    pipeline_path = target_dir / "pipeline.joblib"
    metadata_path = target_dir / "metadata.json"

    if not pipeline_path.exists():
        raise FileNotFoundError(f"Model pipeline not found at {pipeline_path.resolve()}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Model metadata not found at {metadata_path.resolve()}")

    pipeline: Pipeline = joblib.load(pipeline_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata: Dict[str, Any] = json.load(f)

    _MODEL_CACHE[t_clean] = (pipeline, metadata)
    return pipeline, metadata


def load_all_models(
    models_root: Optional[Path] = None,
    force_reload: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """Loads all four targets into a structured dictionary."""
    bundle = {}
    for target_key in TARGET_DIR_MAP.keys():
        pipeline, metadata = load_model_pipeline(
            target_key, models_root=models_root, force_reload=force_reload
        )
        bundle[target_key] = {
            "pipeline": pipeline,
            "metadata": metadata,
            "threshold": float(metadata.get("decision_threshold", 0.5)),
            "model_family": metadata.get("model_family"),
            "calibration": metadata.get("calibration_method"),
        }
    return bundle


def clear_model_cache() -> None:
    """Clears the in-memory model cache."""
    _MODEL_CACHE.clear()
