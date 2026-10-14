import sys
sys.path.insert(0, ".")
import joblib
from pathlib import Path
from sklearn.impute import SimpleImputer

def _patch_pipeline_compatibility(pipeline):
    def _visit(obj):
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

for t in ["cad", "lad", "lcx", "rca"]:
    p = joblib.load(f"models/{t}/pipeline.joblib")
    _patch_pipeline_compatibility(p)
    print(f"Patched {t} successfully!")

print("All pipelines patched successfully!")
