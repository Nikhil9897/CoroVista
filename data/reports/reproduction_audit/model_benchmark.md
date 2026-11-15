# CoroVista: Machine Learning Benchmark & Internal Validation Report
**Stage 2: Leakage-Safe Multi-Target Modeling & Calibration**

> **Clinical & Methodological Disclaimer**  
> Predictions are for educational and research decision-support only. They do not constitute formal diagnostic coronary imaging.  
> All metrics below are **internal repeated-CV fold summaries** on the 303-patient cohort; repeated folds share patient observations and are not independent datasets or external validation.

---

## 1. Executive Summary & Selected Final Models

Following **Repeated Stratified 5-Fold Cross-Validation (5 Repeats = 25 correlated fold evaluations on the 303-patient cohort)** with strict pipeline, calibration, class-weight, and inner-OOF threshold isolation, the selected model configurations are:

| Target | Clinical Endpoint | Selected Model Family | Preprocessing / Scaler | Calibration | ROC-AUC (Fold Mean ± SD) | PR-AUC (Fold Mean ± SD) | Balanced Acc | Brier Score |
|---|---|---|---|---|---|---|---|---|
| **Cath** | Overall CAD Status | **XGBoost** | `onehot` / `none` | `sigmoid` | **0.912 ± 0.040** | **0.960 ± 0.020** | 0.826 ± 0.050 | 0.103 |
| **LAD** | Left Anterior Descending Stenosis | **XGBoost** | `onehot` / `none` | `sigmoid` | **0.844 ± 0.052** | **0.882 ± 0.046** | 0.773 ± 0.052 | 0.161 |
| **LCX** | Left Circumflex Stenosis | **RandomForest** | `onehot` / `none` | `uncalibrated` | **0.725 ± 0.065** | **0.609 ± 0.085** | 0.664 ± 0.060 | 0.210 |
| **RCA** | Right Coronary Artery Stenosis | **LogisticRegression** | `onehot` / `standard` | `uncalibrated` | **0.716 ± 0.060** | **0.613 ± 0.075** | 0.666 ± 0.048 | 0.225 |

*Note: Reported Mean ± SD values summarize internal repeated-CV folds rather than independent external cohorts.*

## 2. Comprehensive Model Family Comparisons (5×5 Repeated Stratified CV Fold Summaries)

### Target: `Cath`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.713 ± 0.007 | 0.713 ± 0.007 | 1.000 ± 0.000 | 0.832 ± 0.005 | 0.500 ± 0.000 | 0.205 |
| **LogisticRegression** | 0.916 ± 0.035 | 0.966 ± 0.015 | 0.922 ± 0.036 | 0.849 ± 0.055 | 0.883 ± 0.035 | 0.834 ± 0.051 | 0.116 |
| **RandomForest** | 0.920 ± 0.037 | 0.965 ± 0.018 | 0.904 ± 0.042 | 0.900 ± 0.048 | 0.901 ± 0.036 | 0.830 ± 0.064 | 0.117 |
| **XGBoost** | 0.912 ± 0.038 | 0.961 ± 0.018 | 0.916 ± 0.039 | 0.883 ± 0.049 | 0.899 ± 0.036 | 0.841 ± 0.060 | 0.107 |

### Target: `LAD`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.584 ± 0.006 | 0.584 ± 0.006 | 1.000 ± 0.000 | 0.738 ± 0.005 | 0.500 ± 0.000 | 0.243 |
| **LogisticRegression** | 0.817 ± 0.053 | 0.866 ± 0.042 | 0.784 ± 0.054 | 0.733 ± 0.074 | 0.755 ± 0.048 | 0.722 ± 0.053 | 0.185 |
| **RandomForest** | 0.853 ± 0.051 | 0.885 ± 0.045 | 0.805 ± 0.051 | 0.852 ± 0.063 | 0.826 ± 0.038 | 0.778 ± 0.050 | 0.167 |
| **XGBoost** | 0.834 ± 0.052 | 0.877 ± 0.045 | 0.803 ± 0.048 | 0.799 ± 0.074 | 0.799 ± 0.047 | 0.760 ± 0.053 | 0.165 |

### Target: `LCX`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.393 ± 0.005 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 | 0.238 |
| **LogisticRegression** | 0.685 ± 0.075 | 0.587 ± 0.099 | 0.532 ± 0.071 | 0.611 ± 0.106 | 0.566 ± 0.080 | 0.631 ± 0.060 | 0.239 |
| **RandomForest** | 0.725 ± 0.065 | 0.609 ± 0.085 | 0.602 ± 0.079 | 0.580 ± 0.094 | 0.588 ± 0.077 | 0.664 ± 0.060 | 0.210 |
| **XGBoost** | 0.736 ± 0.062 | 0.617 ± 0.082 | 0.602 ± 0.072 | 0.616 ± 0.097 | 0.605 ± 0.073 | 0.674 ± 0.055 | 0.205 |

### Target: `RCA`
| Model Family | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | Balanced Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| **Dummy** | 0.500 ± 0.000 | 0.376 ± 0.005 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.500 ± 0.000 | 0.235 |
| **LogisticRegression** | 0.716 ± 0.060 | 0.613 ± 0.075 | 0.555 ± 0.052 | 0.645 ± 0.099 | 0.594 ± 0.060 | 0.666 ± 0.048 | 0.225 |
| **RandomForest** | 0.719 ± 0.056 | 0.608 ± 0.064 | 0.573 ± 0.091 | 0.507 ± 0.127 | 0.531 ± 0.098 | 0.639 ± 0.062 | 0.209 |
| **XGBoost** | 0.704 ± 0.062 | 0.594 ± 0.077 | 0.547 ± 0.083 | 0.559 ± 0.124 | 0.548 ± 0.091 | 0.639 ± 0.065 | 0.215 |

## 3. Echocardiographic Ablation Study: Region RWMA

Regional Wall Motion Abnormality (`Region RWMA`) is an echocardiographic finding indicating regional LV dysfunction. It provides strong physiological signal but MUST NOT be misrepresented as physical 3D lesion coordinates. We evaluated model performance with vs without `Region RWMA` across all targets:

| Target | Model | With RWMA (ROC-AUC) | Without RWMA (ROC-AUC) | Delta (ROC-AUC) | Interpretation |
|---|---|---|---|---|---|
| **Cath** | LogisticRegression | 0.916 | 0.909 | +0.007 | Internal repeated-CV fold comparison |
| **Cath** | RandomForest | 0.920 | 0.909 | +0.011 | Internal repeated-CV fold comparison |
| **Cath** | XGBoost | 0.912 | 0.900 | +0.012 | Internal repeated-CV fold comparison |
| **LAD** | LogisticRegression | 0.817 | 0.801 | +0.017 | Internal repeated-CV fold comparison |
| **LAD** | RandomForest | 0.853 | 0.827 | +0.026 | Internal repeated-CV fold comparison |
| **LAD** | XGBoost | 0.834 | 0.819 | +0.014 | Internal repeated-CV fold comparison |
| **LCX** | LogisticRegression | 0.685 | 0.689 | -0.004 | Internal repeated-CV fold comparison |
| **LCX** | RandomForest | 0.725 | 0.723 | +0.002 | Internal repeated-CV fold comparison |
| **LCX** | XGBoost | 0.736 | 0.740 | -0.004 | Internal repeated-CV fold comparison |
| **RCA** | LogisticRegression | 0.716 | 0.716 | +0.000 | Internal repeated-CV fold comparison |
| **RCA** | RandomForest | 0.719 | 0.718 | +0.001 | Internal repeated-CV fold comparison |
| **RCA** | XGBoost | 0.704 | 0.710 | -0.006 | Internal repeated-CV fold comparison |

**Ablation Summary**: `Region RWMA` contributes additive discrimination primarily for `Cath` and `LAD`, while models without RWMA retain predictive signal on internal CV.

## 4. Multicollinearity Study: BMI vs (Weight & Length)

BMI is deterministically derived from Weight and Length ($BMI = Weight / (Length/100)^2$). Model performance was evaluated with and without explicit `BMI` inclusion:

| Target | Model | With BMI (ROC-AUC) | Without BMI (ROC-AUC) | Delta | Collinearity Finding |
|---|---|---|---|---|---|
| **Cath** | LogisticRegression | 0.916 | 0.915 | +0.000 | Minimal difference on internal repeated CV |
| **Cath** | XGBoost | 0.912 | 0.910 | +0.002 | Minimal difference on internal repeated CV |
| **LAD** | LogisticRegression | 0.817 | 0.817 | +0.000 | Minimal difference on internal repeated CV |
| **LAD** | XGBoost | 0.834 | 0.834 | +0.000 | Minimal difference on internal repeated CV |

**Conclusion**: Retaining BMI does not destabilize tree-based models and aligns with clinical user mental models for the simulator.

## 5. Probability Calibration & Reliability Analysis

CoroVista visualizes predicted vessel-specific stenosis probabilities on the 3D coronary anatomy. We compared Uncalibrated, Platt (Sigmoid), and Isotonic calibration with preprocessing encapsulated inside the calibrated pipeline:

#### Target: `Cath` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (10 Uniform Bins) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.1156** | 0.1200 | 0.916 |
| `XGBoost_uncalibrated` | **0.1074** | 0.1265 | 0.912 |
| `LogisticRegression_sigmoid` | **0.1070** | 0.1082 | 0.918 |
| `XGBoost_sigmoid` | **0.1034** | 0.1004 | 0.912 |
| `LogisticRegression_isotonic` | **0.1089** | 0.1001 | 0.913 |
| `XGBoost_isotonic` | **0.1044** | 0.1068 | 0.912 |

#### Target: `LAD` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (10 Uniform Bins) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.1849** | 0.1477 | 0.817 |
| `XGBoost_uncalibrated` | **0.1651** | 0.1434 | 0.834 |
| `LogisticRegression_sigmoid` | **0.1740** | 0.1306 | 0.821 |
| `XGBoost_sigmoid` | **0.1609** | 0.1326 | 0.844 |
| `LogisticRegression_isotonic` | **0.1726** | 0.1426 | 0.818 |
| `XGBoost_isotonic` | **0.1623** | 0.1339 | 0.840 |

#### Target: `LCX` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (10 Uniform Bins) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.2393** | 0.1827 | 0.685 |
| `XGBoost_uncalibrated` | **0.2054** | 0.1366 | 0.736 |
| `LogisticRegression_sigmoid` | **0.2171** | 0.1050 | 0.690 |
| `XGBoost_sigmoid` | **0.2073** | 0.1068 | 0.725 |
| `LogisticRegression_isotonic` | **0.2192** | 0.1287 | 0.684 |
| `XGBoost_isotonic` | **0.2078** | 0.1299 | 0.730 |

#### Target: `RCA` Calibration Metrics
| Model & Calibration Method | Brier Score (Lower is Better) | ECE (10 Uniform Bins) | ROC-AUC |
|---|---|---|---|
| `LogisticRegression_uncalibrated` | **0.2245** | 0.1673 | 0.716 |
| `XGBoost_uncalibrated` | **0.2154** | 0.1490 | 0.704 |
| `LogisticRegression_sigmoid` | **0.2060** | 0.1000 | 0.716 |
| `XGBoost_sigmoid` | **0.2092** | 0.1146 | 0.708 |
| `LogisticRegression_isotonic` | **0.2069** | 0.1236 | 0.713 |
| `XGBoost_isotonic` | **0.2090** | 0.1148 | 0.708 |

## 6. Target Coherence & Diagnostic Anomaly Preservation

- In **302 of 303 cases (99.67%)**, `Cath == 'CAD'` is concordant with having at least one stenotic branch (`LAD | LCX | RCA == 'Stenotic'`).
- **Record 93**: Preserved as raw observation (`LAD='Stenotic'`, `LCX='Normal'`, `RCA='Normal'`, `Cath='Normal'`). Not silently corrected or dropped.
