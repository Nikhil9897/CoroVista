"""
CoroVista - Model Pipeline & Metadata Loader Service
Cached Model Artifacts & Metadata Provider

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
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# ---------------------------------------------------------------------------
# Cross-version scikit-learn compatibility patch:
# Ensures models pickled with scikit-learn < 1.6 run cleanly in scikit-learn >= 1.6
# where SimpleImputer expects '_fill_dtype' during .transform()
# ---------------------------------------------------------------------------
if not isinstance(getattr(SimpleImputer, "_fill_dtype", None), property):
    class _FillDtypeDescriptor:
        def __get__(self, instance, owner):
            if instance is None:
                return self
            if "_fill_dtype" in instance.__dict__:
                return instance.__dict__["_fill_dtype"]
            if hasattr(instance, "statistics_") and instance.statistics_ is not None:
                return instance.statistics_.dtype
            return object

        def __set__(self, instance, value):
            instance.__dict__["_fill_dtype"] = value

    SimpleImputer._fill_dtype = _FillDtypeDescriptor()


def _patch_pipeline_compatibility(pipeline: Any) -> None:
    """Recursively patches any SimpleImputer instances in pipeline."""
    def _visit(obj: Any):
        if obj is None:
            return
        if isinstance(obj, SimpleImputer):
            if not hasattr(obj, "_fill_dtype") or getattr(obj, "_fill_dtype", None) is None:
                if hasattr(obj, "statistics_") and obj.statistics_ is not None:
                    obj._fill_dtype = obj.statistics_.dtype
                else:
                    obj._fill_dtype = object
        if hasattr(obj, "named_steps"):
            for step in obj.named_steps.values():
                _visit(step)
        if hasattr(obj, "steps"):
            for _, step in obj.steps:
                _visit(step)
        if hasattr(obj, "transformers_"):
            for _, transformer, _ in obj.transformers_:
                _visit(transformer)
        if hasattr(obj, "transformers"):
            for item in obj.transformers:
                if isinstance(item, tuple) and len(item) >= 2:
                    _visit(item[1])
        if hasattr(obj, "estimator"):
            _visit(obj.estimator)
        if hasattr(obj, "calibrated_classifiers_"):
            for cc in obj.calibrated_classifiers_:
                if hasattr(cc, "estimator"):
                    _visit(cc.estimator)
                if hasattr(cc, "base_estimator"):
                    _visit(cc.base_estimator)

    _visit(pipeline)


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
    _patch_pipeline_compatibility(pipeline)

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
