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

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

from src.corovista.inference.loader import load_model_pipeline


class TargetExplainer:
    """
    Explainer for a specific target model operating in uncalibrated log-odds / margin space.

    Mathematical Properties:
    - For uncalibrated models, SHAP attributions exactly reconstruct the model score (log-odds).
    - For calibrated models (CalibratedClassifierCV), SHAP attributions represent the arithmetic
      mean of feature contributions across the K fitted fold estimators. The sum of attributions
      plus base value reconstructs the ensemble's mean uncalibrated score: (1/K) * sum(score_k).
    - Probability calibration is a post-processing mapping that converts scores to calibrated
      probabilities; it does not admit an exact additive linear decomposition in probability space.
    """

    def __init__(
        self,
        target: str,
        pipeline: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        models_root: Optional[Any] = None,
    ):
        self.target = target.lower().strip()
        if pipeline is not None and metadata is not None:
            self.pipeline = pipeline
            self.metadata = metadata
        else:
            self.pipeline, self.metadata = load_model_pipeline(self.target, models_root=models_root)

        self._extract_pipeline_components()
        self.feature_names: List[str] = self._extract_feature_names()
        self.model_family: str = self.metadata.get("model_family", "Unknown")
        self.calibration_method: str = self.metadata.get("calibration_method", "uncalibrated")
        self.explanation_space: str = "log-odds (model score)"

        # Background dataset reference for LinearExplainer if needed
        self._linear_explainers: Optional[List[shap.LinearExplainer]] = None

    def _extract_pipeline_components(self) -> None:
        """
        Extracts self.preprocessing and self.classifier across both:
        1. New calibrated structure: self.pipeline is CalibratedClassifierCV wrapping Pipeline
        2. Legacy calibrated structure: self.pipeline is Pipeline with CalibratedClassifierCV classifier step
        3. Uncalibrated structure: self.pipeline is Pipeline with raw estimator classifier step
        """
        # Case 1: Outer object is CalibratedClassifierCV (new calibrated structure)
        if isinstance(self.pipeline, CalibratedClassifierCV) or hasattr(self.pipeline, "calibrated_classifiers_"):
            self.classifier = self.pipeline
            cal_classifiers = getattr(self.pipeline, "calibrated_classifiers_", None)
            if cal_classifiers and len(cal_classifiers) > 0:
                first_cal = cal_classifiers[0]
                first_est = getattr(first_cal, "estimator", getattr(first_cal, "base_estimator", None))
                if (
                    isinstance(first_est, Pipeline)
                    and hasattr(first_est, "named_steps")
                    and "preprocessing" in first_est.named_steps
                ):
                    self.preprocessing = first_est.named_steps["preprocessing"]
                    return

            # Blueprint estimator fallback
            if (
                hasattr(self.pipeline, "estimator")
                and isinstance(self.pipeline.estimator, Pipeline)
                and hasattr(self.pipeline.estimator, "named_steps")
                and "preprocessing" in self.pipeline.estimator.named_steps
            ):
                self.preprocessing = self.pipeline.estimator.named_steps["preprocessing"]
                return

            raise ValueError("CalibratedClassifierCV is missing a fitted preprocessing pipeline.")

        # Case 2 & 3: Outer object is Pipeline (legacy calibrated or uncalibrated structure)
        if isinstance(self.pipeline, Pipeline) or hasattr(self.pipeline, "named_steps"):
            if "preprocessing" not in self.pipeline.named_steps or "classifier" not in self.pipeline.named_steps:
                raise ValueError("Pipeline must contain 'preprocessing' and 'classifier' named steps.")
            self.preprocessing = self.pipeline.named_steps["preprocessing"]
            self.classifier = self.pipeline.named_steps["classifier"]
            return

        raise TypeError(f"Unsupported pipeline structure type: {type(self.pipeline).__name__}")

    def _extract_feature_names(self) -> List[str]:
        """Extracts transformed output feature names from the preprocessing step."""
        from sklearn.exceptions import NotFittedError

        try:
            if hasattr(self.preprocessing, "named_steps") and "processor" in self.preprocessing.named_steps:
                proc = self.preprocessing.named_steps["processor"]
                if hasattr(proc, "get_feature_names_out"):
                    return list(proc.get_feature_names_out())
            if hasattr(self.preprocessing, "get_feature_names_out"):
                return list(self.preprocessing.get_feature_names_out())
        except NotFittedError as e:
            raise ValueError("Preprocessing pipeline must be fitted before initializing TargetExplainer.") from e

        raise ValueError("Cannot extract feature names from preprocessing pipeline.")

    def _get_calibrated_classifiers(self) -> Optional[List[Any]]:
        """Returns the list of calibrated classifier fold objects if calibrated, else None."""
        if hasattr(self.pipeline, "calibrated_classifiers_"):
            return list(self.pipeline.calibrated_classifiers_)
        if hasattr(self.classifier, "calibrated_classifiers_"):
            return list(self.classifier.calibrated_classifiers_)
        return None

    def _extract_fold_estimator(self, cal_clf: Any) -> Tuple[Optional[Pipeline], Any]:
        """
        Extracts (fold_preprocessing, fold_classifier) from a calibrated fold object.
        Supports:
        - New structure: cal_clf.estimator is Pipeline([('preprocessing', ...), ('classifier', ...)])
        - Legacy structure: cal_clf.estimator is the raw estimator (XGBClassifier, LogisticRegression)
        """
        est = getattr(cal_clf, "estimator", getattr(cal_clf, "base_estimator", None))
        if est is None:
            raise ValueError("Calibrated classifier entry is missing an underlying fitted estimator.")

        if isinstance(est, Pipeline) and hasattr(est, "named_steps"):
            fold_prep = est.named_steps.get("preprocessing")
            fold_clf = est.named_steps.get("classifier")
            if fold_clf is None:
                raise ValueError("Fold Pipeline is missing a 'classifier' step.")
            return fold_prep, fold_clf

        return None, est

    def _get_uncalibrated_classifier(self) -> Any:
        """Returns the raw uncalibrated classifier instance."""
        if hasattr(self.pipeline, "named_steps") and "classifier" in self.pipeline.named_steps:
            step = self.pipeline.named_steps["classifier"]
            if hasattr(step, "named_steps") and "classifier" in step.named_steps:
                return step.named_steps["classifier"]
            return step
        if hasattr(self.classifier, "named_steps") and "classifier" in self.classifier.named_steps:
            return self.classifier.named_steps["classifier"]
        return self.classifier

    def transform_features(self, df_input: pd.DataFrame) -> np.ndarray:
        """Applies pipeline preprocessing transformations."""
        return self.preprocessing.transform(df_input)

    def explain(self, df_input: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """
        Calculates exact SHAP values and base value in log-odds / margin model score space.

        Mathematical Properties:
        ------------------------
        - Reconstructs the mean uncalibrated model score (log-odds / margin) across fitted folds:
            sum(shap_values, axis=1) + base_value == (1/K) * sum(fold_scores)
        - Does NOT linearly decompose the final calibrated probability P(Y=1|X) because
          probability calibration (Platt scaling / isotonic regression) applies non-linear mappings
          per fold before averaging in probability space.

        Returns:
        --------
        Tuple[np.ndarray, float]: (shap_values of shape (n_samples, n_features), base_value)
        """
        calibrated_list = self._get_calibrated_classifiers()
        is_calibrated = calibrated_list is not None and len(calibrated_list) > 0

        if self.model_family == "XGBoost":
            if is_calibrated:
                assert calibrated_list is not None
                contribs_list = []
                for cal_clf in calibrated_list:
                    fold_prep, fold_clf = self._extract_fold_estimator(cal_clf)
                    if fold_prep is not None:
                        X_fold = fold_prep.transform(df_input)
                    else:
                        X_fold = self.transform_features(df_input)

                    if not hasattr(fold_clf, "get_booster"):
                        raise TypeError(
                            f"Expected XGBoost classifier in calibrated fold, got {type(fold_clf).__name__}"
                        )
                    booster = fold_clf.get_booster()
                    dmat = xgb.DMatrix(X_fold, feature_names=self.feature_names)
                    contribs = booster.predict(dmat, pred_contribs=True)
                    contribs_list.append(contribs)

                avg_contribs = np.mean(contribs_list, axis=0)
                shap_values = avg_contribs[:, :-1]
                base_value = float(avg_contribs[0, -1])
                return shap_values, base_value
            else:
                underlying_clf = self._get_uncalibrated_classifier()
                if not hasattr(underlying_clf, "get_booster"):
                    raise TypeError(
                        f"Expected XGBoost classifier, got {type(underlying_clf).__name__}"
                    )
                booster = underlying_clf.get_booster()
                X_trans = self.transform_features(df_input)
                dmat = xgb.DMatrix(X_trans, feature_names=self.feature_names)
                contribs = booster.predict(dmat, pred_contribs=True)
                shap_values = contribs[:, :-1]
                base_value = float(contribs[0, -1])
                return shap_values, base_value

        elif self.model_family == "LogisticRegression":
            n_features = len(self.feature_names)
            zero_masker = np.zeros((1, n_features))

            if is_calibrated:
                assert calibrated_list is not None
                if self._linear_explainers is None or len(self._linear_explainers) != len(calibrated_list):
                    self._linear_explainers = []
                    for cal_clf in calibrated_list:
                        _, fold_clf = self._extract_fold_estimator(cal_clf)
                        exp = shap.LinearExplainer(fold_clf, zero_masker)
                        self._linear_explainers.append(exp)

                shap_list = []
                base_list = []
                for idx, cal_clf in enumerate(calibrated_list):
                    fold_prep, _ = self._extract_fold_estimator(cal_clf)
                    if fold_prep is not None:
                        X_fold = fold_prep.transform(df_input)
                    else:
                        X_fold = self.transform_features(df_input)

                    exp = self._linear_explainers[idx]
                    s_vals = exp.shap_values(X_fold)
                    shap_list.append(s_vals)
                    base_list.append(float(exp.expected_value))

                avg_shap = np.mean(shap_list, axis=0)
                avg_base = float(np.mean(base_list))
                return avg_shap, avg_base
            else:
                underlying_clf = self._get_uncalibrated_classifier()
                if self._linear_explainers is None or len(self._linear_explainers) != 1:
                    self._linear_explainers = [shap.LinearExplainer(underlying_clf, zero_masker)]

                X_trans = self.transform_features(df_input)
                exp = self._linear_explainers[0]
                shap_values = exp.shap_values(X_trans)
                base_value = float(exp.expected_value)
                return shap_values, base_value

        else:
            raise NotImplementedError(f"Unsupported model family for explanation: {self.model_family}")


_EXPLAINER_CACHE: Dict[str, TargetExplainer] = {}


def get_target_explainer(target: str, models_root: Optional[Any] = None) -> TargetExplainer:
    """Retrieves or instantiates cached TargetExplainer."""
    t_clean = target.lower().strip()
    if models_root is not None:
        return TargetExplainer(t_clean, models_root=models_root)
    if t_clean not in _EXPLAINER_CACHE:
        _EXPLAINER_CACHE[t_clean] = TargetExplainer(t_clean)
    return _EXPLAINER_CACHE[t_clean]


def clear_explainer_cache() -> None:
    """Clears cached TargetExplainer instances."""
    _EXPLAINER_CACHE.clear()
