"""
CoroVista - SHAP Explainer Engine
Exact TreeSHAP & LinearSHAP Attributions

Provides exact, robust SHAP explanation generators for all four final models:
- Cath (XGBoost + CalibratedClassifierCV): Exact Tree SHAP in log-odds space,
  averaged across the 3 calibrated base estimators.
- LAD (XGBoost + CalibratedClassifierCV): Exact Tree SHAP in log-odds space,
  averaged across the 3 calibrated base estimators.
- LCX (XGBoost Uncalibrated): Exact Tree SHAP in log-odds space.
- RCA (Logistic Regression + CalibratedClassifierCV): Exact Linear SHAP in log-odds space,
  averaged across the 3 calibrated base estimators.

Important Calibration Clarification:
"SHAP values explain the underlying predictive model score (log-odds / margin);
probability calibration is applied separately to produce final visual probabilities."
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.pipeline import Pipeline

from src.corovista.inference.loader import load_model_pipeline


class TargetExplainer:
    """Explainer for a specific target model."""

    def __init__(self, target: str):
        self.target = target.lower().strip()
        self.pipeline, self.metadata = load_model_pipeline(self.target)
        self.preprocessing: Pipeline = self.pipeline.named_steps["preprocessing"]
        self.classifier = self.pipeline.named_steps["classifier"]
        self.feature_names: List[str] = list(
            self.preprocessing.named_steps["processor"].get_feature_names_out()
        )
        self.model_family: str = self.metadata.get("model_family", "Unknown")
        self.calibration_method: str = self.metadata.get("calibration_method", "uncalibrated")
        self.explanation_space: str = "log-odds (model score)"

        # Background dataset reference for LinearExplainer if needed
        self._linear_explainers: Optional[List[shap.LinearExplainer]] = None

    def transform_features(self, df_input: pd.DataFrame) -> np.ndarray:
        """Applies pipeline preprocessing transformations."""
        return self.preprocessing.transform(df_input)

    def explain(self, df_input: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """
        Calculates exact SHAP values and base value for the input dataset.

        Returns:
        --------
        Tuple[np.ndarray, float]: (shap_values of shape (n_samples, n_features), base_value)
        """
        X_trans = self.transform_features(df_input)
        n_samples = X_trans.shape[0]

        if self.model_family == "XGBoost":
            dmat = xgb.DMatrix(X_trans, feature_names=self.feature_names)

            if hasattr(self.classifier, "calibrated_classifiers_"):
                # Cath and LAD: Average exact Tree SHAP across the 3 calibrated fold models
                contribs_list = []
                for cal_clf in self.classifier.calibrated_classifiers_:
                    booster = cal_clf.estimator.get_booster()
                    contribs = booster.predict(dmat, pred_contribs=True)
                    contribs_list.append(contribs)
                avg_contribs = np.mean(contribs_list, axis=0)
                shap_values = avg_contribs[:, :-1]
                base_value = float(avg_contribs[0, -1])
            else:
                # LCX: Single uncalibrated XGBoost model
                booster = self.classifier.get_booster()
                contribs = booster.predict(dmat, pred_contribs=True)
                shap_values = contribs[:, :-1]
                base_value = float(contribs[0, -1])

            return shap_values, base_value

        elif self.model_family == "LogisticRegression":
            # RCA: LinearExplainer across calibrated fold models
            if self._linear_explainers is None:
                self._linear_explainers = []
                for cal_clf in self.classifier.calibrated_classifiers_:
                    exp = shap.LinearExplainer(cal_clf.estimator, X_trans)
                    self._linear_explainers.append(exp)

            shap_list = []
            base_list = []
            for exp in self._linear_explainers:
                s_vals = exp.shap_values(X_trans)
                shap_list.append(s_vals)
                base_list.append(exp.expected_value)

            avg_shap = np.mean(shap_list, axis=0)
            avg_base = float(np.mean(base_list))
            return avg_shap, avg_base

        else:
            raise NotImplementedError(f"Unsupported model family for explanation: {self.model_family}")


_EXPLAINER_CACHE: Dict[str, TargetExplainer] = {}


def get_target_explainer(target: str) -> TargetExplainer:
    """Retrieves or instantiates cached TargetExplainer."""
    t_clean = target.lower().strip()
    if t_clean not in _EXPLAINER_CACHE:
        _EXPLAINER_CACHE[t_clean] = TargetExplainer(t_clean)
    return _EXPLAINER_CACHE[t_clean]
