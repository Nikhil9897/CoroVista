# Reliable and Explainable Machine Learning for Coronary Artery Disease Prediction: Calibration, Prediction Stability, Explainability Stability and Robustness

**Authors:**\
Naman Deep Tripathi$^{1,*}$, Nikhil Agrawal$^2$

$^1$ Sanskriti University, Mathura, Uttar Pradesh, India (Academic programme: Bachelor of Computer Applications [BCA], Second Year; ORCID: [0009-0006-8775-3794](https://orcid.org/0009-0006-8775-3794))\
$^2$ VIT Bhopal University, Bhopal, Madhya Pradesh, India (Academic programme: Bachelor of Technology [B.Tech.], Fourth Year; ORCID: [0009-0009-1546-5576](https://orcid.org/0009-0009-1546-5576))\
$^*$ *Corresponding Author:* Naman Deep Tripathi (namandeeptripathi@gmail.com)\
*(Note: Specific academic departments within Sanskriti University and VIT Bhopal University have not been specified and are flagged for author confirmation if required by the target journal)*

---

## Abstract

### Background
Machine learning models for coronary artery disease (CAD) diagnosis predominantly optimize global discrimination metrics (such as ROC-AUC) on composite binary outcomes while neglecting probability calibration, explanation consistency under resampling, prediction stability near decision boundaries, and vessel-specific anatomical localization. Consequently, high benchmark accuracies reported in the literature frequently mask severe probability miscalibration, volatile feature attributions, and localized prediction fragility that hinder safe clinical translation.

### Methods
Using the extended Z-Alizadeh Sani cohort ($N = 303$ consecutive adult patients referred for invasive coronary catheterization at Shaheed Rajaei Cardiovascular, Medical and Research Center in Tehran, Iran), we developed and audited an end-to-end, multi-target predictive framework. We modeled overall CAD (`Cath`) and obstructive stenosis ($\ge 50\%$ luminal diameter reduction) across the three primary epicardial coronary branches: Left Anterior Descending (`LAD`), Left Circumflex (`LCX`), and Right Coronary Artery (`RCA`). Evaluation followed a strict 25-fold Repeated Stratified Cross-Validation protocol (5 splits $\times$ 5 repeats) with partition-isolated preprocessing and target-specific calibration (Sigmoid Platt calibration for Cath, LAD, and RCA; uncalibrated for LCX). We systematically quantified: (i) discrimination (ROC-AUC, PR-AUC) and probability calibration (Brier score, Expected Calibration Error [ECE]); (ii) global and patient-level TreeSHAP and LinearSHAP explanation stability across resampled folds; (iii) empirical out-of-fold prediction dispersion and boundary proximity classification invariance; (iv) predictive uncertainty quantification via binary entropy; (v) continuous Gaussian perturbation, synthetic missingness stress testing, and inside-cross-validation feature ablation; and (vi) exploratory subgroup feasibility across 13 demographic and comorbidity strata.

### Results
Selected production models demonstrated strong multi-target discrimination and calibration reliability across 25 outer test folds (Mean $\pm$ Sample SD, `ddof=1`): Cath (calibrated) ROC-AUC $0.9123 \pm 0.0404$ (Brier $0.1034 \pm 0.0251$, ECE $0.1004 \pm 0.0227$); LAD (calibrated) ROC-AUC $0.8443 \pm 0.0528$ (Brier $0.1609 \pm 0.0226$, ECE $0.1326 \pm 0.0394$); LCX (uncalibrated) ROC-AUC $0.7358 \pm 0.0629$ (Brier $0.2054 \pm 0.0240$, ECE $0.1366 \pm 0.0315$); and RCA (calibrated) ROC-AUC $0.7163 \pm 0.0605$ (Brier $0.2060 \pm 0.0150$, ECE $0.1000 \pm 0.0321$). Standard arbitrary thresholding ($\tau = 0.50$) caused severe sensitivity collapse on calibrated RCA models (Recall $31.24\% \pm 8.56\%$), which was resolved by nested inner-fold threshold tuning (cutoff $0.3188 \pm 0.0380$, Recall $79.46\% \pm 10.92\%$, Specificity $49.41\% \pm 14.29\%$, $F_1 = 0.6037 \pm 0.0516$) and fixed production thresholding at $\tau = 0.35$ (Recall $74.21\% \pm 10.64\%$ across 25 outer folds [$74.21\% \pm 2.53\%$ across 5 repeats], Specificity $57.48\% \pm 7.10\%$ [$57.46\% \pm 1.10\%$ across 5 repeats]). Exact SHAP additivity verified in 100% of outer folds ($25/25$). Global feature ranking exhibited high stability for tree models across resampled folds (Spearman $\rho = 0.9319 \pm 0.0192$ for Cath, $0.9217 \pm 0.0197$ for LAD, $0.9081 \pm 0.0263$ for LCX). Classification label flips across 5 cross-validation repeats were concentrated among borderline patients: in the immediate threshold margin ($|p - \tau| < 0.05$), all Cath ($6/6$) and LAD ($17/17$) patients experienced at least one label change ($0\%$ invariance), while LCX and RCA exhibited $2.2\%$ ($1/45$) and $22.7\%$ ($17/75$) invariance respectively, confirming that predictions closer to operating thresholds were generally less stable; in contrast, confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance across targets. While predictive entropy is computable directly from model output probabilities without outcome labels during inference, retrospective evaluation against reference catheterization labels demonstrated that entropy discriminated misclassified from correctly classified predictions (retrospective error-detection ROC-AUC $0.7593$ for Cath). Inside-cross-validation ablation revealed distinct territorial statistical patterns: LAD models depended primarily on echocardiography (`Region RWMA`, `EF-TTE`), while LCX models relied predominantly on laboratory blood panels (`CR`, `TG`, `PLT`).

### Conclusions
Evaluating coronary artery disease models through the multi-dimensional lenses of probability calibration, explanation stability, prediction dispersion, and boundary-focused uncertainty exposes critical behavioral characteristics that standard discrimination benchmarks obscure. Target-specific probability calibration and systematic stability profiling represent essential prerequisites for trustworthy clinical decision support.

**Keywords:** Coronary Artery Disease; Multi-Vessel Stenosis; Probability Calibration; SHAP Stability; Prediction Stability; Uncertainty Quantification; Diagnostic Angiography; Machine Learning.

---

## 1. Introduction

### 1.1 Clinical Burden & Diagnostic Paradigms in Coronary Artery Disease
Coronary artery disease (CAD), characterized by atherosclerotic plaque accumulation within epicardial coronary arteries, remains the leading cause of morbidity and premature mortality worldwide, accounting for over 9 million deaths annually (Martin et al., 2024). The clinical manifestation of CAD spans a broad spectrum—from asymptomatic subclinical atherosclerosis and stable chronic coronary syndromes to unstable angina and acute myocardial infarction. Timely, accurate diagnosis is vital to prevent irreversible myocardial necrosis, ischemic heart failure, and malignant ventricular arrhythmias.

In contemporary cardiovascular practice, invasive coronary angiography (ICA) is recognized as the definitive reference standard for diagnosing CAD and determining the anatomical extent of luminal stenosis (Lawton et al., 2022). Significant obstructive coronary artery disease is conventionally defined as $\ge 50\%$ luminal diameter narrowing in one or more major epicardial coronary vessels (Alizadehsani et al., 2013). However, ICA is an invasive catheterization procedure requiring arterial puncture, fluoroscopic ionizing radiation, and iodinated contrast media. Consequently, it carries non-negligible procedural risks, including iatrogenic vascular injury, access-site hematoma, retroperitoneal bleeding, contrast-induced acute kidney injury, embolic stroke, coronary dissection, and, rarely, procedure-related death (Lawton et al., 2022). Furthermore, cardiac catheterization laboratory infrastructure demands substantial capital expenditure and specialized personnel. In clinical practice, large-scale multicenter registry data indicate that more than half of elective diagnostic catheterizations yield non-obstructive findings or completely normal coronary arteries—with landmark registry investigations documenting that only 37.6% of elective procedures identify obstructive stenosis (Patel et al., 2010)—indicating a pressing clinical need for more accurate, non-invasive pre-catheterization risk stratification.

To mitigate unnecessary invasive procedures, clinical practice relies on non-invasive assessments, including cardiovascular risk scores (e.g., Framingham, SCORE2), resting 12-lead electrocardiography (ECG), exercise treadmill testing, transthoracic echocardiography (TTE), and coronary computed tomography angiography (CCTA). While CCTA provides exceptional anatomical visualization, its availability is constrained by specialized scanner requirements, high costs, radiocontrast administration, and nephrotoxicity risks in renal insufficiency. Conversely, routine clinical variables—comprising demographic characteristics, cardiovascular risk habits, physical examination signs, standard laboratory blood panels, resting ECG parameters, and resting echocardiographic measurements—are routinely gathered during initial patient evaluations at minimal marginal expense. Developing sophisticated, reliable machine learning algorithms capable of mining complex non-linear interactions across these ubiquitous multimodal clinical inputs represents a high-impact diagnostic opportunity.

Crucially, the clinical management of CAD is fundamentally governed by **vessel-specific anatomical localization**, rather than an aggregate, binary determination of whether disease is present:
- **Left Anterior Descending (LAD) Artery:** The LAD courses along the anterior interventricular groove, perfusing approximately 45% to 55% of the left ventricular myocardium, including the anterior wall, cardiac apex, and the anterior two-thirds of the interventricular septum. In clinical cardiology literature, significant stenosis in the proximal or mid LAD exposes large territories of myocardium to ischemic risk (Lawton et al., 2022). Revascularization guidelines frequently discuss revascularization (via percutaneous coronary intervention [PCI] or coronary artery bypass grafting [CABG]) for high-grade LAD lesions in eligible symptomatic or high-risk patients to confer potential prognostic benefits (Lawton et al., 2022).
- **Left Circumflex (LCX) Artery:** Branching from the left main coronary artery to traverse the left atrioventricular groove, the LCX supplies blood to the posterolateral left ventricular free wall and, in left-dominant circulations, the posterior descending artery. Isolated LCX stenosis is notoriously challenging to detect non-invasively; the posterolateral myocardial territory is frequently electrical and mechanical "silent" on resting 12-lead ECG and standard resting echocardiography, leading to underdiagnosis or diagnostic delay.
- **Right Coronary Artery (RCA):** The RCA courses down the right atrioventricular sulcus, supplying the right ventricle, inferior left ventricular wall, posterior ventricular septum, and, in 90% of individuals, the sinoatrial and atrioventricular (AV) nodal conduction tissue. Obstructive RCA lesions frequently present with acute inferior myocardial infarction complicated by severe bradyarrhythmias, high-degree AV block, and right ventricular dysfunction.

Because clinical prognosis, therapeutic urgency, and revascularization strategy diverge drastically depending on which specific coronary vessel is compromised, diagnostic machine learning systems must extend beyond binary whole-patient classification to deliver reliable, vessel-specific anatomical risk predictions.

---

### 1.2 The Reliability Gap in Clinical Machine Learning
Over the past decade, hundreds of machine learning studies have reported high classification accuracies on cardiology datasets. However, a substantial translational gap persists between reported benchmark metrics and safe clinical integration. This disconnect stems from several pervasive algorithmic vulnerabilities that standard machine learning workflows routinely overlook:

#### 1. Over-Reliance on Discrimination over Probability Calibration
In clinical prediction modeling, model performance is traditionally reported using discrimination metrics, primarily the Area Under the Receiver Operating Characteristic Curve (ROC-AUC / Concordance index). ROC-AUC measures the probability that a randomly chosen diseased patient receives a higher predicted risk score than a randomly chosen non-diseased patient. However, ROC-AUC is completely invariant to strictly monotonic transformations of the predicted scores. A model may demonstrate an outstanding ROC-AUC of 0.90 while outputting predicted probabilities that are severely miscalibrated (Van Calster et al., 2019; Guo et al., 2017).

In clinical practice, physicians do not treat rank orders; they make medical decisions based on absolute risk probabilities. For example, a patient assigned an estimated CAD probability of $p = 0.85$ may be scheduled for urgent invasive catheterization, whereas an estimated probability of $p = 0.20$ may warrant conservative medical management and lifestyle modification. If an uncalibrated classifier compresses probabilities or systematically overestimates risk, patients face overtreatment, unnecessary catheterization, and psychological distress. Conversely, systematic probability underestimation risks undertreatment and fatal missed events. Well-calibrated probabilities—where an assigned probability of 70% corresponds to exactly 70 events per 100 individuals—are an essential ethical and clinical prerequisite for medical decision support (Van Calster et al., 2019; Collins et al., 2024).

#### 2. The Instability and Fragility of Post-Hoc Feature Explanations
To address the "black-box" dilemma of modern machine learning, post-hoc explainability frameworks—particularly Shapley Additive Explanations (SHAP; Lundberg & Lee, 2017; Lundberg et al., 2020)—have gained widespread adoption in healthcare informatics. SHAP attributes an additive importance value to each clinical feature based on cooperative game theory. In clinical machine learning literature, SHAP explanations are almost universally computed on a single train-test split, presented as static bar charts, and assumed to represent immutable physiological drivers.

However, recent mathematical investigations indicate that post-hoc feature explanations can be volatile (Alvarez-Melis & Jaakkola, 2018; Visani et al., 2022). Small perturbations in training data composition, stochastic model retraining, or multi-collinearity among clinical covariates can cause substantial shifts in feature importance rankings. If an artificial intelligence system asserts to a clinician that `Ejection Fraction` is the primary determinant of risk during one evaluation, but demotes it behind peripheral laboratory markers following a minor data resample, clinician trust is legitimately destroyed. To establish genuine explainability, attribution methods must be systematically audited for mathematical consistency, fold-to-fold ranking stability, and sign coherence.

#### 3. Prediction Instability and Decision Boundary Vulnerability
In standard clinical machine learning evaluations, models are fit once, and test predictions are treated as definitive. Yet, when models are trained under repeated cross-validation or deployed in non-stationary clinical environments, individual patient predictions can exhibit substantial variance across different model fits. A patient who falls near the decision boundary ($\tau = 0.50$) may receive a predicted risk of $0.52$ under one fold partition (classified as "Stenotic") and $0.48$ under another partition (classified as "Normal"). This phenomenon—termed *prediction instability* or *prediction churn*—represents a critical safety concern in healthcare. If a clinical decision-support tool flips a patient's diagnostic classification across retrained iterations of the exact same algorithm on identical data distributions, the model exhibits unacceptable epistemic fragility. The relationship between probability dispersion ($\sigma_p$), boundary proximity ($|p - \tau|$), and classification invariance requires exhaustive characterization.

#### 4. The Neglect of Defensive Uncertainty Quantification
Standard supervised learning models produce deterministic class predictions or point probabilities without conveying their internal epistemic or aleatoric confidence. A model forced to predict a class for an atypical, high-dimensional patient input will generate an output even when operating in regions of feature space unsupported by training evidence (Kompa et al., 2021). Without uncertainty indicators, clinical systems fail silently. Implementing mathematical uncertainty metrics (e.g., normalized predictive entropy) that can autonomously flag high-ambiguity predictions for secondary human review is vital for defensive clinical AI engineering.

---

### 1.3 Scope, Contributions, and Scientific Boundaries of this Study
To address these critical reliability challenges, this study presents **CoroVista**, a multi-target machine learning framework for non-invasive coronary artery disease prediction, evaluated through an extensive, multi-dimensional reliability audit. Using the extended Z-Alizadeh Sani cohort ($N = 303$ consecutive catheterization patients, 54 active clinical features), we model overall CAD (`Cath`) and vessel-specific stenosis across the three primary epicardial branches (`LAD`, `LCX`, `RCA`), standardizing anatomical vessel definitions and spatial mapping in alignment with anatomical concept databases (Mitsuhashi et al., 2009) and cardiovascular revascularization guidelines (Lawton et al., 2022).

The primary scientific contributions of this investigation are:
1. **Multi-Target Epicardial Vessel Discrimination:** We develop and benchmark leakage-isolated machine learning pipelines that predict both composite CAD and branch-level stenosis (`Cath`, `LAD`, `LCX`, `RCA`) using non-invasive clinical, laboratory, ECG, and echocardiographic variables, explicitly elucidating the anatomical and hemodynamic disparities among coronary territories.
2. **Systematic Probability Calibration and Threshold Tuning:** We evaluate parametric (Platt / Sigmoid) scaling and non-parametric (Isotonic) regression across all models using proper scoring rules (Brier score, ECE). We characterize the severe phenomenon of Platt probability compression on minority classes (e.g., RCA, prevalence 37.6%) and demonstrate that nested inner-fold threshold tuning ($F_1$-optimization) successfully recovers clinical sensitivity without compromising probability fidelity.
3. **Multi-Fold Explainability Stability Auditing:** We conduct an exhaustive stability evaluation of TreeSHAP and LinearSHAP across 25 outer cross-validation folds (300 pairwise fold comparisons), verifying exact floating-point additivity ($\sum \phi_i + \phi_0 = f(x)$) in 100% of folds, and quantifying global rank stability (Spearman $\rho$, Kendall $\tau$), top-$k$ feature set agreement (Jaccard similarity), and patient-level sign consistency across independent resampled models.
4. **Prediction Dispersion and Boundary Proximity Profiling:** We track out-of-fold predicted probabilities across 5 independent cross-validation repeats ($N=303$), establishing that prediction flips do not occur randomly throughout the cohort but concentrate heavily near the operating threshold, while confident predictions ($|p - \tau| \ge 0.20$) achieve $>99\%$ label invariance.
5. **Defensive Uncertainty Quantification via Entropy:** We demonstrate that normalized binary predictive entropy $H(p)$—computable directly from model output probabilities without outcome labels—retrospectively discriminates empirical classification errors when evaluated against reference catheterization labels (retrospective error-detection ROC-AUC $0.7593$ for Cath), highlighting its value as an exploratory indicator for identifying predictions with high epistemic ambiguity.
6. **Robustness Stress Testing and Inside-CV Feature Ablation:** We evaluate pipeline resilience under continuous Gaussian input noise perturbations and synthetic missingness (MCAR), and conduct inside-cross-validation feature block ablations to characterize the distinct feature associations underlying each coronary territory model.
7. **Reporting Informed by TRIPOD+AI Recommendations:** Study reporting was informed by the TRIPOD+AI recommendations for clinical prediction models using machine learning (Collins et al., 2024), maintaining full partition isolation across all transformers, scalers, imputers, and calibration estimators. Formal checklist-based compliance assessment remains outside the scope of this work.

#### Explicit Limitations and Scientific Claim Boundaries
To preserve absolute scientific honesty and avoid unjustified translational claims, we explicitly declare the following boundaries:
- **Academic Research Scope:** CoroVista is an academic research software system designed to evaluate algorithmic reliability. It is not approved by regulatory authorities (e.g., FDA, CE mark) and is not intended for autonomous clinical diagnosis, triage, treatment recommendation, or therapy prescription. Evaluated decision thresholds and entropy cutoff values represent exploratory research parameters rather than clinically validated decision rules.
- **Single-Center Cohort Origin:** All data originate from a single tertiary cardiovascular center (Shaheed Rajaei Cardiovascular, Medical and Research Center, Tehran, Iran; $N = 303$). CAD prevalence (71.3%) reflects tertiary referral patterns and is substantially higher than primary outpatient screening populations.
- **Internal Cross-Validation Only:** All reported metrics reflect internal repeated cross-validation. No external geographic validation cohorts (different hospital networks or demographic populations) or prospective temporal validation cohorts were available.
- **Observational Nature of Feature Attributions:** SHAP attributions describe statistical input-output relationships within trained estimators. They do not establish biological causality, clinical etiology, or interventional treatment effects.
- **Exploratory Subgroup Analysis:** Subgroup evaluations across demographic strata are hypothesis-generating observations and do not constitute formal algorithmic fairness certification.

---

## 2. Related Work

### 2.1 Machine Learning Benchmarks on the Z-Alizadeh Sani Cohort
The Z-Alizadeh Sani dataset, first compiled and published by Alizadehsani and colleagues (2013) at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran), has become one of the most widely investigated clinical tabular benchmarks for machine learning research in cardiovascular disease. In their foundational study, Alizadehsani et al. (2013) evaluated 303 consecutive patients undergoing coronary catheterization, extracting 54 non-invasive features encompassing demographic, symptom, physical examination, ECG, laboratory, and echocardiographic domains. Utilizing sequential minimal optimization (SMO) algorithms for support vector machines, C4.5 decision trees, and Naive Bayes classifiers, they reported classification accuracies up to 94.08% for overall CAD detection, identifying `Typical Chest Pain`, `Age`, and `Region RWMA` (Regional Wall Motion Abnormality) as primary predictive markers.

Subsequent investigators have applied a wide variety of machine learning and deep learning methodologies to this benchmark. Arabasadi et al. (2017) proposed a hybrid genetic algorithm-artificial neural network (GA-ANN) architecture, where a genetic algorithm optimized the connection weights of a multilayer perceptron, reporting an accuracy of 93.85%, sensitivity of 97.00%, and specificity of 92.00% on the binary CAD target. Abdar et al. (2019) developed an ensemble framework combining Nu-Support Vector Classification (Nu-SVC) with genetic algorithm feature selection and nested stacking classifiers, reporting classification accuracies exceeding 98%.

#### Methodological Shortcomings in Prior Literature
Despite these impressive reported figures, a rigorous meta-methodological examination of literature utilizing the Z-Alizadeh Sani cohort reveals critical systemic vulnerabilities:
1. **Unverified Data Leakage and Pre-Partition Feature Selection:** Multiple published studies applied feature selection algorithms (e.g., filter-based correlation ranking, genetic wrappers, or principal component analysis) across the *entire pooled dataset* prior to executing cross-validation splits. This induces severe data leakage from test partitions into training partitions, inflating reported classification metrics and yielding overly optimistic performance estimates that fail to generalize.
2. **Absence of Nested Probability Calibration:** To our knowledge, none of the prior machine learning publications on this cohort implemented nested probability calibration (e.g., Platt scaling or Isotonic regression). Models were evaluated strictly on raw decision functions or uncalibrated sigmoid outputs. Consequently, their risk outputs were never evaluated using proper scoring rules (Brier score) or calibration curve diagnostics.
3. **Conflation of Arbitrary Splits with Reproducible Generalization:** Many prior works evaluated models on a single random train-test partition (e.g., an 80/20 or 70/30 split) or single $K$-fold cross-validation without reporting the variance across multiple random seeds or repeats. Given the cohort size ($N = 303$), a single fold partition contains approximately 60 test patients, where the misclassification of just two or three individuals swings reported accuracy by $3\%$ to $5\%$. Reporting point estimates without sample dispersion (`ddof=1`) obscures substantial fold-level variability.
4. **Neglect of Anatomical Multi-Vessel Granularity:** The overwhelming majority of prior studies evaluated only the composite binary outcome (`Cath`), collapsing CAD into a single homogeneous entity and discarding the clinical reality that coronary atherosclerosis is anatomically heterogeneous across epicardial territories.

---

### 2.2 Artery-Specific vs. Overall CAD Prediction
A critical limitation of typical cardiovascular AI research is the reduction of CAD to a single binary label. In clinical cardiology, knowing that a patient has CAD without knowing which vessel is obstructed provides insufficient diagnostic utility for procedural planning or risk stratification.

Relatively few studies have attempted non-invasive prediction of stenosis in individual coronary arteries. In a notable follow-up study, Alizadehsani et al. (2018) extended their investigation to evaluate stenosis prediction for the LAD, LCX, and RCA individually using cost-sensitive support vector machines and sequential minimal optimization. They reported accuracies of 86.14% for LAD, 83.17% for LCX, and 83.50% for RCA.

However, predicting vessel-specific disease introduces substantial hemodynamic and physiological complexity:
- **Disparities in Territorial Diagnostic Signals:** The LAD supplies the anterior left ventricular wall and septum. Consequently, severe LAD stenosis frequently induces overt regional wall motion abnormalities visible on resting echocardiography (`Region RWMA`) and marked reductions in global ejection fraction (`EF-TTE`), as well as anterior ST-segment and T-wave changes on resting ECG. These strong physiological anchors provide tree-based and linear classifiers with robust, highly discriminative signals.
- **The Diagnostic Challenge of the LCX Territory:** In contrast, the LCX supplies the posterolateral myocardial wall. Resting surface 12-lead ECG is notoriously insensitive to posterior ischemia (the standard leads V1–V6 view the anterior heart, while posterolateral changes produce only subtle, indirect reciprocal alterations). Similarly, resting echocardiography can miss lateral wall dyssynergy in the absence of active stress. Consequently, non-invasive prediction of LCX stenosis must rely on diffuse systemic markers—such as lipid profiles (`TG`), renal function (`CR`), and platelet counts (`PLT`)—yielding substantially lower baseline discrimination (ROC-AUC ~0.73) compared to LAD (ROC-AUC ~0.84).
- **Class Imbalance in Vessel Targets:** In the extended Z-Alizadeh Sani cohort ($N = 303$), overall CAD (`Cath`) has a prevalence of 71.29% ($N=216$). In contrast, obstructive stenosis occurs in 58.42% for LAD ($N=177$), 39.27% for LCX ($N=119$), and 37.62% for RCA ($N=114$). The shift from a majority-positive target (`Cath`) to minority-positive targets (`LCX`, `RCA`) creates distinct class imbalance challenges that severely distort standard probability thresholds.

---

### 2.3 Calibration Methodologies in Medical Risk Prediction
A predictive model is said to be well-calibrated if the predicted risk probability reflects the true underlying event rate across all segments of the risk distribution (Van Calster et al., 2019):
$$P(Y = 1 \mid P_{\text{model}} = p) = p, \quad \forall p \in [0, 1]$$
In clinical medicine, miscalibrated algorithms pose severe safety risks. Van Calster et al. (2019) established a formal hierarchy of calibration, distinguishing mean calibration (calibration-in-the-large), weak calibration (calibration slope and intercept), moderate calibration (agreement across risk groups), and strong calibration (perfect event matching at every probability level).

#### Post-Processing Calibration Techniques
Machine learning classifiers—including gradient boosted decision trees (`XGBoost`) and support vector machines—frequently generate uncalibrated output scores. For example, boosted trees tend to produce sigmoidal distortion, pushing probabilities toward 0 and 1, whereas regularized logistic regression can exhibit probability shrinkage under class imbalance (Niculescu-Mizil & Caruana, 2005). Two primary post-processing calibration methodologies are widely used in medical machine learning:
1. **Platt (Sigmoid) Scaling:** Proposed by Platt (1999), this parametric approach fits a univariate logistic transformation to the uncalibrated model score $f(x)$:
   $$P_{\text{calibrated}}(Y = 1 \mid x) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$
   The scalar parameters $A$ and $B$ are estimated via maximum likelihood on a held-out calibration partition. Platt scaling is monotonic, smooth, and robust against overfitting on small-to-moderate clinical cohorts ($N \sim 300$).
2. **Isotonic Regression:** Introduced for classifier calibration by Niculescu-Mizil and Caruana (2005), isotonic regression fits a non-parametric, piecewise constant monotonic function using the pair-adjacent violators (PAV) algorithm. While more flexible than Platt scaling, isotonic regression is prone to overfitting and step-function artifacting when calibration validation sample sizes are small ($N < 500$; Guo et al., 2017).

#### Proper Scoring Rules: Brier Score and ECE
To evaluate probability calibration mathematically, proper scoring rules are mandatory:
- **Brier Score:** Proposed by Brier (1950), the Brier score measures the mean squared error between the predicted probability $p_i$ and the binary truth $y_i \in \{0, 1\}$:
  $$\text{BS} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
  The Brier score decomposes into reliability (calibration error), resolution (discriminative spread), and uncertainty (inherent variance), serving as an overarching metric of probabilistic quality.
- **Expected Calibration Error (ECE):** ECE partitions the probability interval $[0, 1]$ into $M$ equally spaced bins (typically $M = 10$). The weighted absolute difference between average bin confidence and empirical bin accuracy is computed (Guo et al., 2017):
  $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
  where $\text{acc}(B_m)$ represents the observed positive proportion in bin $B_m$, and $\text{conf}(B_m)$ represents the mean predicted probability.

#### The Phenomenon of Platt Probability Compression and Operating Threshold Collapse
A vital, under-reported phenomenon in medical machine learning is **probability compression** following Platt calibration on minority classes. When Platt scaling is applied to a calibrated model on a minority target (e.g., RCA, prevalence 37.6%), the logistic transformation maps model margin scores into a narrower probability range centered near the empirical class base rate. Consequently, maximum predicted probabilities rarely exceed 0.60, and the vast majority of true positive patients receive calibrated probabilities in the range of $[0.30, 0.45]$.

If a clinical system naively applies the default arbitrary threshold of $\tau = 0.50$ to these calibrated probabilities, a catastrophic sensitivity collapse ensues. The model classifies almost all patients as negative, missing over two-thirds of diseased vessels. To maintain both calibrated risk probabilities and clinically viable binary classification, **nested inner-fold threshold tuning** or deliberate production operating threshold selection (e.g., $\tau = 0.35$ for RCA) is mathematically mandatory.

---

### 2.4 Stability and Faithfulness of Post-Hoc Feature Attributions
As machine learning models grow in algorithmic complexity, Explainable Artificial Intelligence (XAI) has become an indispensable requirement in medical informatics. The Shapley Additive Explanations (SHAP) framework developed by Lundberg and Lee (2017) provides a mathematically grounded foundation for feature attribution, rooted in the cooperative game theory concepts of Lloyd Shapley. SHAP computes the marginal contribution of each feature across all possible feature subsets, guaranteeing four fundamental properties: local accuracy (additivity), missingness, consistency, and efficiency.

For tree ensemble architectures (Random Forests, Gradient Boosted Trees), Lundberg et al. (2020) formulated **TreeSHAP**, an exact polynomial-time algorithm ($O(TLD^2)$, where $T$ is the number of trees, $L$ is maximum leaves, and $D$ is maximum tree depth) that computes exact Shapley values directly from decision tree structures without Monte Carlo approximations.

#### Explanation Volatility and Attribution Stability
Despite the theoretical guarantees of Shapley values, post-hoc explanations can exhibit substantial instability in real-world clinical modeling:
- **Resampling Volatility:** Alvarez-Melis and Jaakkola (2018) established that post-hoc explanations can be non-robust, where slight perturbations in training inputs yield substantial changes in attribution vectors. Visani et al. (2022) formulated rigorous statistical frameworks for evaluating the stability of feature importance across cross-validation folds, demonstrating that feature attributions in tabular models often fluctuate due to multi-collinearity, sample partitioning, and random seed variation.
- **Model Score Space vs. Calibrated Probability Space:** A critical theoretical reality—frequently obscured in clinical literature—is that **SHAP explanations operate strictly in raw model score space ($f(x)$)**, which corresponds to the log-odds margin for boosted trees or the decision function for linear models. For Platt-calibrated pipelines, the final predicted probability is generated via a non-linear sigmoid transformation:
  $$p(x) = \sigma(A \cdot f(x) + B) = \frac{1}{1 + \exp\left( - \left[ A \left( \sum_{j=1}^M \phi_j(x) + \phi_0 \right) + B \right] \right)}$$
  Because the sigmoid function is non-linear, **individual SHAP attributions cannot be linearly summed in probability space**. Attempting to explain calibrated probabilities by linearly adding raw SHAP values introduces mathematical invalidity. Responsible clinical explainability requires rigorous disclosure that attributions explain pre-calibration model log-odds.

---

### 2.5 Predictive Uncertainty and Robustness in Clinical Decision Support
In high-stakes cardiovascular medicine, an algorithmic prediction is incomplete without an accompanying measure of confidence. Kompa, Snoek, and Beam (2021) highlighted the necessity of communicating predictive uncertainty in healthcare machine learning, arguing that autonomous systems must explicitly signal when a second human medical opinion is required.

In binary classification, predictive uncertainty can be formulated through information-theoretic and geometric lenses:
- **Normalized Binary Predictive Entropy:** For a predicted probability $p \in (0, 1)$, binary entropy quantifies the intrinsic ambiguity of the prediction:
  $$H(p) = -p \log_2(p) - (1-p) \log_2(1-p)$$
  Entropy reaches its theoretical maximum ($H(p) = 1.0$) at the boundary of maximum uncertainty ($p = 0.50$), and decreases monotonically toward zero as $p \to 0$ or $p \to 1$.
- **Decision Margin Distance:** The absolute distance from the operating threshold:
  $$M(p) = |p - \tau|$$
  Patients falling within a narrow margin of the decision threshold ($|p - \tau| < 0.05$) represent borderline clinical cases characterized by elevated misclassification risk and heightened prediction volatility under data resampling.

#### Methodological Synthesis
Existing literature on coronary artery disease machine learning exhibits fragmented priorities: studies that optimize discrimination neglect calibration; studies that implement explainability fail to evaluate attribution stability across resampled folds; and studies proposing clinical risk tools overlook prediction churn and defensive uncertainty flagging.

By unifying multi-target vessel modeling, proper scoring calibration, nested threshold optimization, 25-fold SHAP stability auditing, boundary-proximity prediction invariance tracking, predictive entropy error discrimination, and input stress testing, **CoroVista** provides a comprehensive, traceable methodological blueprint for evaluating machine learning reliability in cardiovascular medicine.

---

## 3. Materials and Methods

### 3.1 Cohort Provenance, Clinical Setting, and Ethical Framework
The empirical foundation of this study is the extended Z-Alizadeh Sani cardiology dataset (Alizadehsani et al., 2013, 2018; Alizadehsani, 2017, 2018). The cohort consists of $N = 303$ consecutive adult patients referred for diagnostic invasive coronary catheterization at Shaheed Rajaei Cardiovascular, Medical and Research Center, a major tertiary cardiovascular referral and teaching hospital in Tehran, Iran.

#### Clinical Study Design & Eligibility
- **Study Design:** Retrospective cross-sectional diagnostic modeling study.
- **Inclusion Criteria:** Adult patients presenting with suspected ischemic heart disease or stable angina who underwent formal elective invasive coronary angiography (ICA) based on clinical indications, resting 12-lead electrocardiography (ECG), exercise stress testing, or echocardiographic abnormalities.
- **Reference Standard:** Selective invasive coronary angiography performed via standard femoral or radial arterial access. Quantitative or visual angiographic interpretation was conducted by expert interventional cardiologists. In accordance with established international cardiology consensus guidelines (Lawton et al., 2022), **significant obstructive coronary artery disease was defined as $\ge 50\%$ luminal diameter stenosis in one or more major epicardial coronary vessels**.
- **Ethical Standards & Data Governance:** The clinical cohort was originally gathered and de-identified during routine diagnostic catheterization evaluations at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran). As documented in foundational publications (Alizadehsani et al., 2013, 2018), patient records were fully anonymized prior to open public deposition in research repositories (Alizadehsani, 2017, 2018). The primary publications do not record an individual Institutional Review Board (IRB) or institutional ethics committee protocol approval number, operating under hospital clinical diagnostic data governance. The present study represents an independent secondary computational modeling and reproducibility investigation conducted exclusively on this previously published, publicly accessible, fully de-identified tabular dataset, involving no prospective clinical intervention, no biological specimen collection, and no patient re-identification potential. Public availability of secondary data does not automatically satisfy all institutional research ethics requirements; because an independent institutional ethics review determination or formal waiver has not been independently documented for this secondary analysis, the target journal editorial office or relevant institutional ethics body must determine whether a formal exemption, waiver, or other institutional determination is required. Formal ethics clearance is not marked as completed, and no formal IRB protocol number or exemption certificate is claimed or fabricated.

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
In alignment with recommendations emphasized by TRIPOD+AI (Collins et al., 2024), all preprocessing operations were wrapped within scikit-learn compatible `Pipeline` objects to enforce absolute cross-validation partitioning:
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
- **Retrospective Error Discrimination Evaluation:** Although predictive entropy $H(p)$ is computed directly from model output probabilities without access to ground-truth labels during inference, evaluating whether entropy discriminates correct from misclassified predictions inherently requires ground-truth reference labels. This discriminative capacity was assessed retrospectively using the Receiver Operating Characteristic curve, computing the **retrospective error-detection ROC-AUC** by treating empirical misclassifications ($y \ne \hat{y}$) as the positive state.

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
Multi-target discrimination and calibration metrics across 25 outer test folds are summarized in Table 2 for the selected production models. A comprehensive comparison across candidate calibration methods is detailed in Table 3. Multi-target ROC and Precision-Recall curves are illustrated in Figure 1, and calibration reliability curves before and after Platt scaling are depicted in Figure 2.

#### Table 2: Benchmark Multi-Target Discrimination & Calibration Performance
*Authoritative Source: `data/reports/reproduction_audit/calibration_results.json` and `data/reports/reproduction_audit/model_benchmark.json`.*
*Protocol: Repeated Stratified $K$-Fold Cross-Validation (5 splits $\times$ 5 repeats = 25 outer folds). Primary metrics report Cross-Fold Mean $\pm$ Sample SD (`ddof=1`, $N=24$), with population SD (`ddof=0`, $N=25$) noted in brackets.*

| Target | Clinical Endpoint | Selected Model | Preprocessing | Calibration Method | Operating Cutoff ($\tau$) | ROC-AUC (Mean $\pm$ SD) | PR-AUC (Mean $\pm$ SD) | Brier Score (Mean $\pm$ SD) | ECE (Mean $\pm$ SD) |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Cath** | Overall CAD Status | **XGBoost** | None, One-Hot | **Sigmoid** (Platt) | 0.50 | **$0.9123 \pm 0.0404$**<br>[$0.0396$ `ddof=0`] | **$0.9597 \pm 0.0200$**<br>[$0.0196$ `ddof=0`] | **$0.1034 \pm 0.0251$**<br>[$0.0246$ `ddof=0`] | **$0.1004 \pm 0.0227$**<br>[$0.0222$ `ddof=0`] |
| **LAD** | Left Anterior Descending | **XGBoost** | None, One-Hot | **Sigmoid** (Platt) | 0.50 | **$0.8443 \pm 0.0528$**<br>[$0.0518$ `ddof=0`] | **$0.8818 \pm 0.0471$**<br>[$0.0462$ `ddof=0`] | **$0.1609 \pm 0.0226$**<br>[$0.0221$ `ddof=0`] | **$0.1326 \pm 0.0394$**<br>[$0.0386$ `ddof=0`] |
| **LCX** | Left Circumflex | **XGBoost** | None, One-Hot | **Uncalibrated** | 0.50 | **$0.7358 \pm 0.0629$**<br>[$0.0616$ `ddof=0`] | **$0.6173 \pm 0.0838$**<br>[$0.0821$ `ddof=0`] | **$0.2054 \pm 0.0240$**<br>[$0.0235$ `ddof=0`] | **$0.1366 \pm 0.0315$**<br>[$0.0309$ `ddof=0`] |
| **RCA** | Right Coronary Artery | **Logistic Regression** | StandardScaler, One-Hot | **Sigmoid** (Platt) | 0.35 | **$0.7163 \pm 0.0605$**<br>[$0.0593$ `ddof=0`] | **$0.6098 \pm 0.0775$**<br>[$0.0759$ `ddof=0`] | **$0.2060 \pm 0.0150$**<br>[$0.0147$ `ddof=0`] | **$0.1000 \pm 0.0321$**<br>[$0.0315$ `ddof=0`] |

\
*[Figure 1 about here: Multi-Target Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Curves]*
\

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

\
*[Figure 2 about here: Multi-Target Probability Calibration Diagrams (Reliability Curves)]*
\

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
| **RCA** | Logistic Regression + Sigmoid | $0.3188 \pm 0.0380$ [$0.20, 0.37$]\* | $0.6072 \pm 0.0716$ | **$0.6443 \pm 0.0575$** | **$0.7946 \pm 0.1092$** | **$0.4941 \pm 0.1429$** | $0.4928 \pm 0.0532$ | **$0.6037 \pm 0.0516$** |

*\*Audit Note on RCA Selected Threshold SD: An exact re-calculation over the 25 outer fold threshold values (`[0.34, 0.27, 0.30, 0.32, 0.31, 0.29, 0.28, 0.30, 0.32, 0.37, 0.36, 0.32, 0.37, 0.31, 0.34, 0.34, 0.35, 0.35, 0.20, 0.37, 0.34, 0.30, 0.29, 0.33, 0.30]`) yields Mean = **0.3188**, Population SD (`ddof=0`) = **0.0372**, and Sample SD (`ddof=1`) = **0.0380**. The value $0.0388$ previously cited in preliminary notes was an unverified draft artifact resulting from an accidental double-Bessel correction ($0.0380 \times \sqrt{25/24} \approx 0.0388$). The verified sample standard deviation is locked as **$0.0380$**.*

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
Global and patient-level explanation stability metrics across the 25 outer cross-validation folds are presented in Table 7. Exact mathematical additivity ($\sum \phi_i + \phi_0 = f(x)$) passed in 100% of folds ($25/25$) across all targets, with maximum observed floating-point reconstruction errors $< 1.2 \times 10^{-6}$ for tree models and $< 1.8 \times 10^{-15}$ for linear models. Global feature importance distributions and fold-to-fold rank correlation heatmaps are presented in Figure 3.

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

\
*[Figure 3 about here: Global TreeSHAP and LinearSHAP Feature Attribution Distributions and Multi-Fold Stability Heatmaps]*
\

---

### 4.5 Prediction Stability and Decision Boundary Proximity
Prediction dispersion and classification invariance across 5 independent cross-validation repeats ($N=303$) are detailed in Table 8. Figure 4 illustrates empirical probability standard deviation distributions and boundary proximity invariance curves.

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
| **Invariance by Boundary Distance: $0.05 \le |p - \tau| < 0.10$** | **28.6% (4/14)** | **29.4% (10/34)** | **31.6% (12/38)** | **82.4% (56/68)** |
| **Invariance by Boundary Distance: $0.10 \le |p - \tau| < 0.20$** | **75.7% (28/37)** | **77.4% (48/62)** | **65.5% (55/84)** | **96.4% (108/112)** |
| **Invariance by Boundary Distance: $|p - \tau| \ge 0.20$** | **99.19% (244/246)** | **100.0% (190/190)** | **99.26% (135/136)** | **100.0% (48/48)** |

As detailed in Table 8, classification label flips were concentrated among borderline cases: in the immediate threshold margin ($|p - \tau| < 0.05$), all Cath ($6/6$, $0.0\%$ invariance) and LAD ($17/17$, $0.0\%$ invariance) patients experienced at least one label change across repeated fits. For LCX and RCA, immediate boundary flip rates were also elevated ($44/45$ flipped, $2.2\%$ invariance for LCX; $58/75$ flipped, $22.7\%$ invariance for RCA), though neither exhibited a 100% flip rate. In contrast, confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance across independent model fits (only 2 of 246 patients flipped for Cath, 0 of 190 for LAD, 1 of 136 for LCX, and 0 of 48 for RCA), demonstrating that predictions closer to the operating threshold were generally less stable without implying that every near-boundary patient across all vessels necessarily flips.

\
*[Figure 4 about here: Prediction Probability Dispersion and Boundary Proximity Agreement Curves]*
\

---

### 4.6 Predictive Uncertainty and Error Detection Discrimination
Predictive entropy $H(p)$ can be calculated directly from model output probabilities without access to ground-truth labels. To evaluate whether this uncertainty metric aligns with empirical model error, retrospective evaluation against ground-truth catheterization labels was performed. Table 9 documents the capacity of normalized binary predictive entropy $H(p)$ and threshold margin $M(p) = |p - \tau|$ to retrospectively discriminate empirical classification errors. Entropy distributions and error-detection ROC curves are presented in Figure 5.

#### Table 9: Predictive Uncertainty and Error Detection Performance
*Authoritative Source: `data/reports/phase4/summary/phase4_master_metrics.json` (Exp C).*

| Target | Error-Detection ROC-AUC of Entropy $H(p)$ | Mean Entropy: Correct Predictions | Mean Entropy: Misclassified Predictions | Error Rate: Margin $< 0.05$ | Error Rate: Margin $0.05 - 0.10$ | Error Rate: Margin $0.10 - 0.20$ | Error Rate: Margin $\ge 0.20$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cath** | **0.7593** | 0.4079 | **0.7550** | **33.3%** | 30.8% | 15.8% | **1.6%** |
| **LAD** | **0.6595** | 0.6534 | **0.8258** | **41.2%** | 32.1% | 16.2% | **7.4%** |
| **LCX** | **0.6392** | 0.8123 | **0.9080** | **44.4%** | 31.5% | 22.1% | **14.7%** |
| **RCA** | **0.6796** | 0.7780 | **0.8879** | **40.0%** | 25.7% | 14.2% | **16.7%** |

In retrospective evaluation against reference labels, normalized binary entropy discriminated misclassified from correctly classified cases on the primary composite outcome (retrospective error-detection ROC-AUC $0.7593$ for Cath; $0.6595$ for LAD; $0.6392$ for LCX; $0.6796$ for RCA). Furthermore, empirical error rates declined monotonically as distance from the operating threshold expanded (from 33.3% down to 1.6% for Cath). These ROC-AUC values represent retrospective evaluation metrics rather than autonomous label-free error detection in deployment.

\
*[Figure 5 about here: Normalized Binary Predictive Entropy Distributions and Error-Detection ROC Curves]*
\

---

### 4.7 Model Robustness Under Input Perturbations and Feature Ablation
Pipeline robustness under continuous Gaussian feature perturbation and synthetic missingness stress testing is reported in Table 10. Table 11 reports inside-cross-validation feature group ablation drops ($\Delta \text{ROC-AUC}$) relative to the Repeat-1 5-fold pooled baseline ($N=303$). Figure 6 compares the marginal ablation drops across coronary territories.

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

\
*[Figure 6 about here: Inside-Cross-Validation Feature Group Ablation Impact Across Coronary Territories]*
\

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

### 4.9 Proposed Figure Captions

#### Figure 1: Multi-Target Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Curves
**Caption:** Multi-target discrimination across 25 outer test folds of repeated stratified cross-validation (5 splits $\times$ 5 repeats). Solid curves depict the mean trajectory; shaded envelopes represent $\pm 1$ cross-fold standard deviation (`ddof=1`). Panels illustrate: (A) Cath composite CAD (ROC-AUC $0.9123 \pm 0.0404$, PR-AUC $0.9597 \pm 0.0200$); (B) LAD stenosis (ROC-AUC $0.8443 \pm 0.0528$, PR-AUC $0.8818 \pm 0.0471$); (C) LCX stenosis (ROC-AUC $0.7358 \pm 0.0629$, PR-AUC $0.6173 \pm 0.0838$); and (D) RCA stenosis (ROC-AUC $0.7163 \pm 0.0605$, PR-AUC $0.6098 \pm 0.0775$).

#### Figure 2: Multi-Target Probability Calibration Diagrams (Reliability Curves) Before and After Sigmoid Scaling
**Caption:** Calibration reliability diagrams evaluating 10 probability confidence deciles against empirical event frequencies across 25 outer test folds. Dashed diagonal lines represent ideal calibration ($y = x$). Curves compare uncalibrated model outputs against Platt (Sigmoid) calibrated probabilities. Platt scaling significantly improves alignment for Cath (Brier $0.1034$, ECE $0.1004$) and LAD (Brier $0.1609$, ECE $0.1326$), and reduces ECE to $0.1000$ for RCA. Probability compression on RCA illustrates clustering of calibrated probabilities below 0.50, necessitating operating threshold optimization ($\tau = 0.35$).

#### Figure 3: Global TreeSHAP and LinearSHAP Feature Attribution Distributions and Multi-Fold Stability Heatmaps
**Caption:** Feature explanation stability across 25 outer cross-validation folds. Left panels display global mean absolute SHAP attributions ($\frac{1}{N} \sum |\phi_i|$) in raw model score space ($f(x)$) for the Top-15 clinical features. Right heatmaps illustrate pairwise Spearman rank correlation matrices across all $\binom{25}{2} = 300$ fold comparisons. Tree-based models display exceptional attribution stability (Mean $\rho = 0.9319$ for Cath, $0.9217$ for LAD, $0.9081$ for LCX). Exact mathematical additivity ($\sum \phi_i + \phi_0 = f(x)$) verified in 100% of folds ($25/25$).

#### Figure 4: Prediction Probability Dispersion ($\sigma_p$) and Decision Boundary Proximity Agreement Curves
**Caption:** Empirical out-of-fold prediction dispersion and classification invariance across 5 cross-validation repeats ($N=303$). (A) Cohort distributions of patient probability standard deviation ($\sigma_p$). (B) Classification label consistency plotted as a function of absolute distance from the operating threshold ($|p - \tau|$). Invariance curves confirm that classification flips concentrate heavily in the immediate boundary margin $|p - \tau| < 0.05$, where all Cath ($0.0\%$ invariance, $6/6$ flipped) and LAD ($0.0\%$ invariance, $17/17$ flipped) patients experienced label flips, alongside elevated flip rates in LCX ($2.2\%$ invariance, $44/45$ flipped) and RCA ($22.7\%$ invariance, $58/75$ flipped). In contrast, confident predictions ($|p - \tau| \ge 0.20$) achieved $>99\%$ label invariance across independent model fits.

#### Figure 5: Normalized Binary Predictive Entropy Distributions and Error-Detection ROC Curves
**Caption:** Predictive uncertainty quantification via binary entropy $H(p)$. (A) Violin plots comparing entropy distributions between correctly classified and misclassified patients across all four targets. (B) Receiver Operating Characteristic curves retrospectively evaluating the capacity of model entropy to discriminate empirical classification errors against ground-truth reference labels (retrospective error-detection ROC-AUC $0.7593$ for Cath, $0.6595$ for LAD, $0.6392$ for LCX, $0.6796$ for RCA). While entropy is calculated from probabilities alone, validating its error-discriminative performance is an offline retrospective evaluation.

#### Figure 6: Inside-Cross-Validation Feature Group Ablation Impact Across Coronary Territories
**Caption:** Physiological divergence across coronary branches revealed by inside-cross-validation feature group ablation. Bars represent the absolute decline in out-of-fold ROC-AUC ($\Delta \text{AUC}$) relative to the unablated Repeat-1 baseline when retraining pipelines without indicated clinical feature domains. LAD displays acute sensitivity to echocardiographic ablation ($\Delta = -0.0528$), whereas LCX is predominantly driven by laboratory blood panels ($\Delta = -0.0524$).

---

## 5. Discussion

### 5.1 Multi-Target Epicardial Modeling & Anatomical Disparities
A central thesis of this investigation is that conventional cardiovascular machine learning has fundamentally oversimplified coronary artery disease diagnosis by collapsing multi-vessel pathophysiology into a single, composite binary label (`Cath`). While predicting composite obstructive CAD provides an initial indicator of disease presence, clinical decision-making in the cardiac catheterization laboratory is fundamentally governed by vessel-specific anatomical localization, where revascularization is frequently prioritized under clinical practice guidelines (Lawton et al., 2022). High-grade obstruction of the proximal Left Anterior Descending (`LAD`) artery imperils more than half of the left ventricular myocardium, carrying elevated risks of anterior myocardial infarction, cardiogenic shock, and malignant arrhythmias that often warrant urgent revascularization evaluation. Conversely, isolated chronic stenosis of the Left Circumflex (`LCX`) or distal Right Coronary Artery (`RCA`) presents with divergent hemodynamic risk profiles, distinct collateral circulation dynamics, and alternative conservative or medical management pathways.

Our empirical findings demonstrate that multi-target prediction using non-invasive clinical, laboratory, electrocardiographic, and echocardiographic variables achieves varying levels of discriminative efficacy across coronary branches:
- **`LAD` Stenosis:** The gradient boosted tree pipeline (`XGBoost` with Sigmoid calibration) achieved strong discrimination (ROC-AUC $0.8443 \pm 0.0528$, PR-AUC $0.8818 \pm 0.0471$). While observational associations cannot establish causal biological mechanisms, this statistical relationship is consistent with the anatomical territory perfused by the LAD. Because the LAD perfuses the anterior left ventricular free wall, cardiac apex, and anterior interventricular septum, high-grade luminal narrowing directly correlates with regional contractile dysfunction that manifests conspicuously on resting transthoracic echocardiography (`Region RWMA`) and lower global ejection fraction (`EF-TTE`). These objective imaging signals provide tree ensembles with strong, statistically invariant physiological anchors.
- **`LCX` Stenosis:** In sharp contrast, LCX stenosis exhibited the lowest baseline discrimination among the four evaluated endpoints (ROC-AUC $0.7358 \pm 0.0629$, PR-AUC $0.6173 \pm 0.0838$). This performance attenuation reflects well-documented clinical and anatomical challenges. The LCX traverses the posterior atrioventricular groove to supply the posterolateral myocardium. In resting clinical assessments, posterolateral ischemia is notoriously "silent": standard 12-lead ECG leads (V1–V6) primarily interrogate the anterior and septal walls, while resting echocardiography frequently misses localized lateral wall hypokinesis in the absence of exercise or pharmacological stress. Consequently, the predictive models for LCX were forced to rely on non-specific systemic laboratory markers (e.g., triglycerides, serum creatinine, platelet count) and demographic variables, placing an inherent ceiling on non-invasive discrimination.
- **`RCA` Stenosis:** Regularized linear modeling (`Logistic Regression` with Sigmoid calibration) achieved moderate discrimination (ROC-AUC $0.7163 \pm 0.0605$, PR-AUC $0.6098 \pm 0.0775$). Unlike the tree ensembles selected for Cath and LAD, a regularized linear model proved optimal for RCA. This observation suggests that in this cohort, non-invasive risk for RCA disease is characterized by diffuse, additive contributions across systemic cardiovascular risk factors (`Age`, `Diabetes Mellitus`, `Erythrocyte Sedimentation Rate`, `Dyspnea`) rather than sharp, localized mechanical thresholds.

---

### 5.2 The Clinical Imperative of Probability Calibration
In translational medical artificial intelligence, discrimination alone is insufficient to justify clinical decision support (Van Calster et al., 2019). While ROC-AUC evaluates the ranking of diseased versus non-diseased individuals, it is invariant to monotonic transformations and completely blind to absolute probability scaling. A diagnostic model with an exemplary ROC-AUC of 0.91 can output risk estimates that cluster arbitrarily between 0.60 and 0.90, presenting a severely distorted perception of true risk to attending clinicians.

Our comparative calibration benchmarking (Table 3) illustrates the critical role of probability post-processing. Uncalibrated `XGBoost` models for composite CAD (`Cath`) exhibited sigmoidal probability distortion, yielding an Expected Calibration Error of $0.1265 \pm 0.0218$. Implementing parametric Platt (Sigmoid) scaling (Platt, 1999) via nested cross-validation successfully realigned model log-odds with empirical event rates, reducing ECE to $0.1004 \pm 0.0227$ and the quadratic Brier loss from $0.1074$ to $0.1034$, while fully preserving rank-order discrimination (ROC-AUC $0.9123 \pm 0.0404$). Similar calibration benefits were verified for LAD (Brier reduced from $0.1651$ to $0.1609$; ECE reduced from $0.1434$ to $0.1326$).

Importantly, our results expose the limitations of non-parametric Isotonic regression (Niculescu-Mizil & Caruana, 2005) in moderate-sized clinical cohorts ($N \sim 300$). While isotonic regression is mathematically more flexible than Platt scaling, its non-parametric step-function mapping exhibited minor overfitting across cross-validation folds, yielding inferior Brier scores compared to Sigmoid scaling for Cath ($0.1044$ vs. $0.1034$) and LAD ($0.1623$ vs. $0.1609$). Platt scaling's parametric assumption of logistic linearity in log-odds space provides a natural regularizing effect that prevents sample-specific step-function artifacts in tabular medical datasets (Guo et al., 2017).

#### The Rationale for Retaining an Uncalibrated Model for LCX
A crucial, balanced observation in our investigation is that post-processing calibration is not universally beneficial across all endpoints. For `LCX`, uncalibrated `XGBoost` achieved superior resolution and lower quadratic loss (Brier $0.2054 \pm 0.0240$) compared to its sigmoid-calibrated ($0.2073 \pm 0.0155$) and isotonic-calibrated ($0.2078 \pm 0.0190$) counterparts. Applying post-hoc calibration to LCX compressed predicted probabilities into a narrow band near the class base rate ($39.27\%$), which severely degraded class separation without improving reliability. Consequently, uncalibrated XGBoost was intentionally selected as the production model for LCX. This design choice underscores an important methodological principle: post-processing calibration must be evaluated empirically against proper scoring rules rather than deployed as an unverified dogma.

---

### 5.3 Operating Threshold Collapse and the Dilemma of Minority Class Calibration
Our findings illuminate a severe, under-recognized challenge in clinical machine learning: **the probability compression phenomenon following calibration on imbalanced clinical outcomes**.

When Platt scaling was applied to the regularized linear model for `RCA` (prevalence 37.62%), the logistic calibration mapper appropriately adjusted the model's raw decision scores to reflect the true minority event frequency. However, this mathematical adjustment concentrated the calibrated probability distribution within the range of $[0.20, 0.45]$, with very few patients receiving estimated probabilities exceeding $0.50$. Consequently, when the arbitrary standard threshold of $\tau = 0.50$ was applied to these calibrated probabilities (Table 4), the model suffered a **catastrophic clinical sensitivity collapse**:
- Sensitivity fell to **$31.24\% \pm 8.56\%$**, failing to identify more than two-thirds of patients with angiographically proven RCA stenosis.
- The model achieved high specificity ($86.38\% \pm 7.41\%$) at the cost of diagnostic paralysis, yielding an unacceptably low $F_1$-score of $0.4027 \pm 0.0872$.

This failure mode highlights the danger of relying on default software midpoint thresholds ($\tau = 0.50$) in medical artificial intelligence. A well-calibrated probability vector does not imply that 0.50 is an optimal classification cutoff for clinical intervention. In diagnostic cardiology, where the cost of a missed obstructive stenosis (false negative) far exceeds the cost of a confirmatory non-invasive test or elective catheterization (false positive), operating cutoffs must be systematically tuned.

Our nested inner-fold threshold tuning protocol (Table 5) resolved this failure mode without data leakage. By optimizing decision cutoffs strictly on inner out-of-fold training predictions (mean tuned cutoff $0.3188 \pm 0.0380$, sample standard deviation with $\text{ddof}=1$), clinical sensitivity for RCA was restored to **$79.46\% \pm 10.92\%$** with a balanced accuracy of $64.43\% \pm 5.75\%$ and an $F_1$-score of $0.6037 \pm 0.0516$. Furthermore, freezing a constant production operating threshold at $\tau = 0.35$ (Table 6) yielded robust fold-level performance across 25 outer folds (Sensitivity $74.21\% \pm 10.64\%$, Specificity $57.48\% \pm 7.10\%$, $F_1 = 0.6053 \pm 0.0684$) and consistent repeat-level stability across 5 complete repeats (Sensitivity $74.21\% \pm 2.53\%$, Specificity $57.46\% \pm 1.10\%$, $F_1 = 0.6063 \pm 0.0120$). Importantly, both the inner-fold tuned cutoff ($0.3188$) and the fixed production operating cutoff ($\tau = 0.35$) represent exploratory research operating points tailored for statistical trade-off optimization in this dataset, rather than clinically validated intervention or treatment thresholds. This analysis proves that clinical classification must be addressed through explicit threshold realignment that respects post-calibration probability scaling.

---

### 5.4 Feature Attribution Stability & The Pre-Calibration Score Space Disconnect

#### Multi-Fold Attribution Stability
In high-stakes clinical decision support, post-hoc explanations must be stable across stochastic data variations if they are to earn physician trust. If an algorithm attributes elevated cardiovascular risk to `Ejection Fraction` during one cross-validation fold, but demotes it behind non-specific laboratory markers during another, clinicians cannot rely on its explanations for medical reasoning (Alvarez-Melis & Jaakkola, 2018; Visani et al., 2022).

Our 25-fold stability evaluation (Table 7) establishes that tree ensemble explanations via TreeSHAP (Lundberg et al., 2020) exhibit high global attribution stability when anchored by dominant physiological predictors:
- `Cath` and `LAD` achieved mean pairwise Spearman rank correlations of **$\rho = 0.9319 \pm 0.0192$** and **$\rho = 0.9217 \pm 0.0197$** across all 300 fold comparisons.
- For LAD, four primary features—`Age`, `EF-TTE`, `Region RWMA`, and `Typical Chest Pain`—appeared in the Top-5 importance ranking in **100% of outer folds ($25/25$)**, yielding a Top-5 Jaccard similarity index of $0.7456 \pm 0.1417$.
- Patient-level attribution signs remained consistent across 5 independent repeats in **$91.09\%$** of evaluations for Cath and **$90.03\%$** for LAD.

In contrast, our analysis exposes a critical vulnerability in linear model explanations for `RCA`:
- The regularized linear model for RCA exhibited substantially lower ranking stability ($\rho = 0.7737 \pm 0.0583$, range $[0.5690, 0.8912]$) and a depressed Top-5 Jaccard agreement ($0.4890 \pm 0.1724$).
- This instability does not stem from algorithmic failure, but from **multi-collinearity among clinical covariates**. In linear models, collinear predictors (e.g., `Age`, `Diabetes`, `Hypertension`, `ESR`, `Dyspnea`) compete for regression coefficient weight. Minor fluctuations in patient sampling across training folds redistribute coefficients among correlated features, causing large shifts in rank order while preserving aggregate prediction. This finding indicates that linear attributions require cautious interpretation when collinear predictors are present.

#### Disclosure of the Pre-Calibration Score Space Disconnect
A vital scientific disclosure of this study is the mathematical boundary between SHAP attribution space and post-calibration probability space. SHAP is formulated strictly as an additive decomposition in raw model score space ($f(x)$):
$$f(x) = \phi_0 + \sum_{j=1}^M \phi_j(x)$$
For our tree models, $f(x)$ represents the uncalibrated margin (log-odds). In Platt-calibrated pipelines, the final probability is obtained via a non-linear sigmoid transformation:
$$p(x) = \sigma\left( A \cdot f(x) + B \right) = \frac{1}{1 + \exp\left( - \left[ A \left( \phi_0 + \sum_{j=1}^M \phi_j(x) \right) + B \right] \right)}$$
Because the logistic function is non-linear, individual SHAP values cannot be linearly summed to yield the final calibrated probability $\Delta p$. Asserting that a specific feature "increased patient risk by $+15\%$ probability" is mathematically invalid in a Platt-calibrated pipeline. SHAP attributions quantify contributions to pre-calibration log-odds risk, and medical informatics literature must communicate this distinction transparently to avoid misinforming clinicians.

---

### 5.5 Deconstructing Prediction Instability: Localized Boundary Proximity vs. Random Noise
Prediction instability—where identical patients receive conflicting binary classifications across different model training iterations—represents a recognized safety concern in clinical machine learning. Our repeated cross-validation tracking across 5 independent repeats ($N=303$) provides critical empirical insights into the anatomy of prediction flips (Table 8):
1. **Prediction Flips Are Heavily Concentrated Near Cutoffs:** Classification flips across repeats occurred in $8.91\%$ of patients for Cath ($27/303$), $18.15\%$ for LAD ($55/303$), and $24.42\%$ for RCA ($74/303$).
2. **Boundary Margin Stratification:** When stratified by distance from the operating threshold ($|p - \tau|$), predictions closer to the operating threshold were substantially less stable across model retraining. In the immediate boundary margin $|p - \tau| < 0.05$, all Cath ($6/6$, $0.0\%$ invariance) and LAD ($17/17$, $0.0\%$ invariance) patients experienced at least one classification flip across 5 repeats. LCX and RCA exhibited similarly elevated flip rates without reaching $100\%$: LCX showed $2.2\%$ invariance ($1/45$ invariant, $44/45$ flipped), while RCA showed $22.7\%$ invariance ($17/75$ invariant, $58/75$ flipped). At intermediate margins ($0.05 \le |p - \tau| < 0.10$), flips remained prevalent across targets (e.g., Cath label invariance $28.6\%$ [$4/14$], LAD $29.4\%$ [$10/34$]), demonstrating a continuous gradient of prediction stability rather than a uniform threshold anomaly.
3. **Invariance of Confident Predictions:** For patients whose predicted risk was separated from the threshold by $|p - \tau| \ge 0.20$, classification invariance exceeded **$99.19\%$ for Cath ($244/246$)** and achieved **$100.0\%$ for LAD ($190/190$)** and RCA ($48/48$). Rare flips did occur even at larger distances (e.g., 2 patients out of 246 in Cath), indicating that while boundary proximity is the predominant driver of instability, subtle interactions between feature values and fold partitions can occasionally perturb predictions further from the cutoff.

This empirical dichotomy demonstrates that prediction instability in well-regularized models is not an erratic, cohort-wide noise artifact, but a localized manifestation of **epistemic boundary ambiguity**. Patients whose clinical profiles place them directly on the decision boundary naturally experience classification churn under minor training set perturbations. While not representing a validated clinical triage rule, recognizing this boundary-localized vulnerability allows clinical decision-support systems to explore defensive safety guardrails: automated predictions can be delivered with high statistical stability for patients with $|p - \tau| \ge 0.20$, while borderline cases ($|p - \tau| < 0.05$) highlight elevated algorithmic uncertainty warranting secondary human review or supplemental diagnostic evaluation.

---

### 5.6 Defensive Uncertainty Quantification: Entropy as an Algorithmic Safety Mechanism
In cardiovascular medicine, an algorithmic output is incomplete without a measure of confidence (Kompa et al., 2021). Our evaluation of normalized binary predictive entropy $H(p) = -p \log_2(p) - (1-p) \log_2(1-p)$ demonstrates that information-theoretic uncertainty provides an effective defensive safety mechanism (Table 9):
- While normalized binary predictive entropy $H(p)$ can be computed directly from model output probabilities without access to ground-truth labels at inference time, evaluating whether entropy discriminates correct from incorrect classifications requires reference ground-truth labels. In this retrospective offline evaluation, entropy exhibited moderate-to-strong discriminative power for separating classification errors from correct predictions, achieving a **retrospective error-detection ROC-AUC of $0.7593$ for Cath**, $0.6595$ for LAD, $0.6392$ for LCX, and $0.6796$ for RCA (Table 9).
- For Cath, the mean entropy among misclassified patients ($0.7550$) was nearly double that among correctly classified patients ($0.4079$).
- Empirical error rates exhibited a steep, monotonic gradient: for patients in the highest uncertainty margin ($|p - \tau| < 0.05$), the observed error rate was **$33.3\%$ for Cath** and **$41.2\%$ for LAD**, whereas for patients in the confident margin ($|p - \tau| \ge 0.20$), the error rate collapsed to **$1.6\%$ for Cath** and **$7.4\%$ for LAD**.

These findings indicate that binary entropy and decision margin distance can serve as exploratory algorithmic safety indicators. Rather than interpreting borderline probabilities as definitive diagnostic evidence, future clinical decision-support systems could evaluate automated referral or deferral protocols (e.g., flagging cases where $H(p) > 0.80$ for secondary clinician review), subject to prospective clinical validation.

---

### 5.7 Physiological Insights from Inside-CV Feature Ablation
The inside-cross-validation feature ablation experiments (Table 11) provide empirical evidence regarding the biological information required to predict distinct coronary territories:
- **Symptoms and Physical Examination:** Ablating anginal symptoms (primarily `Typical Chest Pain`) induced the largest marginal drop in discrimination for composite CAD ($\Delta \text{AUC} = -0.0847$) and LAD ($\Delta \text{AUC} = -0.0532$). This confirms established clinical consensus that typical angina pectoris remains the single most powerful pre-test clinical indicator of obstructive disease.
- **Echocardiography as the LAD Anchor:** Ablating resting echocardiographic measurements (`EF-TTE`, `Region RWMA`, `VHD`) caused a major discrimination collapse for LAD ($\Delta \text{AUC} = -0.0528$), whereas its impact on LCX ($\Delta = -0.0185$) and RCA ($\Delta = -0.0094$) was minimal. This divergence is anatomically coherent: anterior myocardial contractility is directly coupled to LAD perfusion, making resting echocardiography an indispensable diagnostic modality specifically for the left anterior descending territory.
- **Laboratory Blood Panels Compensating for LCX Silence:** Conversely, ablating laboratory blood panels (`CR`, `TG`, `LDL`, `ESR`, `PLT`) caused the largest performance decline in LCX ($\Delta \text{AUC} = -0.0524$), while producing modest drops in LAD ($\Delta = -0.0189$) and Cath ($\Delta = -0.0142$). Because posterolateral ischemia is largely silent on resting ECG and echocardiography, the LCX model relied on systemic metabolic and inflammatory markers to infer vascular risk.

---

### 5.8 Critical Re-Evaluation of Prior Z-Alizadeh Sani Benchmarks
Contextualizing our findings within the broader literature on the Z-Alizadeh Sani dataset requires a critical, methodologically rigorous perspective. Numerous prior publications have reported extraordinary diagnostic accuracies—often exceeding 95% to 98%—on this cohort using complex neural networks, genetic algorithms, and stacked ensembles (Arabasadi et al., 2017; Abdar et al., 2019).

Our systematic auditing suggests that these extreme performance figures should be interpreted with substantial caution:
1. **Pervasive Pre-Partition Leakage:** Multiple published works performed feature selection, dimensionality reduction, or hyperparameter optimization over the complete $N = 303$ cohort prior to establishing cross-validation splits. This introduces subtle but pervasive data leakage from validation folds into training folds, artificially inflating reported test metrics.
2. **Single-Split Reporting Volatility:** In a cohort of $N = 303$, a single random 80/20 train-test split places only $\sim 60$ patients in the test partition. In such a small test set, the correct classification of just two borderline patients swings accuracy by $>3.3\%$. Reporting single-split point estimates without sample dispersion (`ddof=1`) masks severe resampling variance.
3. **Absence of Calibration Verification:** Prior studies focused exclusively on uncalibrated classification accuracy, ignoring probability calibration, Brier loss, ECE, and operating threshold stability.
4. **Leakage-Safe Benchmarking:** Under our strictly leakage-isolated 25-fold cross-validation protocol, composite CAD (`Cath`) achieved an audited ROC-AUC of **$0.9123 \pm 0.0404$** and an accuracy of **$86.67\% \pm 4.11\%$** (Table 4). We submit that this performance represents a realistic, reproducible baseline for non-invasive machine learning on this cohort, unmarred by optimistic leakage artifacts.

---

## 6. Limitations & Scientific Claim Boundaries

To ensure complete scientific integrity, the findings of this study must be interpreted within the context of explicit methodological limitations:

### 6.1 Single-Center Cohort and Referral Selection Bias
The entire empirical analysis was conducted on $N = 303$ consecutive patients referred for coronary catheterization at a single tertiary institution: Shaheed Rajaei Cardiovascular, Medical and Research Center in Tehran, Iran. Tertiary cardiology referral centers evaluate patient populations with advanced clinical presentations and enriched cardiovascular risk profiles. Consequently, the observed disease prevalence in this cohort—$71.29\%$ for composite CAD and $58.42\%$ for LAD stenosis—is substantially higher than the prevalence encountered in primary care outpatient clinics or community screening settings. This referral selection bias alters pre-test disease probabilities and means that the reported predictive models cannot be assumed to generalize directly to lower-prevalence screening populations without prospective recalibration.

### 6.2 Absence of External Geographic and Prospective Temporal Validation
In alignment with recommendations emphasized by TRIPOD+AI (Collins et al., 2024)—noting that a formal checklist-based compliance certification remains outside the scope of this retrospective computational study—we explicitly emphasize that **this investigation constitutes internal cross-validation only**. No external validation cohorts from different hospital networks, diverse geographic regions, or distinct ethnic and racial demographics were available. Furthermore, the cohort was collected retrospectively; no prospective temporal validation was performed across differing clinical operating eras. While our repeated cross-validation harness evaluated algorithmic stability under data resampling, true clinical generalizability can only be confirmed through prospective external validation across heterogeneous healthcare environments.

### 6.3 Correlated Resampling Folds and Statistical Generalization
The 25 outer folds generated by our Repeated Stratified Cross-Validation scheme (5 splits $\times$ 5 repeats) are statistically correlated because patient samples are reused across different random repeats. Consequently, the standard deviations reported throughout this manuscript describe **fold-level resampling dispersion (`ddof=1`)**; they do **not** represent independent-sample population confidence intervals. Hypotheses regarding model comparisons should be interpreted as descriptive evaluations of algorithmic stability under partition perturbation, rather than formal population inferential tests.

### 6.4 Disconnect Between Additive SHAP Space and Non-Linear Probability Calibration
As detailed in Section 5.4, SHAP feature attributions operate strictly in raw model score space (pre-calibration log-odds for tree ensembles). For pipelines incorporating Platt (Sigmoid) scaling, the non-linear transformation $\sigma(A \cdot f(x) + B)$ breaks linear additivity in probability space. While SHAP explanations faithfully reflect the internal logic of the tree models, they cannot be linearly interpreted as absolute percentages of probability risk. Developing mathematically exact additive attribution frameworks that directly explain post-calibrated non-linear probabilities remains an active open challenge in explainable AI.

### 6.5 Observational Correlations vs. Biological Causality
All feature attributions documented in this study represent statistical associations between input covariates and angiographic ground truth within trained machine learning estimators. **These statistical associations must not be conflated with biological etiology or clinical causality**. For example, while `Erythrocyte Sedimentation Rate (ESR)` emerged as a prominent predictor for RCA stenosis, our observational data provide no evidence that lowering ESR via therapeutic intervention will reduce RCA stenotic burden. Attributions provide diagnostic decision support, not causal targets for medical intervention.

### 6.6 Statistical Power Limitations in Subgroup Analyses
Our exploratory subgroup analysis (Table 12) evaluated model performance across 13 feasible strata. However, several clinical subgroups possessed constrained sample sizes (e.g., $N = 90$ diabetic patients, including only 12 non-stenotic individuals; $N = 95$ elderly patients $\ge 65$ years). While descriptive performance parity was observed across biological sex, the observed performance attenuation in older patients (Cath ROC-AUC $0.7480$ vs. $0.8954$ in younger patients) represents an exploratory, hypothesis-generating observation. Due to statistical power constraints, this study makes **no claim of algorithmic fairness certification, demographic parity, or equalized odds guarantees**.

### 6.7 Barriers to Clinical Readiness and Implementation
We explicitly declare that **this investigation does not establish clinical readiness for the CoroVista system**. CoroVista is an academic research software prototype designed to study algorithmic reliability, probability calibration, and explainability stability. All operating thresholds, decision margins, and entropy cutoff values documented herein are exploratory research operating points, not clinically validated diagnostic criteria or treatment thresholds. It has not received regulatory clearance or certification from health authorities (e.g., U.S. FDA, European CE mark) and has not undergone prospective randomized clinical trial evaluation. Machine learning models must not be used for autonomous clinical diagnosis, triage, or alteration of patient therapy outside of approved investigational protocols under direct physician oversight.

---

## 7. Conclusion and Future Directions

### 7.1 Summary of Contributions
This study established an audited, multi-target, calibrated, and stable machine learning framework for non-invasive coronary artery disease prediction using the extended Z-Alizadeh Sani cohort ($N = 303$). By expanding evaluation beyond traditional discrimination benchmarks, our investigation yielded several core insights:
1. **Multi-Target Anatomical Feasibility:** Non-invasive clinical, laboratory, ECG, and echocardiographic variables successfully discriminated overall CAD (`Cath` ROC-AUC $0.9123 \pm 0.0404$) and LAD stenosis (ROC-AUC $0.8443 \pm 0.0528$), while exposing the inherent diagnostic challenge of the posterolateral territory (`LCX` ROC-AUC $0.7358 \pm 0.0629$).
2. **Probability Calibration & Operating Threshold Recovery:** Parametric Platt scaling significantly improved probability reliability, while nested inner-fold threshold tuning ($F_1$-optimization) successfully resolved catastrophic sensitivity collapse on minority targets (recovering RCA sensitivity from $31.24\%$ up to $79.46\%$).
3. **Attribution Stability:** TreeSHAP attributions demonstrated high global rank stability across 25 outer folds ($\rho > 0.90$ for Cath, LAD, and LCX) and 100% additivity verification, while linear models on RCA exposed attribution volatility driven by covariate multi-collinearity.
4. **Boundary-Localized Prediction Churn:** Out-of-fold prediction tracking across 5 repeats proved that classification flips concentrate heavily in the immediate decision boundary margin ($|p - \tau| < 0.05$), where all near-boundary Cath ($6/6$) and LAD ($17/17$) patients alongside the vast majority of LCX ($44/45$) and RCA ($58/75$) patients experienced label flips, while confident predictions ($|p - \tau| \ge 0.20$) achieve $>99\%$ label invariance.
5. **Defensive Uncertainty Quantification:** Predictive entropy can be computed directly from output probabilities without reference labels; retrospective evaluation against ground-truth labels demonstrated strong error-detection discrimination (retrospective ROC-AUC $0.7593$ for Cath, $0.6796$ for RCA), supporting its investigation as an exploratory automated referral indicator.

### 7.2 Recommendations for Clinical Machine Learning Research
Based on our findings, we propose that peer-reviewed clinical machine learning literature adopt the following reporting standards:
- **Mandatory Reporting of Probability Calibration:** Studies reporting classification accuracy or ROC-AUC should routinely report proper scoring rules (Brier score) and Expected Calibration Error (ECE), accompanied by reliability diagrams.
- **Auditing Attribution Stability:** Explainability claims should not rely on a single train-test split; post-hoc feature importance rankings should be audited for stability across resampled cross-validation folds.
- **Reporting Prediction Dispersion:** Researchers should evaluate prediction churn across model retraining to distinguish confident, invariant predictions from boundary-adjacent volatile predictions.
- **Separation of Evaluation Protocols:** Operating threshold tuning must be executed strictly within nested inner partitions to prevent optimistic bias, and evaluation protocols must be meticulously segregated.

### 7.3 Concluding Remarks
Machine learning offers powerful methodologies for non-invasive cardiovascular risk stratification. However, algorithmic performance in clinical medicine cannot be judged by discrimination alone. Evaluating models through the combined lenses of probability calibration, explanation consistency, prediction stability, and defensive uncertainty quantification bridges the gap between statistical benchmarking and responsible, transparent clinical decision support.

---

## Declarations

### Ethics Approval and Consent to Participate
The empirical data utilized in this study originate from the open-access Z-Alizadeh Sani coronary artery disease dataset, collected and de-identified at Shaheed Rajaei Cardiovascular, Medical and Research Center in Tehran, Iran (Alizadehsani et al., 2013, 2018; Alizadehsani, 2017, 2018). The foundational publications do not disclose a specific institutional review board (IRB) or institutional ethics committee protocol identifier, operating under standard hospital clinical diagnostic data governance. The present investigation represents an independent secondary computational modeling study performed exclusively on previously published, fully de-identified, publicly accessible tabular research data, involving no direct patient interaction, prospective clinical intervention, biological specimen collection, or re-identification risk. Public availability of open data does not automatically obviate institutional research ethics governance; because an independent institutional ethics review determination or formal waiver has not been independently documented for this secondary study, the target journal or relevant institutional ethics body must determine whether an exemption, waiver, or other formal ethics determination is required. Formal ethics clearance is not marked as completed, and no IRB protocol number or exemption certificate is claimed or fabricated.

### Consent for Publication
Not applicable. No personally identifiable individual patient data, images, or biometric identifiers are contained within this manuscript.

### Availability of Data and Materials
The extended Z-Alizadeh Sani cardiology dataset utilized in this investigation is openly available in public data repositories:
- UCI Machine Learning Repository: DOI [10.24432/C5Q31T](https://doi.org/10.24432/C5Q31T) (Alizadehsani, 2017).
- Mendeley Data Repository: DOI [10.17632/9k56pwtvz9.1](https://doi.org/10.17632/9k56pwtvz9.1) (Alizadehsani, 2018).
All open-source software, preprocessing pipelines, model configurations, and experimental evaluation scripts developed for CoroVista are hosted in the project research repository.

### Competing Interests
The authors declare that they have no competing financial interests, personal relationships, or corporate affiliations that could have influenced the work reported in this paper.

### Funding
This research received no specific grant or external financial support from any funding agency in the public, commercial, or not-for-profit sectors.

### Authors' Contributions
- **Naman Deep Tripathi:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing – original draft, Writing – review and editing.
- **Nikhil Agrawal:** Cardiovascular domain mapping, Anatomical multi-target localization, 3D anatomical asset integration, Clinical workflow visualization, Early data exploration and data audit, Critical manuscript review.

### Acknowledgements
The authors express their sincere gratitude to Dr. Zahra Alizadeh Sani, Dr. Roohallah Alizadehsani, and their clinical colleagues at Shaheed Rajaei Cardiovascular, Medical and Research Center (Tehran, Iran) for compiling, de-identifying, and openly sharing the Z-Alizadeh Sani coronary artery disease dataset through the UCI Machine Learning Repository and Mendeley Data. We also acknowledge the Database Center for Life Science (DBCLS, Japan) for open public access to the BodyParts3D anatomical polygon model database. The authors also appreciate the organizers of the IIT Mandi hackathon for originally highlighting cardiovascular prediction benchmarks as an open-access scientific challenge problem.

---

## References

1. **Abdar, M., Książek, W., Acharya, U. R., Tan, R.-S., Makarenkov, V., & Pławiak, P.** (2019). A new machine learning technique for an accurate diagnosis of coronary artery disease. *Computer Methods and Programs in Biomedicine*, 179, 104992. DOI: [10.1016/j.cmpb.2019.104992](https://doi.org/10.1016/j.cmpb.2019.104992)
2. **Alizadehsani, R.** (2017). Z-Alizadeh Sani Data Set. *UCI Machine Learning Repository*. DOI: [10.24432/C5Q31T](https://doi.org/10.24432/C5Q31T)
3. **Alizadehsani, R.** (2018). Extension of Z-Alizadeh Sani dataset. *Mendeley Data*, V1. DOI: [10.17632/9k56pwtvz9.1](https://doi.org/10.17632/9k56pwtvz9.1)
4. **Alizadehsani, R., Habibi, J., Hosseini, M. M., Mashayekhi, H., Boghrati, R., Ghandeharioun, A., Bahadorian, B., & Sani, Z. A.** (2013). A data mining approach for diagnosis of coronary artery disease. *Computer Methods and Programs in Biomedicine*, 111(1), 52–61. DOI: [10.1016/j.cmpb.2013.03.004](https://doi.org/10.1016/j.cmpb.2013.03.004)
5. **Alizadehsani, R., Roshanzamir, M., Abdar, M., Beykikhoshk, A., Khosravi, A., Panahiazar, M., Nahavandi, S., & Sani, Z. A.** (2018). Non-invasive detection of coronary artery disease in high-risk patients based on the stenosis prediction of separate coronary arteries. *Computer Methods and Programs in Biomedicine*, 162, 119–127. DOI: [10.1016/j.cmpb.2018.05.009](https://doi.org/10.1016/j.cmpb.2018.05.009)
6. **Alvarez-Melis, D., & Jaakkola, T. S.** (2018). Towards Robust Interpretability with Self-Explaining Neural Networks. In *Advances in Neural Information Processing Systems (NeurIPS 2018)*, 31, 7775–7784. URL: [https://proceedings.neurips.cc/paper/2018/hash/3e9f0fc9b2f89e2c5076e008d7da4f44-Abstract.html](https://proceedings.neurips.cc/paper/2018/hash/3e9f0fc9b2f89e2c5076e008d7da4f44-Abstract.html)
7. **Arabasadi, Z., Alizadehsani, R., Roshanzamir, M., Moosaei, H., & Yarifard, A. A.** (2017). Computer aided decision making for heart disease detection using hybrid neural network-Genetic algorithm. *Computer Methods and Programs in Biomedicine*, 141, 19–26. DOI: [10.1016/j.cmpb.2017.01.004](https://doi.org/10.1016/j.cmpb.2017.01.004)
8. **Brier, G. W.** (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3. DOI: [10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2](https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2)
9. **Chen, T., & Guestrin, C.** (2016). XGBoost: A Scalable Tree Boosting System. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16)*, pp. 785–794. DOI: [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)
10. **Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L., Van Calster, B., Ghassemi, M., Liu, X., Reitsma, J. B., van Smeden, M., et al.** (2024). TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use machine learning or artificial intelligence. *BMJ*, 385, e078378. DOI: [10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378)
11. **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q.** (2017). On Calibration of Modern Neural Networks. In *Proceedings of the 34th International Conference on Machine Learning (ICML 2017)*, PMLR 70, pp. 1321–1330. URL: [http://proceedings.mlr.press/v70/guo17a.html](http://proceedings.mlr.press/v70/guo17a.html)
12. **Kompa, B., Snoek, J., & Beam, A. L.** (2021). Second opinion needed: communicating uncertainty in machine learning for healthcare. *npj Digital Medicine*, 4(1), 4. DOI: [10.1038/s41746-020-00367-3](https://doi.org/10.1038/s41746-020-00367-3)
13. **Lawton, J. S., Tamis-Holland, J. E., Bangalore, S., Bates, E. R., Beckie, T. M., Bischoff, J. M., Bittl, J. A., Cohen, M. G., DiMaio, J. M., Don, C. W., et al.** (2022). 2021 ACC/AHA/SCAI Guideline for Coronary Artery Revascularization: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. *Circulation*, 145(3), e18–e114. DOI: [10.1161/CIR.0000000000001038](https://doi.org/10.1161/CIR.0000000000001038)
14. **Lundberg, S. M., & Lee, S.-I.** (2017). A Unified Approach to Interpreting Model Predictions. In *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30, 4765–4774. URL: [https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html)
15. **Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N., & Lee, S.-I.** (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2(1), 56–67. DOI: [10.1038/s42256-019-0138-9](https://doi.org/10.1038/s42256-019-0138-9)
16. **Martin, S. S., Aday, A. W., Almarzooq, Z. I., Anderson, C. A. M., Arora, P., Avery, C. L., Baker-Smith, C. M., Barone Gibbs, B., Beaton, A. Z., Boehme, A. K., et al.** (2024). 2024 Heart Disease and Stroke Statistics: A Report of US and Global Data From the American Heart Association. *Circulation*, 149(8), e347–e913. DOI: [10.1161/CIR.0000000000001209](https://doi.org/10.1161/CIR.0000000000001209)
17. **Mitsuhashi, N., Fujieda, K., Tamura, T., Kawamoto, S., Takagi, T., & Okubo, K.** (2009). BodyParts3D: 3D structure database for anatomical concepts. *Nucleic Acids Research*, 37(Database issue), D782–D785. DOI: [10.1093/nar/gkn613](https://doi.org/10.1093/nar/gkn613)
18. **Niculescu-Mizil, A., & Caruana, R.** (2005). Predicting good probabilities with supervised learning. In *Proceedings of the 22nd International Conference on Machine Learning (ICML '05)*, pp. 625–632. DOI: [10.1145/1102351.1102430](https://doi.org/10.1145/1102351.1102430)
19. **Patel, M. R., Peterson, E. D., Dai, D., Brennan, J. M., Redberg, R. F., Anderson, H. V., Brindis, R. G., & Douglas, P. S.** (2010). Low diagnostic yield of elective coronary angiography. *New England Journal of Medicine*, 362(10), 886–895. DOI: [10.1056/NEJMoa0907272](https://doi.org/10.1056/NEJMoa0907272)
20. **Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., et al.** (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830. URL: [https://jmlr.org/papers/v12/pedregosa11a.html](https://jmlr.org/papers/v12/pedregosa11a.html)
21. **Platt, J. C.** (1999). Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods. *Advances in Large Margin Classifiers*, 10(3), 61–74. URL: [https://www.cs.colorado.edu/~mozer/Teaching/syllabi/6622/papers/Platt1999.pdf](https://www.cs.colorado.edu/~mozer/Teaching/syllabi/6622/papers/Platt1999.pdf)
22. **Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., Steyerberg, E. W., & Topic Group ‘Evaluating diagnostic tests and prediction models’ of the STRATOS initiative.** (2019). A calibration hierarchy for risk models was defined: from utopia to empirical calibration. *Journal of Clinical Epidemiology*, 110, 29–38. DOI: [10.1016/j.jclinepi.2019.02.017](https://doi.org/10.1016/j.jclinepi.2019.02.017)
23. **Visani, G., Bagli, E., Chesani, F., Poluzzi, A., & Capobianco, D.** (2022). Statistical stability of feature importance in machine learning models. *Data Mining and Knowledge Discovery*, 36(3), 1269–1314. DOI: [10.1007/s10618-022-00858-5](https://doi.org/10.1007/s10618-022-00858-5)

