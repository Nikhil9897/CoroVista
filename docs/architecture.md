# CoroVista — System Architecture

**Track A: Cardiovascular Risk Visualization & Multi-Target Prediction**

---

## 1. System Overview & Architecture Diagram

CoroVista is architected as a modular, decoupled web-based clinical decision support prototype:

```
+-------------------------------------------------------------------+
|                     React Frontend (Future)                       |
|  - Interactive 3D Coronary Anatomy (Three.js)                     |
|  - Patient Clinical Simulator Controls                            |
|  - Local SHAP Waterfall / Feature Impact Cards                    |
+-------------------------------------------------------------------+
                                  |
                                  | REST / JSON
                                  v
+-------------------------------------------------------------------+
|                       FastAPI Backend                             |
|  backend/app/                                                     |
|  ├── routes/ (health, metadata, prediction, explanation)          |
|  ├── schemas/ (Pydantic request/response validation)              |
|  ├── services/ (orchestration of inference & explainability)      |
|  └── core/ (CORS, error envelopes, configuration)                 |
+-------------------------------------------------------------------+
                                  |
         +------------------------+------------------------+
         |                                                 |
         v                                                 v
+----------------------------------+   +----------------------------------+
|    Inference Engine              |   |    Explainability Engine         |
|    src/corovista/inference/      |   |    src/corovista/explainability/ |
|  - Target leakage prevention     |   |  - Native XGBoost Tree SHAP      |
|  - Categorical normalization     |   |  - LinearExplainer for RCA       |
|  - Calibrated probability scoring|   |  - Calibrated ensemble averaging |
|  - Thresholded classification    |   |  - Clinical label mapping        |
+----------------------------------+   +----------------------------------+
                 \                                 /
                  \                               /
                   v                             v
+-------------------------------------------------------------------+
|                    Serialized Model Artifacts                     |
|  models/                                                          |
|  ├── cad/ (XGBoost + Platt/Sigmoid calibration, threshold=0.50)   |
|  ├── lad/ (XGBoost + Platt/Sigmoid calibration, threshold=0.50)   |
|  ├── lcx/ (XGBoost uncalibrated, threshold=0.50)                  |
|  └── rca/ (Logistic Regression + Platt/Sigmoid, threshold=0.38)   |
+-------------------------------------------------------------------+
```

---

## 2. Layer Responsibilities & Technical Contracts

### 2.1 API Tier (`backend/app/`)
* **Framework**: FastAPI (Python 3.10 / 3.11).
* **Stateless Operation**: No database or session state; every inference request is evaluated in-memory.
* **Security & Validation**: Authoritative server-side Pydantic validation rejects target leakage, checks types, and normalizes categorical inputs before inference.
* **Uniform Error Envelope**:
  * Errors are formatted into `{"error": {"code": "...", "message": "...", "details": [...]}}`.
  * Python stack traces and file system paths are never leaked to external clients.

### 2.2 Inference Engine (`src/corovista/inference/`)
* **Single Source of Truth**: All pipeline evaluation is performed through [`src.corovista.inference.predictor`](file:///c:/Users/agnik/OneDrive/Desktop/CoroVista/src/corovista/inference/predictor.py).
* **Target Leakage Gate**: Rejects inputs containing `Cath`, `LAD`, `LCX`, or `RCA`.
* **Probability vs. Prediction Contract**:
  * Probability $p \in [0.0, 1.0]$ represents the continuous risk score.
  * Prediction (`CAD`/`Normal` or `Stenotic`/`Normal`) is strictly derived by comparing $p$ to the locked decision threshold:
    * Cath: threshold = 0.50
    * LAD: threshold = 0.50
    * LCX: threshold = 0.50
    * RCA: threshold = 0.38

### 2.3 Explainability Engine (`src/corovista/explainability/`)
* **SHAP Space**: Operates strictly in **model score / log-odds margin space** ($\sum \phi_j + \phi_0 = f(x)$).
* **Tree SHAP**: Uses native C++ Lundberg Tree SHAP via XGBoost booster `predict(pred_contribs=True)`.
* **CalibratedClassifierCV Handling**: Averages margin-level SHAP attributions across the 3 calibrated fold estimators.
* **Linear SHAP**: Uses `shap.LinearExplainer` on the transformed feature space for RCA Logistic Regression.
* **Human Feature Mapping**: Automatically translates internal pipeline names (e.g., `EF-TTE`, `Tinversion`, `Region RWMA`) to human-readable clinical labels.

### 2.4 Model Artifact Tier (`models/`)
* **Lock State**: Serialized in Stage 2; locked and unchanged.
* **Memory Management**: Cached upon service startup via thread-safe singleton loader; never reloaded per request.

---

## 3. Clinical & Safety Boundaries

1. **Non-Causality**:
   SHAP values reflect statistical association in the Z-Alizadeh Sani cohort ($N=303$) and do not establish direct physiological cause-and-effect.
2. **Probability vs. Spatial Coordinates**:
   Predicted vessel probabilities indicate functional likelihood of obstructive stenosis ($\ge 50\%$). They **do not** correspond to 3D lesion millimeters or spatial geometry on the coronary tree.
3. **Regulatory Status**:
   Educational and decision-support prototype only. Model outputs do not replace formal coronary angiography or physician diagnosis.
