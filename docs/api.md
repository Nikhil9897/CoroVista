# CoroVista — Backend API Contract & Specification

**FastAPI Backend + Multi-Target Prediction & Explainability API**  
**Version**: 1.0.0  
**Base URL**: `/api/v1`

---

## 1. Overview & System Boundary

CoroVista provides a stateless, high-throughput REST API that bridges clinical features from the Patient Simulator and Clinical Dashboard to the serialized machine learning models. 

### Key Design Principles:
1. **Strict Separation of Probability vs. Classification**:
   * Continuous risk probabilities ($p \in [0.0, 1.0]$) represent functional risk of stenosis $\ge 50\%$ and drive 3D coronary mesh color intensity.
   * Discrete binary classifications (`CAD`/`Normal` or `Stenotic`/`Normal`) are determined strictly by target-specific decision thresholds.
2. **Explicit Explanation Space (Log-Odds / Model Score)**:
   * SHAP attributions reflect additive feature impacts in the underlying model score / logit margin space ($\sum \phi_j + \phi_0 = f(x)$).
   * Probability calibration (Platt scaling) is applied downstream; SHAP scores are **never** falsely labeled as "percentage risk changes".
3. **No Target Leakage**:
   * Ground truth target fields (`Cath`, `LAD`, `LCX`, `RCA`) are strictly rejected with HTTP 422 if present in input.
4. **Clinical & 3D Spatial Boundary**:
   * Predicted vessel risk probabilities represent functional stenosis likelihood and do **not** indicate physical 3D lesion coordinates or plaque geometry.

---

## 2. API Endpoints

### 2.1 Health & Liveness
* **Endpoint**: `GET /api/v1/health`
* **Summary**: Service Health & Model Status
* **Response (200 OK)**:
```json
{
  "status": "ok",
  "service": "corovista-api",
  "version": "1.0.0",
  "models_loaded": true
}
```
* **Degraded Response (503 Service Unavailable)**:
```json
{
  "status": "degraded",
  "service": "corovista-api",
  "version": "1.0.0",
  "models_loaded": false
}
```

---

### 2.2 Model Inventory
* **Endpoint**: `GET /api/v1/models`
* **Summary**: Model Inventory & Threshold Metadata
* **Response (200 OK)**:
```json
{
  "models": [
    {
      "target": "cath",
      "model": "XGBoost",
      "calibrated": true,
      "calibration": "Platt/Sigmoid",
      "threshold": 0.50,
      "positive_label": "CAD",
      "negative_label": "Normal",
      "explanation_space": "log-odds (model score)",
      "version": "1.0.0"
    },
    {
      "target": "lad",
      "model": "XGBoost",
      "calibrated": true,
      "calibration": "Platt/Sigmoid",
      "threshold": 0.50,
      "positive_label": "Stenotic",
      "negative_label": "Normal",
      "explanation_space": "log-odds (model score)",
      "version": "1.0.0"
    },
    {
      "target": "lcx",
      "model": "XGBoost",
      "calibrated": false,
      "calibration": "Uncalibrated",
      "threshold": 0.50,
      "positive_label": "Stenotic",
      "negative_label": "Normal",
      "explanation_space": "log-odds (model score)",
      "version": "1.0.0"
    },
    {
      "target": "rca",
      "model": "LogisticRegression",
      "calibrated": true,
      "calibration": "Platt/Sigmoid",
      "threshold": 0.38,
      "positive_label": "Stenotic",
      "negative_label": "Normal",
      "explanation_space": "log-odds (model score)",
      "version": "1.0.0"
    }
  ]
}
```

---

### 2.3 Feature Registry
* **Endpoint**: `GET /api/v1/features`
* **Summary**: Clinical Feature Registry for Patient Simulator
* **Response (200 OK)**:
```json
{
  "features": [
    {
      "machine_name": "Age",
      "human_readable_label": "Patient Age (years)",
      "type": "numeric",
      "category": "Demographic",
      "allowed_values": null,
      "dataset_observed_range": "30 to 86 (mean 58.9)",
      "simulator_validation_range": {
        "min": 18.0,
        "max": 100.0,
        "step": 1.0
      },
      "is_required": true,
      "description": "Patient age in years"
    },
    {
      "machine_name": "Sex",
      "human_readable_label": "Biological Sex (Male = 1, Female = 0)",
      "type": "categorical",
      "category": "Demographic",
      "allowed_values": ["Male", "Female"],
      "dataset_observed_range": "Male (176), Fmale (127)",
      "simulator_validation_range": null,
      "is_required": true,
      "description": "Biological sex"
    }
  ],
  "total_features": 54
}
```

---

### 2.4 Multi-Target Prediction
* **Endpoint**: `POST /api/v1/predict`
* **Summary**: Multi-Target Coronary Risk Prediction
* **Request**:
```json
{
  "patient": {
    "Age": 62,
    "Sex": "Male",
    "Weight": 78,
    "Length": 172,
    "BMI": 26.37,
    "DM": 1,
    "HTN": 1,
    "Current Smoker": 0,
    "EX-Smoker": 1,
    "FH": 0,
    "Obesity": "Y",
    "CRF": "N",
    "CVA": "N",
    "Airway disease": "N",
    "Thyroid Disease": "N",
    "CHF": "N",
    "DLP": "Y",
    "BP": 135,
    "PR": 76,
    "Edema": 0,
    "Weak Peripheral Pulse": "N",
    "Lung rales": "N",
    "Systolic Murmur": "N",
    "Diastolic Murmur": "N",
    "Typical Chest Pain": 1,
    "Dyspnea": "N",
    "Function Class": 2,
    "Atypical": "N",
    "Nonanginal": "N",
    "LowTH Ang": "N",
    "Q Wave": 0,
    "St Elevation": 0,
    "St Depression": 1,
    "Tinversion": 1,
    "LVH": "N",
    "Poor R Progression": "N",
    "BBB": "N",
    "FBS": 126,
    "CR": 1.1,
    "TG": 195,
    "LDL": 142,
    "HDL": 38,
    "BUN": 18,
    "ESR": 14,
    "HB": 14.5,
    "K": 4.4,
    "Na": 140,
    "WBC": 7200,
    "Lymph": 30,
    "Neut": 65,
    "PLT": 230,
    "EF-TTE": 45,
    "Region RWMA": 1,
    "VHD": "Mild"
  }
}
```
* **Response (200 OK)**:
```json
{
  "predictions": {
    "cath": {
      "probability": 0.7657,
      "prediction": "CAD",
      "threshold": 0.50,
      "model_family": "XGBoost",
      "calibration": "sigmoid"
    },
    "lad": {
      "probability": 0.5323,
      "prediction": "Stenotic",
      "threshold": 0.50,
      "model_family": "XGBoost",
      "calibration": "sigmoid"
    },
    "lcx": {
      "probability": 0.1308,
      "prediction": "Normal",
      "threshold": 0.50,
      "model_family": "XGBoost",
      "calibration": "uncalibrated"
    },
    "rca": {
      "probability": 0.4005,
      "prediction": "Stenotic",
      "threshold": 0.38,
      "model_family": "LogisticRegression",
      "calibration": "sigmoid"
    }
  }
}
```

---

### 2.5 Single-Target SHAP Explanation
* **Endpoint**: `POST /api/v1/explain`
* **Summary**: Patient-Level SHAP Feature Attribution
* **Request**:
```json
{
  "patient": { "...clinical features..." },
  "target": "cath"
}
```
* **Response (200 OK)**:
```json
{
  "target": "cath",
  "explanation_space": "log-odds (model score)",
  "calibration_disclosure": "SHAP values explain the underlying predictive model score (log-odds/margin); probability calibration is applied separately to determine the final visual risk probability.",
  "base_value": -0.1192,
  "features": [
    {
      "feature": "Typical Chest Pain",
      "label": "Typical Anginal Chest Pain",
      "value": 1.0,
      "shap_value": -0.7724,
      "direction": "negative"
    },
    {
      "feature": "Tinversion",
      "label": "T-Wave Inversion (ECG)",
      "value": 1.0,
      "shap_value": 0.4556,
      "direction": "positive"
    }
  ],
  "positive_contributors": [
    {
      "feature": "Tinversion",
      "label": "T-Wave Inversion (ECG)",
      "value": 1.0,
      "shap_value": 0.4556,
      "direction": "positive"
    }
  ],
  "negative_contributors": [
    {
      "feature": "Typical Chest Pain",
      "label": "Typical Anginal Chest Pain",
      "value": 1.0,
      "shap_value": -0.7724,
      "direction": "negative"
    }
  ]
}
```

---

### 2.6 Combined Patient Assessment
* **Endpoint**: `POST /api/v1/analyze`
* **Summary**: Comprehensive Patient Assessment (Prediction + 4-Target SHAP)
* **Request**:
```json
{
  "patient": { "...clinical features..." }
}
```
* **Response (200 OK)**:
```json
{
  "predictions": {
    "cath": { "probability": 0.7657, "prediction": "CAD", "threshold": 0.50, ... },
    "lad": { "probability": 0.5323, "prediction": "Stenotic", "threshold": 0.50, ... },
    "lcx": { "probability": 0.1308, "prediction": "Normal", "threshold": 0.50, ... },
    "rca": { "probability": 0.4005, "prediction": "Stenotic", "threshold": 0.38, ... }
  },
  "explanations": {
    "cath": { ... },
    "lad": { ... },
    "lcx": { ... },
    "rca": { ... }
  },
  "clinical_disclaimer": "Educational and decision-support prototype only. Model predictions are not a diagnosis and do not replace clinical judgment, formal angiography, or diagnostic imaging.",
  "visualization_note": "Predicted vessel probabilities represent model-estimated stenosis risk and are not physical 3D lesion coordinates."
}
```

---

## 3. Standard Error Envelope

All API errors return a standardized JSON structure without exposing internal python tracebacks or directory paths:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Human-readable explanation of the validation failure.",
    "details": []
  }
}
```

### HTTP Status Codes:
* **400 Bad Request (`INVALID_TARGET`)**: Raised when requesting an explanation for an unknown target (e.g., target != `cath`, `lad`, `lcx`, `rca`).
* **422 Unprocessable Content (`INVALID_INPUT`)**:
  * Missing required clinical features.
  * Invalid categorical values (e.g. `Sex: "Other"`).
  * Target leakage detected (input contains `Cath`, `LAD`, `LCX`, or `RCA`).
* **500 Internal Server Error (`INTERNAL_ERROR`)**: Generic safety fallback for unhandled exceptions.
* **503 Service Unavailable (`SERVICE_UNAVAILABLE`)**: Serialized model pipelines failed to load.
