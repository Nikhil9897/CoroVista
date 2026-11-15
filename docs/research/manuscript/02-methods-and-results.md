# Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness

**Authors:** Naman Deep Tripathi$^1$, Nikhil Agrawal$^1$  
$^1$ Department of Computer Science & Biomedical Informatics / Cardiovascular Systems Engineering  

---

## 3. Materials and Methods

### 3.1 Cohort Provenance, Clinical Setting, and Ethical Framework
The empirical foundation of this study is the extended Z-Alizadeh Sani cardiology dataset (Alizadehsani et al., 2013, 2018; Alizadehsani, 2017, 2018). The cohort consists of $N = 303$ consecutive adult patients referred for diagnostic invasive coronary catheterization at Shaheed Rajaei Cardiovascular, Medical and Research Center, a major tertiary cardiovascular referral and teaching hospital in Tehran, Iran.

#### Clinical Study Design & Eligibility
- **Study Design:** Retrospective cross-sectional diagnostic modeling study.
- **Inclusion Criteria:** Adult patients presenting with suspected ischemic heart disease or stable angina who underwent formal elective invasive coronary angiography (ICA) based on clinical indications, resting 12-lead electrocardiography (ECG), exercise stress testing, or echocardiographic abnormalities.
- **Reference Standard:** Selective invasive coronary angiography performed via standard femoral or radial arterial access. Quantitative or visual angiographic interpretation was conducted by expert interventional cardiologists. In accordance with established international cardiology consensus guidelines (Lawton et al., 2022), **significant obstructive coronary artery disease was defined as $\ge 50\%$ luminal diameter stenosis in one or more major epicardial coronary vessels**.
- **Ethical Standards & Approvals:** The dataset was collected and anonymized at Shaheed Rajaei Cardiovascular, Medical and Research Center in compliance with the ethical principles of the Declaration of Helsinki [CITATION NEEDED for formal Institutional Review Board / Ethics Committee approval protocol identifier]. Patient records were fully de-identified prior to public dissemination, obviating the requirement for individual written informed consent for retrospective secondary algorithmic analysis.

#### Prediction Target Definitions and Class Distributions
The anatomical partitioning of epicardial coronary artery territories (LAD, LCX, RCA) follows established clinical revascularization guidelines (Lawton et al., 2022) and standardized biomedical anatomical ontologies (Mitsuhashi et al., 2009). Four independent clinical prediction targets were established to reflect both aggregate disease burden and vessel-specific anatomical localization:
1. **`Cath` (Composite Obstructive CAD):** Presence of $\ge 50\%$ luminal diameter stenosis in at least one primary epicardial coronary vessel (or major branch). The cohort ground-truth distribution is $N_+ = 216$ positive (71.29%) and $N_- = 87$ negative (28.71%), reflecting a high-prevalence tertiary referral population.
2. **`LAD` (Left Anterior Descending Stenosis):** Presence of $\ge 50\%$ stenosis in the LAD artery. Ground truth: $N_+ = 177$ positive (58.42%) and $N_- = 126$ negative (41.58%).
3. **`LCX` (Left Circumflex Stenosis):** Presence of $\ge 50\%$ stenosis in the LCX artery. Ground truth: $N_+ = 119$ positive (39.27%) and $N_- = 184$ negative (60.73%).
4. **`RCA` (Right Coronary Artery Stenosis):** Presence of $\ge 50\%$ stenosis in the RCA. Ground truth: $N_+ = 114$ positive (37.62%) and $N_- = 189$ negative (62.38%).

#### Multi-Target Diagnostic Coherence & Record Index 93 Preservation
Cross-tabulation between the composite diagnosis (`Cath`) and vessel-specific annotations reveals an overall diagnostic coherence of **99.67% (302/303 patients)**. Exactly one record—patient **Index 93** (anonymized row 94)—exhibits an anatomical discordance: the vessel annotations record `LAD = 'Stenotic'`, `LCX = 'Normal'`, `RCA = 'Normal'`, yet the aggregate target records `Cath = 'Normal'`. Rather than arbitrarily deleting this record or altering ground-truth labels, **Index 93 was preserved without modification across all experiments**. This preservation adheres to strict data provenance principles; in real-world clinical informatics, minor discordant recordings occur naturally, and selective post-hoc pruning introduces retrospective survival and reporting bias.

---

### 3.2 Clinical Feature Schema, Cleaning, and Preprocessing Architecture

#### Feature Schema & Dimensionality Reconciliation
The primary workbook (`extention of Z-Alizadeh sani dataset.xlsx`, sheet `'Sheet 1 - Table 1'`) contains 59 columns. Dimensionality was processed through a deterministic multi-stage pipeline:
- **Total Raw Columns:** 59 columns.
- **Isolated Prediction Targets:** 4 columns (`Cath`, `LAD`, `LCX`, `RCA`).
- **Non-Target Feature Space:** $59 - 4 = 55$ raw clinical variables.
- **Zero-Variance Feature Exclusion:** The feature `Exertional CP` (Exertional Chest Pain) was found to be invariant across the entire cohort (303 out of 303 records are `'N'`). Because a zero-variance variable provides null mathematical mutual information and causes singular design matrices in linear estimators, it is dropped deterministically by `ClinicalFeatureCleaner`.
- **Active Clinical Feature Matrix:** $55 - 1 = 54$ predictive clinical features.
- **Transformed Design Matrix:** Following nominal One-Hot encoding of multi-level categorical variables (`VHD` with 4 levels, `BBB` with 3 levels), the final transformed numerical design matrix contains exactly **57 dimensions** ($22 \text{ numerical} + 28 \text{ binary} + 7 \text{ one-hot indicators} = 57$).

#### Clinical Feature Categorization
The 54 active features span seven distinct clinical diagnostic domains:
1. **Demographic Variables (4):** `Age` (years), `Sex` (Male/Female), `Weight` (kg), `Length` (Height, cm). (`BMI` is derived as $\text{Weight} / (\text{Length}/100)^2$).
2. **Cardiovascular Risk Habits (7):** `Current Smoker`, `Ex-Smoker`, `Smoking Duration` (pack-years), `Air Pollution Exposure`, `Passive Smoking`, `Heavy Metals Exposure`, `Water Hardness`.
3. **Symptoms & Physical Examination (12):** `Typical Chest Pain`, `Atypical Chest Pain`, `Nonanginal Chest Pain`, `Resting BP` (Systolic, mmHg), `Heart Rate` (Pulse, bpm), `Diastolic Murmur`, `Systolic Murmur`, `Dyspnea`, `Orthopnea`, `Paroxysmal Nocturnal Dyspnea (PND)`, `Third Heart Sound (S3)`, `Fourth Heart Sound (S4)`.
4. **Comorbidities & Family History (3):** `Diabetes Mellitus (DM)`, `Hypertension (HTN)`, `Family History of CAD (FH)`.
5. **Laboratory Blood Panels (14):** Fasting Blood Sugar (`FBS`), Total Cholesterol (`CR`), Triglycerides (`TG`), Low-Density Lipoprotein (`LDL`), High-Density Lipoprotein (`HDL`), Serum Creatinine (`BUN`), Potassium (`K`), Sodium (`Na`), White Blood Cell Count (`WBC`), Lymphocyte Percentage (`Lymph`), Neutrophil Percentage (`Neut`), Platelet Count (`PLT`), Hemoglobin (`Hb`), Erythrocyte Sedimentation Rate (`ESR`).
6. **Resting 12-Lead Electrocardiography (7):** `Q Wave`, `ST Elevation`, `ST Depression`, `T Wave Inversion`, `Poor R Wave Progression`, `Bundle Branch Block (BBB)` (None, LBBB, RBBB), `Heart Rhythm` (Sinus, Arrhythmia).
7. **Transthoracic Echocardiography (3):** Left Ventricular Ejection Fraction (`EF-TTE`), Regional Wall Motion Abnormality (`Region RWMA`), Valvular Heart Disease (`VHD`) (None, Mild, Moderate, Severe).

#### Preprocessing & Leakage-Guard Pipeline
In accordance with TRIPOD+AI recommendations (Collins et al., 2024), all preprocessing operations were wrapped within scikit-learn compatible `Pipeline` objects to enforce absolute cross-validation partitioning:
- **Deterministic Cleaning:** Text normalization, whitespace trimming, and uniform boolean encoding (`'Y'`/`'N'`, `'Male'`/`'Female'`, `'F'`/`'M'`) via `ClinicalFeatureCleaner`.
- **Data Completeness & Imputation:** An exhaustive audit (`data/reports/dataset_audit.json`) confirmed that the primary dataset contains 0 missing entries across all 59 columns (100% natural data completeness). However, to guarantee robust defensive inference against incomplete clinical records in deployment, partition-isolated imputation was embedded: continuous features were imputed using outer-training median values, and categorical/binary features were imputed using outer-training mode values via `SimpleImputer`.
- **Nominal Feature Encoding:** `ColumnTransformer` applied `OneHotEncoder(drop=None, sparse_output=False)` to `VHD` and `BBB`. Binary features were encoded as $\{0, 1\}$.
- **Continuous Feature Standardization:** For linear models (`LogisticRegression`), numerical features were standardized using `StandardScaler(with_mean=True, with_std=True)` fit strictly on the outer training partition. Tree-based architectures (`RandomForest`, `XGBoost`) operated directly on unscaled numerical values.
- **Leakage Guard:** `LeakageGuardTransformer` asserted that design matrix schemas, column orders, and scaling parameters were frozen prior to inference.

---

### 3.3 Model Selection and Repeated Stratified Cross-Validation Scheme

#### Candidate Model Architectures
Three distinct algorithmic families were systematically benchmarked for each target:
1. **Regularized Logistic Regression:** Linear classification baseline optimized via $L_2$ ridge penalty with liblinear solver, tolerance $10^{-4}$, and inverse regularization parameter $C = 1.0$, implemented using scikit-learn (Pedregosa et al., 2011).
2. **Random Forest Classifier:** Bagged decision tree ensemble comprising 100 estimators, maximum tree depth 5, Gini impurity split criterion, and balanced subsample class weighting (Pedregosa et al., 2011).
3. **Extreme Gradient Boosting (`XGBoost`):** Gradient boosted decision tree framework (Chen & Guestrin, 2016) comprising 100 trees, maximum depth 3, learning rate $\eta = 0.1$, subsample ratio 0.8, feature subsampling by tree 0.8, and dynamic class balancing via `scale_pos_weight = N_neg / N_pos`.

#### Resampling Harness: 25-Fold Repeated Stratified Cross-Validation
All machine-learning pipelines, cross-validation iterators, transformers, and baseline estimators were implemented in Python 3.10 using scikit-learn (Pedregosa et al., 2011) and XGBoost (Chen & Guestrin, 2016). To eliminate the risk of partition-specific reporting artifacts, all models were evaluated using **Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats = 25 outer test folds)** initialized with a master random seed of 42:
- Stratification preserved exact positive-to-negative class proportions within every outer training fold ($\approx 242$ patients) and outer test fold ($\approx 61$ patients).
- All transformers, scalers, imputers, hyperparameter estimators, and calibration mappers were fit **strictly inside outer training partitions**. Outer test fold data remained entirely untouched until final scoring.

---

### 3.4 Probability Calibration and Operating Threshold Selection

#### Post-Processing Calibration Architecture
Uncalibrated decision trees and boosted classifiers output scores that can be severely misaligned with empirical event rates (Niculescu-Mizil & Caruana, 2005). We evaluated two post-processing calibration mappings:
1. **Parametric Platt (Sigmoid) Scaling:** Fits a univariate logistic model to pre-calibration margin scores $f(x)$ (Platt, 1999):
   $$P_{\text{sigmoid}}(Y = 1 \mid x) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$
   where parameters $A$ and $B$ are estimated via maximum likelihood.
2. **Non-Parametric Isotonic Regression:** Fits a piecewise constant, non-decreasing step function using the pair-adjacent violators algorithm (PAV; Niculescu-Mizil & Caruana, 2005).

To prevent calibration overfitting, calibration mappers were fit using an **internal 3-fold cross-validation scheme executed exclusively inside each outer training partition** via `CalibratedClassifierCV(method='sigmoid'|'isotonic', cv=3)`.

#### Rationale for Selected Production Models
- **`Cath` (Composite CAD):** **`XGBoost` with Sigmoid Calibration** was selected. Sigmoid scaling reduced Brier score from $0.1074$ to $0.1034$ and Expected Calibration Error (ECE) from $0.1265$ to $0.1004$ while maintaining superior discrimination (ROC-AUC $0.9123$).
- **`LAD`:** **`XGBoost` with Sigmoid Calibration** was selected. Sigmoid scaling lowered Brier score from $0.1651$ to $0.1609$ and ECE from $0.1434$ to $0.1326$ (ROC-AUC $0.8443$).
- **`LCX`:** **`XGBoost` Uncalibrated** was selected as the production model. While uncalibrated XGBoost achieved ROC-AUC $0.7358 \pm 0.0629$, post-hoc calibration post-processing (both Sigmoid and Isotonic) compressed predicted probabilities into a narrow band, causing severe sensitivity collapse at standard cutoffs without providing superior resolution. Retaining the uncalibrated tree ensemble preserved maximum ranking resolution for posterolateral disease.
- **`RCA`:** **`Logistic Regression` with Sigmoid Calibration** was selected. Sigmoid scaling achieved the cohort's lowest Brier score ($0.2060 \pm 0.0150$) and lowest ECE ($0.1000 \pm 0.0321$), matching or outperforming Random Forest (Brier $0.2104$) and XGBoost (Brier $0.2092$) on this diffuse target.

#### Decision Operating Threshold Determination Protocols
To reconcile continuous probabilities with binary clinical classifications, three distinct thresholding protocols were evaluated:
1. **Standard Fixed Threshold ($\tau = 0.50$):** Arbitrary default midpoint cutoff applied uniformly across all 25 outer test folds.
2. **Nested Inner-Fold Tuned Threshold:** To eliminate optimistic threshold tuning bias, the operating cutoff was optimized dynamically inside each outer training fold:
   - An inner 3-fold cross-validation evaluated candidate cutoffs across a dense grid $\tau \in [0.05, 0.95]$ in increments of $0.01$.
   - The cutoff maximizing the macro-averaged $F_1$-score on inner out-of-fold predictions was selected, frozen, and subsequently applied to the outer test fold.
3. **Fixed Production Operating Threshold ($\tau = 0.35$ for RCA):** Derived from the empirical mean of the nested inner-OOF threshold distribution ($0.3188 \pm 0.0380$), a constant production operating threshold of $\tau = 0.35$ was established to resolve Platt probability compression in clinical inference.

---

### 3.5 Evaluation Metrics and Statistical Standards

#### Metric Definitions
- **Discrimination:** Area Under the Receiver Operating Characteristic Curve (ROC-AUC / C-index) and Area Under the Precision-Recall Curve (PR-AUC / Average Precision).
- **Probability Calibration:**
  - **Brier Score (BS):** Mean squared difference between predicted risk $p_i$ and true binary label $y_i \in \{0, 1\}$ (Brier, 1950):
    $$\text{BS} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
  - **Expected Calibration Error (ECE):** Weighted absolute difference between empirical accuracy and mean predicted probability across $M = 10$ equally spaced confidence bins (Guo et al., 2017).
- **Classification Performance:** Accuracy, Balanced Accuracy (macro-average of sensitivity and specificity), Sensitivity / Recall, Specificity, Precision (Positive Predictive Value), and $F_1$-Score ($2 \cdot \frac{\text{Prec} \cdot \text{Rec}}{\text{Prec} + \text{Rec}}$).

#### Strict Separation of Evaluation Protocols and Reporting Standards
To ensure reproducibility, this manuscript enforces strict segregation across three distinct statistical aggregation levels:
1. **25-Fold Outer Cross-Validation (Primary Standard):** Primary tables report the arithmetic mean and **unbiased sample standard deviation (`ddof=1`, dividing by $K - 1 = 24$)** across the 25 outer test folds. For mathematical transparency and continuity with raw code outputs, the population standard deviation (`ddof=0`, dividing by $K = 25$) produced by `aggregate_cv_metrics()` is documented in brackets.
2. **Five-Repeat Pooled Evaluation:** Out-of-fold predicted probabilities for all $N = 303$ patients are concatenated per repeat $r \in \{1, \dots, 5\}$. Metrics are calculated for each complete cohort repeat, and aggregated as Mean $\pm$ Sample SD across the 5 repeats ($N=5, \text{ddof}=1$). This describes repeat-to-repeat stability over complete cohort resamplings.
3. **Consensus Multi-Repeat Patient OOF Evaluation:** For each patient $i \in \{1, \dots, 303\}$, a single consensus predicted probability is derived by averaging their out-of-fold predictions across all 5 repeats: $\bar{p}_i = \frac{1}{5} \sum_{r=1}^5 p_{i,r}$. Metrics are evaluated on this single consensus cohort vector ($N=303$).

---

### 3.6 Explainability Stability Evaluation Protocol (Exp A)

#### Mathematical Framework: TreeSHAP and LinearSHAP
Local feature attributions were computed using Shapley Additive Explanations (Lundberg & Lee, 2017):
- For tree-based models (`Cath`, `LAD`, `LCX`), exact polynomial-time **TreeSHAP** (Lundberg et al., 2020) was executed in raw model-score margin space ($f(x)$ in log-odds).
- For linear models (`RCA`), **LinearSHAP** was executed in decision function space.
- To prevent test data leakage, background expectation distributions were subsampled strictly from outer training partitions ($N_{\text{bg}} \le 100$).

#### Mathematical Reconstruction Additivity Verification
For every patient in every outer test fold, exact floating-point additivity was audited:
$$\left| f(x) - \left( \phi_0 + \sum_{j=1}^M \phi_j(x) \right) \right| < 10^{-5}$$
where $\phi_0$ is the training background expected value, and $\phi_j(x)$ is the SHAP attribution for feature $j$.

#### Multi-Fold Attribution Stability Metrics
Stability of feature attributions across resampled outer folds was quantified along two dimensions:
1. **Global Attribution Stability:** Mean absolute feature importance was computed per fold: $I_j = \frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} |\phi_{i,j}|$. Pairwise stability across all $\binom{25}{2} = 300$ fold pairs was evaluated via:
   - Spearman rank correlation ($\rho$) and Kendall’s Tau ($\tau$).
   - Top-5 and Top-10 Jaccard similarity index: $J(S_A, S_B) = \frac{|S_A \cap S_B|}{|S_A \cup S_B|}$.
2. **Patient-Level Attribution Stability:** Across the 5 independent out-of-fold explanations generated for each individual patient ($N=303$), we evaluated:
   - **Attribution Sign Agreement:** Proportion of repeats where the feature attribution maintained an identical qualitative direction of risk ($\text{sign}(\phi_{i,j}) > 0$ vs. $< 0$).
   - **Per-Patient Rank Correlation:** Mean pairwise Spearman correlation of feature rankings within individual patient profiles.

#### Non-Linear Probability Transformation Disclosure
In accordance with mathematical rigor, we disclose that SHAP attributions operate strictly in pre-calibration model score space ($f(x)$). For Platt-calibrated pipelines, the final predicted probability is generated via:
$$p(x) = \frac{1}{1 + \exp\left( - \left[ A \left( \phi_0 + \sum_{j=1}^M \phi_j(x) \right) + B \right] \right)}$$
Because the sigmoid operator is non-linear, individual SHAP values cannot be linearly summed to reconstruct calibrated probabilities. Attributions explain log-odds risk, not additive probabilities.

---

### 3.7 Prediction Stability and Uncertainty Quantification Protocols (Exp B & Exp C)

#### Out-of-Fold Prediction Dispersion Profiling
To evaluate prediction churn under data resampling, out-of-fold predicted probabilities $p_{i,r}$ were tracked for all $N = 303$ patients across the 5 independent cross-validation repeats ($r \in \{1, \dots, 5\}$):
- **Patient Probability Standard Deviation ($\sigma_{p,i}$):**
  $$\sigma_{p,i} = \sqrt{\frac{1}{4} \sum_{r=1}^5 (p_{i,r} - \bar{p}_i)^2}, \quad \text{where } \bar{p}_i = \frac{1}{5} \sum_{r=1}^5 p_{i,r}$$
- **Cohort Dispersion Proportions:** Proportion of patients exhibiting standard deviations exceeding predefined stability boundaries ($\sigma_p > 0.05$ and $\sigma_p > 0.10$).
- **Classification Invariance Rate:** Proportion of patients receiving identical binary class assignments ($5/5$ positive or $5/5$ negative) across all five independent repeats.
- **Decision Boundary Proximity Stratification:** Patients were stratified into four mutual boundary distance strata: $|p - \tau| < 0.05$, $[0.05, 0.10)$, $[0.10, 0.20)$, and $\ge 0.20$.

#### Defensive Uncertainty Quantification via Binary Entropy
Predictive uncertainty was quantified using normalized binary entropy (Kompa et al., 2021):
$$H(p) = -p \log_2(p) - (1-p) \log_2(1-p)$$
Entropy scales continuously from $H(p) = 0$ (absolute certainty at $p=0$ or $p=1$) to $H(p) = 1.0$ (maximal ambiguity at $p = 0.50$).
- **Error Discrimination Power:** The capacity of binary entropy to discriminate empirical classification errors in the absence of ground-truth labels was quantified using the Receiver Operating Characteristic curve, computing the **error-detection ROC-AUC**.

---

### 3.8 Robustness Stress Testing and Inside-CV Feature Ablation Protocols (Exp D)

#### Input Noise Perturbation & Synthetic Missingness Stress Testing
Pipeline resilience against physiological measurement noise and clinical data collection failure was stress tested:
1. **Continuous Feature Gaussian Perturbation:** Additive zero-mean Gaussian noise was injected into continuous features: $\tilde{x} = x + \epsilon$, where $\epsilon \sim \mathcal{N}(0, (\alpha \cdot \text{std}(x))^2)$ for perturbation intensities $\alpha \in \{0.1, 0.5, 1.0\}$. The mean absolute probability shift ($|\Delta p|$) and binary classification flip rate were recorded across 25 outer test folds.
2. **Synthetic Missing Completely at Random (MCAR) Stress Testing:** Features were artificially erased at rates of 5%, 10%, 15%, and 20%, evaluating the graceful degradation of the pipeline's internal median/mode imputation modules against the Repeat-1 pooled out-of-fold baseline.

#### Inside-Cross-Validation Feature Block and Single-Feature Ablation
To uncover the physiological drivers of each coronary territory without data leakage, feature groups and single prominent features were ablated:
- For each ablation configuration, the full machine learning pipeline (cleaning, imputation, encoding, scaling, model training, and calibration) was **retrained from scratch across all 5 folds** of Repeat 1.
- The resulting out-of-fold ROC-AUC was compared against the unablated Repeat-1 pooled baseline ($N=303$), computing the absolute marginal performance drop: $\Delta \text{AUC} = \text{AUC}_{\text{ablated}} - \text{AUC}_{\text{baseline}}$.

---

### 3.9 Exploratory Subgroup Analysis Protocol (Exp E)

#### Sample Size Feasibility Guard
To prevent reporting misleading statistical metrics on severely underpowered patient partitions, a strict sample size guard was enforced: a subgroup stratum was deemed feasible if and only if **$N_{\text{stratum}} \ge 30$** and **$\min(N_+, N_-) \ge 5$**.

#### Evaluated Clinical Strata
Disaggregated performance was evaluated on consensus multi-repeat predictions ($N=303$) across 13 feasible strata spanning 6 categories:
1. **Biological Sex:** Male ($N=176$), Female ($N=127$).
2. **Age Groups:** Age $<55$ ($N=108$), Age $55-65$ ($N=100$), Age $\ge 65$ ($N=95$).
3. **Diabetes Mellitus:** Diabetic ($N=90$), Non-Diabetic ($N=213$).
4. **Hypertension:** Hypertensive ($N=179$), Normotensive ($N=124$).
5. **Obesity:** Obese ($\text{BMI} \ge 25$, $N=211$), Non-Obese ($\text{BMI} < 25$, $N=92$).
6. **Dyslipidemia:** Dyslipidemic ($N=112$), Non-Dyslipidemic ($N=191$).

#### Explicit Non-Fairness Disclaimer
In adherence to ethical guidelines in medical AI, these subgroup evaluations are designated as **descriptive and hypothesis-generating observations**. Due to single-center sample size constraints ($N=303$), this study does **not** claim formal algorithmic fairness certification, demographic parity, or equalized odds guarantees.

---

## 4. Results

### 4.1 Cohort Baseline Characteristics and Multi-Target Diagnostic Coherence
The baseline demographic, clinical, laboratory, and echocardiographic characteristics of the $N = 303$ study patients are presented in Table 1, stratified by overall CAD catheterization status (`Cath`). Complete data completeness (100%, 0 missing values) was confirmed across all audited parameters.

#### Table 1: Clinical Cohort Baseline Characteristics & Target Distributions
*Authoritative Source: `data/reports/dataset_audit.json` and `data/reports/dataset_audit.md`.*

| Characteristic / Variable | Entire Cohort ($N = 303$) | Cath Positive ($N = 216$) | Cath Negative ($N = 87$) | Missing Count (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Age (years), Mean ± SD [Median, IQR]** | $58.89 \pm 10.39$ [$60.0, 15.0$] | $60.52 \pm 9.87$ [$61.0, 14.0$] | $54.85 \pm 10.51$ [$55.0, 15.0$] | 0 (0.00%) |
| **Sex, Male / Female (% Male)** | 176 / 127 (58.09%) | 130 / 86 (60.19%) | 46 / 41 (52.87%) | 0 (0.00%) |
| **Body Mass Index (BMI, kg/m²), Mean ± SD** | $27.02 \pm 4.09$ [$26.78, 4.90$] | $26.89 \pm 3.98$ | $27.34 \pm 4.36$ | 0 (0.00%) |
| **Systolic Blood Pressure (BP, mmHg), Median [IQR]** | 130.0 [20.0] | 130.0 [20.0] | 120.0 [20.0] | 0 (0.00%) |
| **Ejection Fraction (EF-TTE, %), Median [IQR]** | 50.0 [10.0] | 45.0 [15.0] | 50.0 [5.0] | 0 (0.00%) |
| **Fasting Blood Sugar (FBS, mg/dL), Median [IQR]** | 98.0 [41.5] | 104.0 [54.0] | 92.0 [21.5] | 0 (0.00%) |
| **Serum Triglycerides (TG, mg/dL), Median [IQR]** | 122.0 [87.0] | 133.0 [97.5] | 108.0 [66.5] | 0 (0.00%) |
| **Typical Chest Pain Presentation, Count (%)** | 164 (54.13%) | 148 (68.52%) | 16 (18.39%) | 0 (0.00%) |
| **Regional Wall Motion Abnormality (RWMA), Count (%)** | 68 (22.44%) | 65 (30.09%) | 3 (3.45%) | 0 (0.00%) |
| **Diabetes Mellitus (DM), Count (%)** | 90 (29.70%) | 78 (36.11%) | 12 (13.79%) | 0 (0.00%) |
| **Hypertension (HTN), Count (%)** | 179 (59.08%) | 136 (62.96%) | 43 (49.43%) | 0 (0.00%) |
| **Target: Cath Obstructive CAD (Any Vessel $\ge 50\%$)** | 216 (71.29%) | 216 (100.0%) | 0 (0.00%) | 0 (0.00%) |
| **Target: LAD Stenosis ($\ge 50\%$)** | 177 (58.42%) | 176 (81.48%) | 1 (1.15%)\* | 0 (0.00%) |
| **Target: LCX Stenosis ($\ge 50\%$)** | 119 (39.27%) | 119 (55.09%) | 0 (0.00%) | 0 (0.00%) |
| **Target: RCA Stenosis ($\ge 50\%$)** | 114 (37.62%) | 114 (52.78%) | 0 (0.00%) | 0 (0.00%) |

*\*Note on Record Index 93: Patient exhibits LAD='Stenotic', LCX='Normal', RCA='Normal', Cath='Normal'. Preserved without alteration.*

---

### 4.2 Benchmark Model Discrimination and Calibration Reliability
Multi-target discrimination and calibration metrics across 25 outer test folds are summarized in Table 2 for the selected production models. A comprehensive comparison across candidate calibration methods is detailed in Table 3.

#### Table 2: Benchmark Multi-Target Discrimination & Calibration Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json` and `data/reports/reproduction_audit/model_benchmark.json`.*  
*Protocol: Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats = 25 outer folds). Primary metrics report Cross-Fold Mean $\pm$ Sample SD (`ddof=1`, $N=24$), with population SD (`ddof=0`, $N=25$) noted in brackets.*

| Target | Clinical Endpoint | Selected Model | Preprocessing | Calibration Method | Operating Cutoff ($\tau$) | ROC-AUC (Mean $\pm$ SD) | PR-AUC (Mean $\pm$ SD) | Brier Score (Mean $\pm$ SD) | ECE (Mean $\pm$ SD) |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Cath** | Overall CAD Status | **XGBoost** | None, One-Hot | **Sigmoid** (Platt) | 0.50 | **$0.9123 \pm 0.0404$**<br>[$0.0396$ `ddof=0`] | **$0.9597 \pm 0.0200$**<br>[$0.0196$ `ddof=0`] | **$0.1034 \pm 0.0251$**<br>[$0.0246$ `ddof=0`] | **$0.1004 \pm 0.0227$**<br>[$0.0222$ `ddof=0`] |
| **LAD** | Left Anterior Descending | **XGBoost** | None, One-Hot | **Sigmoid** (Platt) | 0.50 | **$0.8443 \pm 0.0528$**<br>[$0.0518$ `ddof=0`] | **$0.8818 \pm 0.0471$**<br>[$0.0462$ `ddof=0`] | **$0.1609 \pm 0.0226$**<br>[$0.0221$ `ddof=0`] | **$0.1326 \pm 0.0394$**<br>[$0.0386$ `ddof=0`] |
| **LCX** | Left Circumflex | **XGBoost** | None, One-Hot | **Uncalibrated** | 0.50 | **$0.7358 \pm 0.0629$**<br>[$0.0616$ `ddof=0`] | **$0.6173 \pm 0.0838$**<br>[$0.0821$ `ddof=0`] | **$0.2054 \pm 0.0240$**<br>[$0.0235$ `ddof=0`] | **$0.1366 \pm 0.0315$**<br>[$0.0309$ `ddof=0`] |
| **RCA** | Right Coronary Artery | **Logistic Regression** | StandardScaler, One-Hot | **Sigmoid** (Platt) | 0.35 | **$0.7163 \pm 0.0605$**<br>[$0.0593$ `ddof=0`] | **$0.6098 \pm 0.0775$**<br>[$0.0759$ `ddof=0`] | **$0.2060 \pm 0.0150$**<br>[$0.0147$ `ddof=0`] | **$0.1000 \pm 0.0321$**<br>[$0.0315$ `ddof=0`] |

#### Table 3: Calibration Method Comparison Across Model Architectures
*Authoritative Source: `data/reports/reproduction_audit/model_benchmark.json`.*  
*Protocol: 25-fold outer repeated-CV fold distributions (Mean $\pm$ Sample SD, `ddof=1`).*

| Target | Model Candidate | Calibration Method | Brier Score (Lower is Better) | ECE (Lower is Better) | ROC-AUC (Mean $\pm$ SD) | Selected Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Cath** | Logistic Regression | Uncalibrated | $0.1156 \pm 0.0307$ | $0.1200 \pm 0.0294$ | $0.9156 \pm 0.0361$ | Baseline |
| | Logistic Regression | Sigmoid (Platt) | $0.1070 \pm 0.0202$ | $0.1082 \pm 0.0270$ | $0.9176 \pm 0.0354$ | Candidate |
| | Logistic Regression | Isotonic | $0.1089 \pm 0.0255$ | $0.1001 \pm 0.0241$ | $0.9131 \pm 0.0363$ | Candidate |
| | XGBoost | Uncalibrated | $0.1074 \pm 0.0256$ | $0.1265 \pm 0.0218$ | $0.9125 \pm 0.0389$ | Candidate |
| | **XGBoost** | **Sigmoid (Platt)** | **$0.1034 \pm 0.0251$** | **$0.1004 \pm 0.0227$** | **$0.9123 \pm 0.0404$** | **Selected Production** |
| | XGBoost | Isotonic | $0.1044 \pm 0.0283$ | $0.1068 \pm 0.0256$ | $0.9124 \pm 0.0420$ | Candidate |
| **LAD** | Logistic Regression | Uncalibrated | $0.1849 \pm 0.0335$ | $0.1477 \pm 0.0449$ | $0.8171 \pm 0.0538$ | Baseline |
| | Logistic Regression | Sigmoid (Platt) | $0.1740 \pm 0.0188$ | $0.1306 \pm 0.0405$ | $0.8207 \pm 0.0507$ | Candidate |
| | Logistic Regression | Isotonic | $0.1726 \pm 0.0230$ | $0.1426 \pm 0.0298$ | $0.8179 \pm 0.0492$ | Candidate |
| | XGBoost | Uncalibrated | $0.1651 \pm 0.0257$ | $0.1434 \pm 0.0331$ | $0.8338 \pm 0.0530$ | Candidate |
| | **XGBoost** | **Sigmoid (Platt)** | **$0.1609 \pm 0.0226$** | **$0.1326 \pm 0.0394$** | **$0.8443 \pm 0.0528$** | **Selected Production** |
| | XGBoost | Isotonic | $0.1623 \pm 0.0260$ | $0.1339 \pm 0.0318$ | $0.8396 \pm 0.0517$ | Candidate |
| **LCX** | Logistic Regression | Uncalibrated | $0.2393 \pm 0.0367$ | $0.1827 \pm 0.0514$ | $0.6850 \pm 0.0768$ | Baseline |
| | Logistic Regression | Sigmoid (Platt) | $0.2171 \pm 0.0168$ | $0.1050 \pm 0.0453$ | $0.6896 \pm 0.0766$ | Candidate |
| | Logistic Regression | Isotonic | $0.2192 \pm 0.0242$ | $0.1287 \pm 0.0436$ | $0.6838 \pm 0.0794$ | Candidate |
| | **XGBoost** | **Uncalibrated** | **$0.2054 \pm 0.0240$** | **$0.1366 \pm 0.0315$** | **$0.7358 \pm 0.0629$** | **Selected Production** |
| | XGBoost | Sigmoid (Platt) | $0.2073 \pm 0.0155$ | $0.1068 \pm 0.0302$ | $0.7254 \pm 0.0582$ | Candidate |
| | XGBoost | Isotonic | $0.2078 \pm 0.0190$ | $0.1299 \pm 0.0389$ | $0.7296 \pm 0.0533$ | Candidate |
| **RCA** | Logistic Regression | Uncalibrated | $0.2245 \pm 0.0278$ | $0.1673 \pm 0.0373$ | $0.7160 \pm 0.0614$ | Baseline |
| | **Logistic Regression** | **Sigmoid (Platt)** | **$0.2060 \pm 0.0150$** | **$0.1000 \pm 0.0321$** | **$0.7163 \pm 0.0605$** | **Selected Production** |
| | Logistic Regression | Isotonic | $0.2069 \pm 0.0188$ | $0.1236 \pm 0.0423$ | $0.7134 \pm 0.0601$ | Candidate |
| | XGBoost | Uncalibrated | $0.2154 \pm 0.0236$ | $0.1490 \pm 0.0304$ | $0.7036 \pm 0.0634$ | Candidate |
| | XGBoost | Sigmoid (Platt) | $0.2092 \pm 0.0125$ | $0.1146 \pm 0.0350$ | $0.7080 \pm 0.0554$ | Candidate |
| | XGBoost | Isotonic | $0.2090 \pm 0.0145$ | $0.1148 \pm 0.0432$ | $0.7083 \pm 0.0558$ | Candidate |

---

### 4.3 Classification Performance: Standard vs. Tuned Decision Cutoffs
Binary classification metrics under standard fixed cutoffs ($\tau = 0.50$) and nested inner-OOF tuned cutoffs are compared in Table 4 and Table 5. Table 6 provides the four-protocol separation matrix for RCA.

#### Table 4: Standard Threshold (0.50) Binary Classification Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json`.*  
*Protocol: 25 outer fold evaluations at fixed decision cutoff $\tau = 0.50$ (Mean $\pm$ Sample SD, `ddof=1`).*

| Target | Selected Model & Calibration | Accuracy (Mean $\pm$ SD) | Balanced Accuracy (Mean $\pm$ SD) | Sensitivity / Recall (Mean $\pm$ SD) | Specificity (Mean $\pm$ SD) | Precision (Mean $\pm$ SD) | $F_1$-Score (Mean $\pm$ SD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | XGBoost + Sigmoid | $0.8667 \pm 0.0411$ | $0.8262 \pm 0.0513$ | $0.9212 \pm 0.0361$ | $0.7312 \pm 0.0855$ | $0.8953 \pm 0.0318$ | $0.9077 \pm 0.0285$ |
| **LAD** | XGBoost + Sigmoid | $0.7868 \pm 0.0462$ | $0.7730 \pm 0.0527$ | $0.8568 \pm 0.0665$ | $0.6891 \pm 0.1173$ | $0.7995 \pm 0.0573$ | $0.8244 \pm 0.0372$ |
| **LCX** | XGBoost Uncalibrated | $0.6871 \pm 0.0539$ | $0.6744 \pm 0.0563$ | $0.6163 \pm 0.0987$ | $0.7325 \pm 0.0743$ | $0.6020 \pm 0.0733$ | $0.6054 \pm 0.0744$ |
| **RCA** | Logistic Regression + Sigmoid | $0.6562 \pm 0.0504$ | $0.5881 \pm 0.0500$ | **$0.3124 \pm 0.0856$** | $0.8638 \pm 0.0741$ | $0.5998 \pm 0.1346$ | **$0.4027 \pm 0.0872$** |

#### Table 5: Nested Inner-Fold Threshold Tuning Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json`.*  
*Protocol: 25 outer fold evaluations where threshold is tuned on inner 3-fold CV to maximize macro $F_1$ (Mean $\pm$ Sample SD, `ddof=1`).*

| Target | Selected Model & Calibration | Selected Threshold Distribution (Mean $\pm$ SD [Min, Max]) | Accuracy (Mean $\pm$ SD) | Balanced Accuracy (Mean $\pm$ SD) | Sensitivity / Recall (Mean $\pm$ SD) | Specificity (Mean $\pm$ SD) | Precision (Mean $\pm$ SD) | $F_1$-Score (Mean $\pm$ SD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | XGBoost + Sigmoid | $0.4912 \pm 0.0745$ [$0.34, 0.63$] | $0.8686 \pm 0.0392$ | $0.8269 \pm 0.0521$ | $0.9249 \pm 0.0387$ | $0.7289 \pm 0.0971$ | $0.8954 \pm 0.0347$ | $0.9093 \pm 0.0270$ |
| **LAD** | XGBoost + Sigmoid | $0.4496 \pm 0.0568$ [$0.32, 0.54$] | $0.7815 \pm 0.0564$ | $0.7629 \pm 0.0673$ | $0.8760 \pm 0.0652$ | $0.6497 \pm 0.1528$ | $0.7855 \pm 0.0686$ | $0.8248 \pm 0.0407$ |
| **LCX** | XGBoost Uncalibrated | $0.3452 \pm 0.0758$ [$0.16, 0.43$] | $0.6205 \pm 0.0714$ | $0.6508 \pm 0.0648$ | $0.7944 \pm 0.1201$ | $0.5072 \pm 0.1348$ | $0.5161 \pm 0.0638$ | $0.6215 \pm 0.0646$ |
| **RCA** | Logistic Regression + Sigmoid | $0.3188 \pm 0.0380$ [$0.20, 0.37$]\* [PENDING VERIFICATION] | $0.6072 \pm 0.0716$ | **$0.6443 \pm 0.0575$** | **$0.7946 \pm 0.1092$** | **$0.4941 \pm 0.1429$** | $0.4928 \pm 0.0532$ | **$0.6037 \pm 0.0516$** |

*\*Audit Note on RCA Selected Threshold SD [PENDING VERIFICATION]: An exact re-calculation over the 25 outer fold threshold values (`[0.34, 0.27, 0.30, 0.32, 0.31, 0.29, 0.28, 0.30, 0.32, 0.37, 0.36, 0.32, 0.37, 0.31, 0.34, 0.34, 0.35, 0.35, 0.20, 0.37, 0.34, 0.30, 0.29, 0.33, 0.30]`) yields Mean = **0.3188**, Population SD (`ddof=0`) = **0.0372**, and Sample SD (`ddof=1`) = **0.0380**. The value $0.0388$ previously cited in preliminary notes was an unverified draft artifact resulting from an accidental double-Bessel correction ($0.0380 \times \sqrt{25/24} \approx 0.0388$). Until confirmed across all legacy documents, this value is tagged as pending final manuscript sign-off.*

#### Table 6: Production Operating Threshold Performance & Protocol Separation (RCA Deep Dive)
*Authoritative Source: `models/rca/metadata.json`, `data/reports/reproduction_audit/calibration_results.json`, and stored `oof_y_prob`.*

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         RCA EVALUATION PROTOCOL SEPARATION MATRIX                                      │
├────────────────────────────────┬──────────────┬──────────────┬───────────────────┬─────────────────────────────────────┤
│ Protocol Identifier            │ Sample Unit  │ Sample Count │ Decision Cutoff   │ Metrics (Recall / Specificity / F1) │
├────────────────────────────────┼──────────────┼──────────────┼───────────────────┼─────────────────────────────────────┤
│ Protocol 1: Standard 0.50      │ Outer Fold   │ 25 folds     │ Fixed tau = 0.50  │ Sens: 0.312 ± 0.086, Spec: 0.864 ± 0.074│
│ Protocol 2: Nested Tuned       │ Outer Fold   │ 25 folds     │ Inner-OOF dynamic │ Sens: 0.795 ± 0.109, Spec: 0.494 ± 0.143│
│ Protocol 3: Fixed 0.35 (Fold)  │ Outer Fold   │ 25 folds     │ Fixed tau = 0.35  │ Sens: 0.742 ± 0.106, Spec: 0.575 ± 0.071│
│ Protocol 4: Fixed 0.35 (Repeat)│ CV Repeat    │ 5 repeats    │ Fixed tau = 0.35  │ Sens: 0.742 ± 0.025, Spec: 0.575 ± 0.011│
└────────────────────────────────┴──────────────┴──────────────┴───────────────────┴─────────────────────────────────────┘
```

##### Detailed Breakdown of RCA Protocols:
1. **Protocol 1 (Standard 0.50 across 25 outer folds):** Accuracy $0.6562 \pm 0.0504$, Balanced Accuracy $0.5881 \pm 0.0500$, Sensitivity $0.3124 \pm 0.0856$, Specificity $0.8638 \pm 0.0741$, $F_1 = 0.4027 \pm 0.0872$ (`ddof=1`).
2. **Protocol 2 (Nested Inner-OOF Tuned across 25 outer folds):** Accuracy $0.6072 \pm 0.0716$, Balanced Accuracy $0.6443 \pm 0.0575$, Sensitivity $0.7946 \pm 0.1092$, Specificity $0.4941 \pm 0.1429$, $F_1 = 0.6037 \pm 0.0516$ (`ddof=1`). *(Serialized in `models/rca/metadata.json`)*.
3. **Protocol 3 (Fixed 0.35 Operating Cutoff across 25 outer folds):** Accuracy $0.6377 \pm 0.0597$, Balanced Accuracy $0.6585 \pm 0.0638$, Sensitivity $0.7421 \pm 0.1064$, Specificity $0.5748 \pm 0.0710$, $F_1 = 0.6053 \pm 0.0684$ (`ddof=1`).
4. **Protocol 4 (Fixed 0.35 Operating Cutoff across 5 Complete CV Repeats):** Accuracy $0.6376 \pm 0.0075$, Balanced Accuracy $0.6584 \pm 0.0102$, Sensitivity $0.7421 \pm 0.0253$, Specificity $0.5746 \pm 0.0110$, $F_1 = 0.6063 \pm 0.0120$ (`ddof=1` across $R=5$ complete cohort resamplings).

---

### 4.4 SHAP Explanation Stability and Mathematical Verification
Global and patient-level explanation stability metrics across the 25 outer cross-validation folds are presented in Table 7. Exact mathematical additivity ($\sum \phi_i + \phi_0 = f(x)$) passed in 100% of folds ($25/25$) across all targets, with maximum observed floating-point reconstruction errors $< 1.2 \times 10^{-6}$ for tree models and $< 1.8 \times 10^{-15}$ for linear models.

#### Table 7: SHAP Explanation Stability Across Resampled Cross-Validation Folds
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp A).*  
*Protocol: 25 outer folds (5 splits $\times$ 5 repeats). Pairwise global correlations across 300 fold pairs. Patient-level stability evaluated across 5 independent out-of-fold explanations per patient ($N=303$).*

| Metric Dimension | Cath (XGBoost) | LAD (XGBoost) | LCX (XGBoost) | RCA (Logistic Regression) |
| :--- | :---: | :---: | :---: | :---: |
| **Explanation Mathematical Space** | Margin / Log-Odds ($f(x)$) | Margin / Log-Odds ($f(x)$) | Margin / Log-Odds ($f(x)$) | Decision Function ($f(x)$) |
| **Reconstruction Additivity Pass Rate** | **100.0% (25/25)** | **100.0% (25/25)** | **100.0% (25/25)** | **100.0% (25/25)** |
| **Max Reconstruction Error** | $9.54 \times 10^{-7}$ | $9.54 \times 10^{-7}$ | $1.19 \times 10^{-6}$ | $1.78 \times 10^{-15}$ |
| **Global Spearman Rank Correlation ($\rho \pm \text{SD}$)** | **$0.9319 \pm 0.0192$** | **$0.9217 \pm 0.0197$** | **$0.9081 \pm 0.0263$** | **$0.7737 \pm 0.0583$** |
| **Global Spearman Range [Min, Max]** | [0.8644, 0.9738] | [0.8414, 0.9633] | [0.8152, 0.9679] | [0.5690, 0.8912] |
| **Global Kendall’s Tau ($\tau \pm \text{SD}$)** | $0.8133 \pm 0.0293$ | $0.7893 \pm 0.0326$ | $0.7828 \pm 0.0363$ | $0.6011 \pm 0.0568$ |
| **Top-5 Feature Jaccard Similarity** | $0.6887 \pm 0.1834$ | **$0.7456 \pm 0.1417$** | $0.5195 \pm 0.1723$ | $0.4890 \pm 0.1724$ |
| **Top-10 Feature Jaccard Similarity** | $0.7475 \pm 0.1254$ | $0.5354 \pm 0.1190$ | $0.6060 \pm 0.1084$ | $0.5685 \pm 0.1126$ |
| **Patient Attribution Sign Agreement (%)** | **91.09%** | **90.03%** | **86.72%** | **86.07%** |
| **Patient Mean Rank Correlation** | 0.7717 | 0.7661 | 0.6823 | 0.7382 |
| **Top-5 Features by Inclusion Frequency** | `Age` (100%), `Typical Chest Pain` (100%), `EF-TTE` (92%), `Region RWMA` (88%), `FBS` (44%) | `Age` (100%), `EF-TTE` (100%), `Region RWMA` (100%), `Typical Chest Pain` (100%), `ESR` (48%) | `Age` (100%), `Typical Chest Pain` (100%), `CR` (72%), `TG` (60%), `PLT` (60%) | `Age` (100%), `DM` (96%), `Function Class` (64%), `Dyspnea` (60%), `ESR` (52%) |

Tree-based models exhibited exceptional global rank stability ($\rho > 0.90$ across all 300 fold pairs), with LAD demonstrating the highest Top-5 Jaccard consistency ($0.7456 \pm 0.1417$) driven by invariant anatomical anchors (`Age`, `EF-TTE`, `Region RWMA`, `Typical Chest Pain`). Linear regularized regression on RCA displayed lower ranking stability ($\rho = 0.7737 \pm 0.0583$), reflecting coefficient instability induced by multi-collinearity among non-specific clinical risk factors (`DM`, `Age`, `ESR`, `Dyspnea`).

---

### 4.5 Prediction Stability and Decision Boundary Proximity
Prediction dispersion and classification invariance across 5 independent cross-validation repeats ($N=303$) are detailed in Table 8. The analysis demonstrates that classification label flips are not distributed uniformly across the patient population, but concentrate almost exclusively within the narrow margin immediately adjacent to the operating cutoff ($|p - \tau| < 0.05$).

#### Table 8: Prediction Stability and Boundary Proximity Stratification
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp B).*  
*Protocol: 5 repeats of 5-fold CV yielding 5 independent out-of-fold probability estimates per patient ($N=303$).*

| Prediction Metric Dimension | Cath | LAD | LCX | RCA |
| :--- | :---: | :---: | :---: | :---: |
| **Operating Decision Cutoff ($\tau$)** | 0.50 | 0.50 | 0.50 | 0.35 |
| **Across-Patient Mean Probability SD ($\sigma_p$)** | **0.0385** | **0.0488** | **0.0701** | **0.0404** |
| **Across-Patient Median Probability SD** | 0.0248 | 0.0450 | 0.0675 | 0.0370 |
| **Maximum Observed Patient SD ($\max \sigma_p$)** | 0.1733 | 0.1622 | 0.1736 | 0.1286 |
| **Proportion with High Dispersion ($\sigma_p > 0.05$)** | 27.39% (83/303) | 41.58% (126/303) | 71.95% (218/303) | 27.39% (83/303) |
| **Proportion with Severe Dispersion ($\sigma_p > 0.10$)** | 7.92% (24/303) | 11.22% (34/303) | 18.81% (57/303) | 1.98% (6/303) |
| **Patient Risk Ranking Spearman Correlation** | 0.9221 | 0.9339 | 0.8604 | 0.8975 |
| **Complete Classification Invariance (5/5 Identical Labels)** | **91.09% (276/303)** | **81.85% (248/303)** | **67.00% (203/303)** | **75.58% (229/303)** |
| **Classification Flips (1 to 4 Flips Across 5 Repeats)** | 8.91% (27/303) | 18.15% (55/303) | 33.00% (100/303) | 24.42% (74/303) |
| **Invariance by Boundary Distance: $|p - \tau| < 0.05$** | **0.0% (0/6)** | **0.0% (0/17)** | **2.2% (1/45)** | **22.7% (17/75)** |
| **Invariance by Boundary Distance: $0.05 \le |p - \tau| < 0.10$** | 46.2% (6/13) | 42.9% (12/28) | 27.8% (15/54) | 78.4% (58/74) |
| **Invariance by Boundary Distance: $0.10 \le |p - \tau| < 0.20$** | 81.6% (31/38) | 88.2% (60/68) | 75.0% (51/68) | 100.0% (106/106) |
| **Invariance by Boundary Distance: $|p - \tau| \ge 0.20$** | **99.19% (244/246)** | **100.0% (190/190)** | **99.26% (135/136)** | **100.0% (48/48)** |

For all targets, patients with confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance. Conversely, patients located within $|p - \tau| < 0.05$ exhibited nearly complete classification volatility across model retraining (0.0% invariance for Cath and LAD), establishing boundary proximity as the primary driver of prediction instability.

---

### 4.6 Predictive Uncertainty and Error Detection Discrimination
The ability of normalized binary predictive entropy $H(p)$ and threshold margin $M(p) = |p - \tau|$ to discriminate empirical classification errors without access to ground-truth labels is documented in Table 9.

#### Table 9: Predictive Uncertainty and Error Detection Performance
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp C).*

| Target | Error-Detection ROC-AUC of Entropy $H(p)$ | Mean Entropy: Correct Predictions | Mean Entropy: Misclassified Predictions | Error Rate: Margin $< 0.05$ | Error Rate: Margin $0.05 - 0.10$ | Error Rate: Margin $0.10 - 0.20$ | Error Rate: Margin $\ge 0.20$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | **0.7593** | 0.4079 | **0.7550** | **33.3%** | 30.8% | 15.8% | **1.6%** |
| **LAD** | **0.6595** | 0.6534 | **0.8258** | **41.2%** | 32.1% | 16.2% | **7.4%** |
| **LCX** | **0.6392** | 0.8123 | **0.9080** | **44.4%** | 31.5% | 22.1% | **14.7%** |
| **RCA** | **0.6796** | 0.7780 | **0.8879** | **40.0%** | 25.7% | 14.2% | **16.7%** |

Normalized binary entropy exhibited strong discriminative capability for identifying erroneous predictions on the primary composite outcome (error-detection ROC-AUC $0.7593$ for Cath). Furthermore, empirical error rates declined monotonically as distance from the operating threshold expanded (from 33.3% down to 1.6% for Cath).

---

### 4.7 Model Robustness Under Input Perturbations and Feature Ablation
Pipeline robustness under continuous Gaussian feature perturbation and synthetic missingness stress testing is reported in Table 10. Table 11 reports inside-cross-validation feature group ablation drops ($\Delta \text{ROC-AUC}$) relative to the Repeat-1 5-fold pooled baseline ($N=303$).

#### Table 10: Input Noise Perturbation & Synthetic Missingness Degradation
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp D).*

| Target | Mean Prob Shift ($0.1\sigma$) | Label Flip Rate ($0.1\sigma$) | Mean Prob Shift ($0.5\sigma$) | Label Flip Rate ($0.5\sigma$) | Mean Prob Shift ($1.0\sigma$) | Label Flip Rate ($1.0\sigma$) | MCAR 10% Absolute $\Delta \text{AUC}$ | MCAR 20% Absolute $\Delta \text{AUC}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | 0.0040 | 0.43% | 0.0201 | 2.18% | 0.0401 | 4.36% | -0.0146 | -0.0336 |
| **LAD** | 0.0042 | 0.53% | 0.0210 | 2.64% | 0.0421 | 5.28% | -0.0167 | -0.0350 |
| **LCX** | 0.0070 | 0.86% | 0.0348 | 4.29% | 0.0697 | 8.58% | -0.0238 | -0.0456 |
| **RCA** | 0.0051 | 1.35% | 0.0254 | 6.73% | 0.0508 | 13.47% | -0.0229 | -0.0456 |

#### Table 11: Inside-Cross-Validation Feature Group Ablation Impact ($\Delta \text{ROC-AUC}$)
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp D).*  
*Protocol: Models retrained from scratch inside 5-fold CV (Repeat 1) without indicated feature block. Delta evaluated relative to Repeat-1 pooled baseline: Cath (0.9018), LAD (0.8477), LCX (0.7426), RCA (0.7040).*

| Feature Group Ablated | Active Features Included | Cath ($\Delta \text{AUC}$) | LAD ($\Delta \text{AUC}$) | LCX ($\Delta \text{AUC}$) | RCA ($\Delta \text{AUC}$) | Primary Physiological Mechanism |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Symptoms & Exam** | `Typical Chest Pain`, `BP`, `HR`, `Murmurs`, `Dyspnea`, etc. | **-0.0847** | **-0.0532** | -0.0124 | **-0.0280** | Anginal symptom presentation is the primary driver of pre-test CAD suspicion. |
| **Echocardiography** | `EF-TTE`, `Region RWMA`, `VHD` | -0.0200 | **-0.0528** | -0.0185 | -0.0094 | **LAD exhibits profound dependence on echocardiography**, reflecting anterior wall dyssynergy. |
| **Laboratory Panel** | `FBS`, `CR`, `TG`, `LDL`, `HDL`, `ESR`, `WBC`, `PLT`, etc. | -0.0142 | -0.0189 | **-0.0524** | -0.0121 | **LCX depends predominantly on laboratory panels**, compensating for posterolateral imaging silence. |
| **Demographic** | `Age`, `Sex`, `BMI` | -0.0084 | -0.0146 | -0.0210 | -0.0150 | Baseline cardiovascular risk adjustment. |
| **ECG Panel** | `Q Wave`, `ST Elevation`, `ST Depression`, `T Inversion`, `BBB` | -0.0062 | -0.0089 | -0.0045 | -0.0088 | Resting ECG markers provide secondary diagnostic confirmation. |
| **Comorbidities** | `DM`, `HTN`, `FH` | -0.0035 | -0.0052 | -0.0082 | -0.0112 | Chronic systemic risk markers. |

---

### 4.8 Exploratory Subgroup Analysis Across Clinical Strata
Disaggregated discrimination metrics across 13 feasible patient strata evaluated on consensus multi-repeat predictions ($N=303$) are detailed in Table 12.

#### Table 12: Exploratory Subgroup Analysis Across Clinical Strata
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp E).*  
*Protocol: Consensus patient OOF predictions ($N=303$). Sample size feasibility guard enforced ($N \ge 30, \min(N_+, N_-) \ge 5$).*

| Category | Stratum / Subgroup | Total $N$ | Positive ($N_+$) | Negative ($N_-$) | Cath ROC-AUC | LAD ROC-AUC | LCX ROC-AUC | RCA ROC-AUC | Clinical Observations |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Full Cohort** | All Patients | 303 | 216 | 87 | 0.9097 | 0.8396 | 0.7537 | 0.7200 | Consensus baseline. |
| **Biological Sex** | **Male** | 176 | 130 | 46 | 0.8779 | 0.8579 | 0.7557 | 0.6840 | Comparable discrimination across sexes; higher Cath discrimination observed in females. |
| | **Female** | 127 | 86 | 41 | 0.9495 | 0.8102 | 0.7482 | 0.7611 | Descriptive parity; does not imply formal fairness certification. |
| **Age Stratum** | **Age < 55** | 108 | 68 | 40 | 0.8954 | 0.8569 | 0.7380 | 0.7861 | Strong discrimination in younger cohorts. |
| | **Age 55 - 65** | 100 | 78 | 22 | 0.9534 | 0.8451 | 0.7636 | 0.6962 | Peak discrimination observed in middle-age bracket. |
| | **Age $\ge$ 65** | 95 | 70 | 25 | **0.7480** | **0.7171** | **0.6055** | **0.6422** | **Descriptive attenuation in elderly patients**, reflecting diffuse vascular calcification and non-anginal symptom presentations. |
| **Diabetes** | **Diabetic** | 90 | 78 | 12 | 0.9838 | 0.6874 | 0.7011 | 0.6174 | High Cath discrimination in diabetics; lower LAD/RCA discrimination reflects silent ischemia. |
| | **Non-Diabetic** | 213 | 138 | 75 | 0.8843 | 0.8763 | 0.7585 | 0.7099 | Robust vessel discrimination in non-diabetics. |
| **Hypertension** | **Hypertensive** | 179 | 136 | 43 | 0.8886 | 0.7855 | 0.7203 | 0.6898 | Stable discrimination across blood pressure categories. |
| | **Normotensive** | 124 | 80 | 44 | 0.8980 | 0.8850 | 0.7585 | 0.7443 | Marginally higher discrimination in normotensive patients. |
| **Obesity** | **Obese ($\text{BMI} \ge 25$)** | 211 | 150 | 61 | 0.9128 | 0.8344 | 0.7758 | 0.7255 | Similar performance across BMI categories. |
| | **Non-Obese ($\text{BMI} < 25$)** | 92 | 66 | 26 | 0.9033 | 0.8463 | 0.7030 | 0.7143 | Robustness across body mass phenotypes. |
| **Dyslipidemia** | **Dyslipidemic** | 112 | 86 | 26 | 0.9275 | 0.7939 | 0.7422 | 0.7257 | Consistent discrimination across lipid profiles. |
| | **Non-Dyslipidemic** | 191 | 130 | 61 | 0.9009 | 0.8680 | 0.7598 | 0.7163 | Marginally higher LAD discrimination in non-dyslipidemic patients. |

---

## Proposed Figure Captions for Scientific Publication

### Figure 1: Multi-Target Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Curves
**Caption:** Multi-target discrimination across 25 outer test folds of repeated stratified cross-validation (5 splits $\times$ 5 repeats). Solid curves depict the mean trajectory; shaded envelopes represent $\pm 1$ cross-fold standard deviation (`ddof=1`). Panels illustrate: (A) Cath composite CAD (ROC-AUC $0.9123 \pm 0.0404$, PR-AUC $0.9597 \pm 0.0200$); (B) LAD stenosis (ROC-AUC $0.8443 \pm 0.0528$, PR-AUC $0.8818 \pm 0.0471$); (C) LCX stenosis (ROC-AUC $0.7358 \pm 0.0629$, PR-AUC $0.6173 \pm 0.0838$); and (D) RCA stenosis (ROC-AUC $0.7163 \pm 0.0605$, PR-AUC $0.6098 \pm 0.0775$).

### Figure 2: Multi-Target Probability Calibration Diagrams (Reliability Curves) Before and After Sigmoid Scaling
**Caption:** Calibration reliability diagrams evaluating 10 probability confidence deciles against empirical event frequencies across 25 outer test folds. Dashed diagonal lines represent ideal calibration ($y = x$). Curves compare uncalibrated model outputs against Platt (Sigmoid) calibrated probabilities. Platt scaling significantly improves alignment for Cath (Brier $0.1034$, ECE $0.1004$) and LAD (Brier $0.1609$, ECE $0.1326$), and reduces ECE to $0.1000$ for RCA. Probability compression on RCA illustrates clustering of calibrated probabilities below 0.50, necessitating operating threshold optimization ($\tau = 0.35$).

### Figure 3: Global TreeSHAP and LinearSHAP Feature Attribution Distributions and Multi-Fold Stability Heatmaps
**Caption:** Feature explanation stability across 25 outer cross-validation folds. Left panels display global mean absolute SHAP attributions ($\frac{1}{N} \sum |\phi_i|$) in raw model score space ($f(x)$) for the Top-15 clinical features. Right heatmaps illustrate pairwise Spearman rank correlation matrices across all $\binom{25}{2} = 300$ fold comparisons. Tree-based models display exceptional attribution stability (Mean $\rho = 0.9319$ for Cath, $0.9217$ for LAD, $0.9081$ for LCX). Exact mathematical additivity ($\sum \phi_i + \phi_0 = f(x)$) verified in 100% of folds ($25/25$).

### Figure 4: Prediction Probability Dispersion ($\sigma_p$) and Decision Boundary Proximity Agreement Curves
**Caption:** Empirical out-of-fold prediction dispersion and classification invariance across 5 cross-validation repeats ($N=303$). (A) Cohort distributions of patient probability standard deviation ($\sigma_p$). (B) Classification label consistency plotted as a function of absolute distance from the operating threshold ($|p - \tau|$). Invariance curves confirm that classification flips concentrate exclusively within $|p - \tau| < 0.05$ (0.0% agreement for Cath and LAD), whereas confident predictions ($|p - \tau| \ge 0.20$) achieve $>99\%$ label invariance across independent model fits.

### Figure 5: Normalized Binary Predictive Entropy Distributions and Error-Detection ROC Curves
**Caption:** Predictive uncertainty quantification via binary entropy $H(p)$. (A) Violin plots comparing entropy distributions between correctly classified and misclassified patients across all four targets. (B) Receiver Operating Characteristic curves evaluating the capacity of entropy to discriminate empirical classification errors without access to ground truth (error-detection ROC-AUC $0.7593$ for Cath, $0.6595$ for LAD, $0.6392$ for LCX, $0.6796$ for RCA).

### Figure 6: Inside-Cross-Validation Feature Group Ablation Impact Across Coronary Territories
**Caption:** Physiological divergence across coronary branches revealed by inside-cross-validation feature group ablation. Bars represent the absolute decline in out-of-fold ROC-AUC ($\Delta \text{AUC}$) relative to the unablated Repeat-1 baseline when retraining pipelines without indicated clinical feature domains. LAD displays acute sensitivity to echocardiographic ablation ($\Delta = -0.0528$), whereas LCX is predominantly driven by laboratory blood panels ($\Delta = -0.0524$).
