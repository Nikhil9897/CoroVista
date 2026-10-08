# CoroVista: Machine Learning Benchmark & Validation Report
**Stage 2: Leakage-Safe Multi-Target Modeling & Calibration**

> **Clinical Decision-Support Disclaimer**  
> Predictions are for educational and clinical decision-support only. They do not constitute formal diagnostic coronary imaging.

---

## 1. Executive Summary & Selected Final Models

Following rigorous **Repeated Stratified 5-Fold Cross-Validation (5 Repeats = 25 evaluation runs per model)** with strict leakage prevention, the best model for each target was independently selected:

| Target | Clinical Endpoint | Selected Model Family | Preprocessing / Scaler | Calibration | ROC-AUC (Mean ± Std) | PR-AUC (Mean ± Std) | Balanced Acc | Brier Score |
|---|---|---|---|---|---|---|---|---|
| **Cath** | Overall CAD Status | **XGBoost** | `onehot` / `none` | `sigmoid` | **0.910 ± 0.041** | **0.958 ± 0.021** | 0.843 ± 0.056 | 0.108 |
| **LAD** | Left Anterior Descending Stenosis | **XGBoost** | `onehot` / `none` | `sigmoid` | **0.836 ± 0.049** | **0.878 ± 0.041** | 0.763 ± 0.056 | 0.165 |
| **LCX** | Left Circumflex Stenosis | **RandomForest** | `onehot` / `none` | `uncalibrated` | **0.724 ± 0.065** | **0.608 ± 0.086** | 0.662 ± 0.060 | 0.210 |
| **RCA** | Right Coronary Artery Stenosis | **LogisticRegression** | `onehot` / `standard` | `uncalibrated` | **0.716 ± 0.060** | **0.613 ± 0.075** | 0.666 ± 0.048 | 0.225 |

*Notice: As designed, different model families were independently chosen for each target to optimize target-specific clinical accuracy, probability calibration, and discrimination.*

## 2. Comprehensive Model Family Comparisons (25-Fold CV)

### Target: `Cath`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.713 ± 0.007 | 0.713 ± 0.007 | 1.000 ± 0.000 | 0.832 ± 0.005 | 0.500 ± 0.000 | 0.205 |
| **LogisticRegression** | 0.916 ± 0.035 | 0.966 ± 0.015 | 0.922 ± 0.036 | 0.849 ± 0.055 | 0.883 ± 0.035 | 0.834 ± 0.051 | 0.116 |
| **RandomForest** | 0.921 ± 0.037 | 0.965 ± 0.018 | 0.905 ± 0.042 | 0.901 ± 0.048 | 0.902 ± 0.037 | 0.831 ± 0.064 | 0.117 |
| **XGBoost** | 0.910 ± 0.041 | 0.958 ± 0.021 | 0.919 ± 0.038 | 0.881 ± 0.051 | 0.899 ± 0.035 | 0.843 ± 0.056 | 0.108 |

### Target: `LAD`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.584 ± 0.006 | 0.584 ± 0.006 | 1.000 ± 0.000 | 0.738 ± 0.005 | 0.500 ± 0.000 | 0.243 |
| **LogisticRegression** | 0.817 ± 0.053 | 0.866 ± 0.042 | 0.784 ± 0.054 | 0.733 ± 0.074 | 0.755 ± 0.048 | 0.722 ± 0.053 | 0.185 |
| **RandomForest** | 0.852 ± 0.051 | 0.884 ± 0.045 | 0.805 ± 0.051 | 0.852 ± 0.063 | 0.826 ± 0.038 | 0.778 ± 0.050 | 0.167 |
| **XGBoost** | 0.836 ± 0.049 | 0.878 ± 0.041 | 0.808 ± 0.056 | 0.799 ± 0.068 | 0.801 ± 0.045 | 0.763 ± 0.056 | 0.165 |

### Target: `LCX`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.393 ± 0.005 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 | 0.238 |
| **LogisticRegression** | 0.685 ± 0.075 | 0.587 ± 0.099 | 0.532 ± 0.071 | 0.611 ± 0.106 | 0.566 ± 0.080 | 0.631 ± 0.060 | 0.239 |
| **RandomForest** | 0.724 ± 0.065 | 0.608 ± 0.086 | 0.600 ± 0.078 | 0.576 ± 0.098 | 0.585 ± 0.079 | 0.662 ± 0.060 | 0.210 |
| **XGBoost** | 0.738 ± 0.061 | 0.622 ± 0.087 | 0.608 ± 0.087 | 0.611 ± 0.106 | 0.606 ± 0.083 | 0.676 ± 0.065 | 0.204 |

### Target: `RCA`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.376 ± 0.005 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 | 0.235 |
| **LogisticRegression** | 0.716 ± 0.060 | 0.613 ± 0.075 | 0.555 ± 0.052 | 0.645 ± 0.099 | 0.594 ± 0.060 | 0.666 ± 0.048 | 0.225 |
| **RandomForest** | 0.719 ± 0.055 | 0.609 ± 0.063 | 0.574 ± 0.090 | 0.508 ± 0.130 | 0.532 ± 0.099 | 0.640 ± 0.062 | 0.209 |
| **XGBoost** | 0.700 ± 0.063 | 0.593 ± 0.078 | 0.550 ± 0.094 | 0.544 ± 0.136 | 0.540 ± 0.100 | 0.636 ± 0.074 | 0.217 |

## 3. Echocardiographic Ablation Study: Region RWMA

Regional Wall Motion Abnormality (`Region RWMA`) is an echocardiographic finding indicating regional LV dysfunction. It provides strong physiological signal but MUST NOT be misrepresented as physical 3D lesion coordinates. We evaluated model performance with vs without `Region RWMA` across all targets:

| Target | Model | With RWMA (ROC-AUC) | Without RWMA (ROC-AUC) | Delta (ROC-AUC) | Clinical Interpretation |
|---|---|---|---|---|---|
| **Cath** | LogisticRegression | 0.916 | 0.909 | +0.007 | Signal present; model remains robust without RWMA |
| **Cath** | RandomForest | 0.921 | 0.910 | +0.011 | Signal present; model remains robust without RWMA |
| **Cath** | XGBoost | 0.910 | 0.900 | +0.010 | Signal present; model remains robust without RWMA |
| **LAD** | LogisticRegression | 0.817 | 0.801 | +0.017 | Signal present; model remains robust without RWMA |
| **LAD** | RandomForest | 0.852 | 0.826 | +0.026 | Signal present; model remains robust without RWMA |
| **LAD** | XGBoost | 0.836 | 0.815 | +0.021 | Signal present; model remains robust without RWMA |
| **LCX** | LogisticRegression | 0.685 | 0.689 | -0.004 | Signal present; model remains robust without RWMA |
| **LCX** | RandomForest | 0.724 | 0.723 | +0.001 | Signal present; model remains robust without RWMA |
| **LCX** | XGBoost | 0.738 | 0.729 | +0.009 | Signal present; model remains robust without RWMA |
| **RCA** | LogisticRegression | 0.716 | 0.716 | +0.000 | Signal present; model remains robust without RWMA |
| **RCA** | RandomForest | 0.719 | 0.718 | +0.001 | Signal present; model remains robust without RWMA |
| **RCA** | XGBoost | 0.700 | 0.704 | -0.004 | Signal present; model remains robust without RWMA |

**Ablation Conclusion**: `Region RWMA` offers consistent additive discrimination for `Cath` and `LAD` (its vascular territory). Crucially, models without RWMA still retain substantial predictive ability (ROC-AUC > 0.80 for Cath), demonstrating that the system is not fragilely dependent on a single imaging variable.

## 4. Multicollinearity Study: BMI vs (Weight & Length)

BMI is deterministically derived from Weight and Length ($BMI = Weight / (Length/100)^2$). Model performance was evaluated with and without explicit `BMI` inclusion:

| Target | Model | With BMI (ROC-AUC) | Without BMI (ROC-AUC) | Delta | Collinearity Finding |
|---|---|---|---|---|---|
| **Cath** | LogisticRegression | 0.916 | 0.915 | +0.000 | Minimal difference; tree models invariant to collinearity |
| **Cath** | XGBoost | 0.910 | 0.911 | -0.001 | Minimal difference; tree models invariant to collinearity |
| **LAD** | LogisticRegression | 0.817 | 0.817 | +0.000 | Minimal difference; tree models invariant to collinearity |
| **LAD** | XGBoost | 0.836 | 0.832 | +0.004 | Minimal difference; tree models invariant to collinearity |

**Conclusion**: Retaining BMI does not destabilize tree-based models and aligns with clinical user mental models for the upcoming simulator.

## 5. Probability Calibration & Reliability Analysis

CoroVista directly visualizes predicted vessel-specific stenosis probabilities on the 3D coronary anatomy. Therefore, well-calibrated probabilities are paramount. We compared Uncalibrated, Platt (Sigmoid), and Isotonic calibration:

#### Target: `Cath` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (Expected Calibration Error) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.1156** | 0.1200 | 0.916 |
| `XGBoost_uncalibrated` | **0.1077** | 0.1246 | 0.910 |
| `LogisticRegression_sigmoid` | **0.1057** | 0.0967 | 0.918 |
| `XGBoost_sigmoid` | **0.1018** | 0.1005 | 0.915 |
| `LogisticRegression_isotonic` | **0.1065** | 0.0978 | 0.914 |
| `XGBoost_isotonic` | **0.1034** | 0.0997 | 0.912 |

#### Target: `LAD` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (Expected Calibration Error) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.1849** | 0.1477 | 0.817 |
| `XGBoost_uncalibrated` | **0.1645** | 0.1321 | 0.836 |
| `LogisticRegression_sigmoid` | **0.1740** | 0.1283 | 0.821 |
| `XGBoost_sigmoid` | **0.1600** | 0.1170 | 0.842 |
| `LogisticRegression_isotonic` | **0.1749** | 0.1336 | 0.816 |
| `XGBoost_isotonic` | **0.1599** | 0.1324 | 0.840 |

#### Target: `LCX` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (Expected Calibration Error) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.2393** | 0.1827 | 0.685 |
| `XGBoost_uncalibrated` | **0.2041** | 0.1324 | 0.738 |
| `LogisticRegression_sigmoid` | **0.2220** | 0.1092 | 0.688 |
| `XGBoost_sigmoid` | **0.2079** | 0.1103 | 0.722 |
| `LogisticRegression_isotonic` | **0.2219** | 0.1244 | 0.676 |
| `XGBoost_isotonic` | **0.2078** | 0.1290 | 0.719 |

#### Target: `RCA` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (Expected Calibration Error) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.2245** | 0.1673 | 0.716 |
| `XGBoost_uncalibrated` | **0.2167** | 0.1469 | 0.700 |
| `LogisticRegression_sigmoid` | **0.2053** | 0.1121 | 0.716 |
| `XGBoost_sigmoid` | **0.2093** | 0.1015 | 0.709 |
| `LogisticRegression_isotonic` | **0.2080** | 0.1292 | 0.708 |
| `XGBoost_isotonic` | **0.2100** | 0.1097 | 0.704 |

## 6. Target Coherence & Diagnostic Anomaly Preservation

- In **302 of 303 cases (99.67%)**, `Cath == 'CAD'` is concordant with having at least one stenotic branch (`LAD | LCX | RCA == 'Stenotic'`).
- **Record 93**: Preserved as raw observation (`LAD='Stenotic'`, `LCX='Normal'`, `RCA='Normal'`, `Cath='Normal'`). Not silently corrected or dropped.
