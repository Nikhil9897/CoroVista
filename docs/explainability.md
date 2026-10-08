# CoroVista — Clinical Explainability & Model Interpretability Documentation
**Multimodal AI Hackathon 2026 — Track A: Cardiovascular Risk Visualization & Prediction**

> [!CAUTION]
> **Clinical Safety & Interpretability Disclaimer**  
> SHAP explanations provided by CoroVista are intended solely for model interpretability, educational exploration, and clinical decision-support research. Feature attributions reflect associative statistical patterns learned by predictive algorithms within this dataset; they **do not establish clinical causality** and **do not replace clinical judgment, formal diagnostic coronary angiography, or professional cardiovascular imaging**. Crucially, predicted vessel-level probabilities and Regional Wall Motion Abnormalities (RWMA) must **never be interpreted as physical 3D lesion coordinates or plaque locations**.

---

## 1. Why SHAP (SHapley Additive exPlanations) is Used

In clinical decision support, "black-box" model outputs are unacceptable for patient risk stratification. Clinicians must understand *why* an algorithm estimates an elevated probability of coronary stenosis.

CoroVista incorporates **SHAP** based on cooperative game theory (Shapley values):
- **Local Accuracy / Additivity**: For every patient, the sum of feature attributions plus the model base value exactly equals the model's raw output score:
  $$\sum_{j=1}^{M} \phi_j(x) + E[f(X)] = f(x)$$
- **Consistency**: Features that reliably elevate predicted risk across patients receive higher importance values without inversion artifacts.
- **Directional Transparency**: Distinguishes risk-elevating factors (e.g., severe dyspnea, pathological Q waves) from protective factors (e.g., high ejection fraction, normal conduction).

---

## 2. Models Explained & Explainer Implementations

The four final locked models from Stage 2 are explained using tailored, mathematically exact explainers:

| Target | Clinical Endpoint | Underlying Model Architecture | Explainer Strategy | Explanation Space |
|---|---|---|---|---|
| **Cath** | Overall CAD Status | `XGBoost` (wrapped in `CalibratedClassifierCV`, 3 folds) | Exact Tree SHAP via XGBoost Core, ensemble-averaged across 3 calibrated fold estimators | Log-Odds (Model Margin) |
| **LAD** | Left Anterior Descending | `XGBoost` (wrapped in `CalibratedClassifierCV`, 3 folds) | Exact Tree SHAP via XGBoost Core, ensemble-averaged across 3 calibrated fold estimators | Log-Odds (Model Margin) |
| **LCX** | Left Circumflex | `XGBoost` (Uncalibrated, cost-weighted) | Exact Tree SHAP via XGBoost Core | Log-Odds (Model Margin) |
| **RCA** | Right Coronary Artery | `Logistic Regression` (wrapped in `CalibratedClassifierCV`, 3 folds) | Exact Linear SHAP via `shap.LinearExplainer`, ensemble-averaged across 3 calibrated fold estimators | Log-Odds (Linear Score) |

---

## 3. Explanation Space & Probability Calibration Behavior

### The Distinction Between Model Score & Calibrated Probability
For calibrated models (`Cath`, `LAD`, and `RCA`), probability calibration via Platt scaling (Sigmoid) is applied on top of the underlying classifier:
- **Base Estimator Output ($f(x)$)**: Evaluated in unconstrained continuous log-odds space ($\mathbb{R}$). Tree SHAP and Linear SHAP operate directly in this log-odds space to preserve exact additivity and mathematical consistency.
- **Calibrated Probability ($P(Y=1|x)$)**: Computed by passing $f(x)$ through the post-hoc sigmoid calibration mapping:
  $$P(Y=1|x) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$

> [!IMPORTANT]
> **Calibration Disclosure Contract**  
> CoroVista's explanation metadata explicitly states:  
> *"SHAP values explain the underlying predictive model score (log-odds / margin); probability calibration is applied separately to determine the final visual risk probability."*  
> Falsely claiming that raw additive SHAP values sum directly to the non-linear sigmoid probability is mathematically incorrect; CoroVista maintains strict scientific precision by explaining the decision margin and reporting calibrated risk separately.

---

## 4. Preprocessing & Transformed Feature Mapping

Raw patient records undergo pipeline transformations before entering the estimator:
1. **One-Hot Encoding**: Categorical variables (`BBB`, `VHD`) are transformed into indicator features (`BBB_N`, `BBB_RBBB`, `VHD_Mild`, `VHD_Moderate`, `VHD_Severe`).
2. **Deterministic Cleaning**: Typographical anomalies (e.g., `'Fmale'`) and casing inconsistencies (`'mild'`) are normalized prior to transformation.
3. **Feature Mapping**: CoroVista automatically maps every transformed feature back to human-readable clinical labels with units:
   - `EF-TTE` → `Left Ventricular Ejection Fraction (% Echo)`
   - `Typical Chest Pain` → `Typical Anginal Chest Pain`
   - `BBB_RBBB` → `Right Bundle Branch Block (ECG)`
   - `Region RWMA` → `Regional Wall Motion Abnormality Count (Echo)`
   - `FBS` → `Fasting Blood Sugar (mg/dL)`

Transformed names like `cat__BBB_RBBB` or `num__Age` are never exposed to the end user.

---

## 5. Separation of Risk Probability & Discrete Classification

CoroVista strictly separates continuous predicted probability from binary classification:
- **Continuous Probability ($P \in [0.0, 1.0]$)**: Directly controls vessel risk color and visual intensity on the interactive 3D coronary anatomy model (e.g., LAD risk = $0.5323$, RCA risk = $0.4005$).
- **Discrete Classification Label**: Determined by evaluating whether the probability meets or exceeds the target-specific decision threshold:
  - `Cath`: Threshold = $0.50$ (`CAD` vs `Normal`)
  - `LAD`: Threshold = $0.50$ (`Stenotic` vs `Normal`)
  - `LCX`: Threshold = $0.50$ (`Stenotic` vs `Normal`)
  - `RCA`: Threshold = $0.38$ (`Stenotic` vs `Normal`)

*Example*: If a patient has an RCA probability of $0.42$, the 3D heart displays a moderate risk color corresponding to $0.42$, while the discrete label correctly reports `Stenotic` because $0.42 \ge 0.38$.

---

## 6. Population-Level Global Explanations (Cohort Summary)

Population-level feature importances across all 303 cohort patients are computed and exported to:
- Machine-readable JSON: [`data/reports/shap_global.json`](file:///c:/Users/agnik/OneDrive/Desktop/CoroVista/data/reports/shap_global.json)
- Summary Visualizations:
  - Cath: [`data/reports/shap/cath_summary.png`](file:///c:/Users/agnik/OneDrive/Desktop/CoroVista/data/reports/shap/cath_summary.png)
  - LAD: [`data/reports/shap/lad_summary.png`](file:///c:/Users/agnik/OneDrive/Desktop/CoroVista/data/reports/shap/lad_summary.png)
  - LCX: [`data/reports/shap/lcx_summary.png`](file:///c:/Users/agnik/OneDrive/Desktop/CoroVista/data/reports/shap/lcx_summary.png)
  - RCA: [`data/reports/shap/rca_summary.png`](file:///c:/Users/agnik/OneDrive/Desktop/CoroVista/data/reports/shap/rca_summary.png)

### Key Population Drivers:
- **Cath**: Primary drivers are `Typical Anginal Chest Pain`, `T-Wave Inversion (ECG)`, `Left Ventricular Ejection Fraction (EF-TTE)`, and `Age`.
- **LAD**: Dominated by `Typical Chest Pain`, `Regional Wall Motion Abnormality (Echo)`, `EF-TTE`, and `T-Wave Inversion`.
- **LCX**: Primary drivers include `Age`, `Systolic Blood Pressure`, `Typical Chest Pain`, and `Serum Creatinine`.
- **RCA**: Dominated by `Typical Chest Pain`, `Diabetes Mellitus History`, `Age`, and `Erythrocyte Sedimentation Rate (ESR)`.

---

## 7. Patient-Level Explanation API Contract

Clinicians or the frontend UI query patient-level explanations via `explain_patient(features, target="cath")`:

```json
{
  "target": "cath",
  "explanation_space": "log-odds (model score)",
  "calibration_note": "SHAP values explain the underlying predictive model score (log-odds/margin); probability calibration is applied separately to determine the final visual risk probability.",
  "base_value": -0.1192,
  "model_family": "XGBoost",
  "calibration_method": "sigmoid",
  "features": [
    {
      "feature": "Typical Chest Pain",
      "label": "Typical Anginal Chest Pain",
      "value": 1.0,
      "shap_value": 0.7724,
      "direction": "positive"
    },
    {
      "feature": "EF-TTE",
      "label": "Left Ventricular Ejection Fraction (% Echo)",
      "value": 45.0,
      "shap_value": 0.3438,
      "direction": "positive"
    },
    {
      "feature": "Age",
      "label": "Patient Age (years)",
      "value": 65.0,
      "shap_value": -0.1331,
      "direction": "negative"
    }
  ]
}
```

Features are sorted strictly by $|\phi_j|$ descending. Helper functions `top_positive_contributors(n=5)` and `top_negative_contributors(n=5)` filter actionable risk elevators and protective indicators for frontend card rendering.

---

## 8. Limitations & Clinical Interpretation Boundaries

1. **Non-Causal Associations**: SHAP values indicate feature contributions to the statistical model's mathematical output; they do not imply that modifying a clinical parameter (e.g., lowering heart rate) will directly modify coronary stenosis pathology.
2. **Anatomical Boundary**: Predictions represent **vessel-level luminal narrowing probability (≥50% stenosis)** across LAD, LCX, and RCA. The dataset does not provide 3D spatial lesion coordinates; hence, visual representations are vessel branch risk colorings, not physical lesion sites.
3. **Cohort Representation**: The models were trained and cross-validated on an Iranian cardiology cohort ($N = 303$) referred for catheterization. Generalization to primary prevention or community screening populations requires prospective multi-center calibration.
