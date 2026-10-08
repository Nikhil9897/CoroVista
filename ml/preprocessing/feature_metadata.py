"""
CoroVista - Clinical Feature Metadata Registry
Stage 2: Machine Learning Pipeline Foundation

This module defines the canonical clinical metadata registry for the CoroVista
cardiovascular risk prediction system. It bridges the observed dataset schema
with official source clinical definitions, documenting:
- Clinical domain categories
- Dataset column names vs source definitions
- Expected data types and value ranges
- Known data quality issues (e.g., 'Fmale' typo, 'MBI' wording anomaly)
- Preprocessing strategies and model eligibility
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

# Ground truth target columns - strictly excluded from feature matrix X
TARGET_COLUMNS: List[str] = ["Cath", "LAD", "LCX", "RCA"]

# Feature with variance = 0 in dataset
ZERO_VARIANCE_COLUMNS: List[str] = ["Exertional CP"]

# 54 Eligible features in the active dataset
ELIGIBLE_FEATURES: List[str] = [
    # Demographic / Anthropometric (5)
    "Age", "Weight", "Length", "Sex", "BMI",
    # Clinical History / Habits (12)
    "DM", "HTN", "Current Smoker", "EX-Smoker", "FH", "Obesity", "CRF", "CVA",
    "Airway disease", "Thyroid Disease", "CHF", "DLP",
    # Physical Exam & Symptoms (13)
    "BP", "PR", "Edema", "Weak Peripheral Pulse", "Lung rales", "Systolic Murmur",
    "Diastolic Murmur", "Typical Chest Pain", "Dyspnea", "Function Class",
    "Atypical", "Nonanginal", "LowTH Ang",
    # 12-Lead ECG (7)
    "Q Wave", "St Elevation", "St Depression", "Tinversion", "LVH", "Poor R Progression", "BBB",
    # Laboratory (14)
    "FBS", "CR", "TG", "LDL", "HDL", "BUN", "ESR", "HB", "K", "Na", "WBC", "Lymph", "Neut", "PLT",
    # Echocardiography (3)
    "EF-TTE", "Region RWMA", "VHD"
]

@dataclass
class FeatureMetadata:
    name: str
    clinical_category: str
    data_type: str
    source_description: str
    observed_range_or_values: str
    stated_source_values: str
    preprocessing_strategy: str
    model_eligibility: str  # "Eligible", "Excluded (Target)", "Excluded (Zero Variance)"
    known_data_quality_issue: Optional[str] = None
    clinical_notes: Optional[str] = None


FEATURE_REGISTRY: Dict[str, FeatureMetadata] = {
    # ------------------ TARGETS ------------------
    "Cath": FeatureMetadata(
        name="Cath",
        clinical_category="Target",
        data_type="object",
        source_description="Cardiac catheterization outcome: overall coronary artery disease (CAD)",
        observed_range_or_values="CAD (216), Normal (87)",
        stated_source_values="CAD, Normal",
        preprocessing_strategy="Target extraction (binary encode CAD=1, Normal=0). MUST NEVER enter X.",
        model_eligibility="Excluded (Target)",
        known_data_quality_issue="Row index 93 mismatch (Cath=Normal while LAD=Stenotic). Preserved as raw observation.",
        clinical_notes="Gold-standard invasive coronary angiography diagnosis. 99.67% concordant with (LAD|LCX|RCA==Stenotic)."
    ),
    "LAD": FeatureMetadata(
        name="LAD",
        clinical_category="Target",
        data_type="object",
        source_description="Left Anterior Descending coronary artery stenosis (>=50% luminal narrowing)",
        observed_range_or_values="Stenotic (177), Normal (126)",
        stated_source_values="Stenotic, Normal",
        preprocessing_strategy="Target extraction (binary encode Stenotic=1, Normal=0). MUST NEVER enter X.",
        model_eligibility="Excluded (Target)",
        known_data_quality_issue="None",
        clinical_notes="Supplies ~50% of left ventricular myocardium (anterior wall, septum, apex)."
    ),
    "LCX": FeatureMetadata(
        name="LCX",
        clinical_category="Target",
        data_type="object",
        source_description="Left Circumflex coronary artery stenosis (>=50% luminal narrowing)",
        observed_range_or_values="Normal (184), Stenotic (119)",
        stated_source_values="Stenotic, Normal",
        preprocessing_strategy="Target extraction (binary encode Stenotic=1, Normal=0). MUST NEVER enter X.",
        model_eligibility="Excluded (Target)",
        known_data_quality_issue="None",
        clinical_notes="Supplies lateral and posterior LV myocardium."
    ),
    "RCA": FeatureMetadata(
        name="RCA",
        clinical_category="Target",
        data_type="object",
        source_description="Right Coronary Artery stenosis (>=50% luminal narrowing)",
        observed_range_or_values="Normal (189), Stenotic (114)",
        stated_source_values="Stenotic, Normal",
        preprocessing_strategy="Target extraction (binary encode Stenotic=1, Normal=0). MUST NEVER enter X.",
        model_eligibility="Excluded (Target)",
        known_data_quality_issue="None",
        clinical_notes="Supplies right ventricle, inferior LV wall, and AV/SA nodes in right-dominant circulation."
    ),

    # ------------------ DEMOGRAPHIC ------------------
    "Age": FeatureMetadata(
        name="Age",
        clinical_category="Demographic",
        data_type="int64",
        source_description="Patient age in years",
        observed_range_or_values="30 to 86 (mean 58.9)",
        stated_source_values="30–86",
        preprocessing_strategy="Numerical pass-through; RobustScaler/StandardScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Established primary cardiovascular risk factor."
    ),
    "Weight": FeatureMetadata(
        name="Weight",
        clinical_category="Demographic",
        data_type="int64",
        source_description="Body weight in kilograms (kg)",
        observed_range_or_values="48 to 120 (median 74)",
        stated_source_values="48–120",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Subject to multicollinearity with BMI and Length."
    ),
    "Length": FeatureMetadata(
        name="Length",
        clinical_category="Demographic",
        data_type="int64",
        source_description="Standing height / body length in centimeters (cm)",
        observed_range_or_values="140 to 188 (median 165)",
        stated_source_values="140–188",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Used with weight to compute BMI."
    ),
    "Sex": FeatureMetadata(
        name="Sex",
        clinical_category="Demographic",
        data_type="object",
        source_description="Biological sex",
        observed_range_or_values="Male (176), Fmale (127)",
        stated_source_values="Male, female",
        preprocessing_strategy="Normalize 'Fmale' -> 'Female'; binary encode Male=1, Female=0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Typo in raw data ('Fmale'). Must be normalized deterministically.",
        clinical_notes="Males have earlier onset and higher initial prevalence of obstructive CAD."
    ),
    "BMI": FeatureMetadata(
        name="BMI",
        clinical_category="Demographic",
        data_type="float64",
        source_description="Body Mass Index (kg/m^2)",
        observed_range_or_values="18.1 to 40.9 (median 26.8)",
        stated_source_values="18–41",
        preprocessing_strategy="Numerical pass-through; evaluate multicollinearity ablation vs Weight/Length.",
        model_eligibility="Eligible",
        known_data_quality_issue="Deterministically derived from Weight and Length.",
        clinical_notes="Overweight/obesity is correlated with dyslipidemia and metabolic syndrome."
    ),

    # ------------------ CLINICAL HISTORY ------------------
    "DM": FeatureMetadata(
        name="DM",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Diabetes Mellitus history",
        observed_range_or_values="0 (213), 1 (90)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Major risk factor for multi-vessel and diffuse coronary disease."
    ),
    "HTN": FeatureMetadata(
        name="HTN",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Hypertension history (blood pressure >= 140/90 or on antihypertensives)",
        observed_range_or_values="1 (179), 0 (124)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="High prevalence in CAD cohorts."
    ),
    "Current Smoker": FeatureMetadata(
        name="Current Smoker",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Current tobacco smoker",
        observed_range_or_values="0 (240), 1 (63)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Major pro-thrombotic and endothelial dysfunction risk factor."
    ),
    "EX-Smoker": FeatureMetadata(
        name="EX-Smoker",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Former tobacco smoker",
        observed_range_or_values="0 (293), 1 (10)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (96.7% zero).",
        clinical_notes="Low positive prevalence (10 patients)."
    ),
    "FH": FeatureMetadata(
        name="FH",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Family History of premature coronary artery disease",
        observed_range_or_values="0 (255), 1 (48)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="First-degree relative CAD onset before age 55 (male) or 65 (female)."
    ),
    "Obesity": FeatureMetadata(
        name="Obesity",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Clinical obesity indicator",
        observed_range_or_values="'Y' (211), 'N' (92)",
        stated_source_values="Yes if MBI > 25, no otherwise",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Source documentation typo: 'MBI > 25' instead of 'BMI > 25'. Preserved as noted.",
        clinical_notes="Note: World Health Organization defines BMI 25-29.9 as overweight and >=30 as obesity; source dataset uses threshold 25."
    ),
    "CRF": FeatureMetadata(
        name="CRF",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Chronic Renal Failure history",
        observed_range_or_values="'N' (297), 'Y' (6)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (98.0% negative).",
        clinical_notes="Accelerates vascular calcification; low prevalence in dataset."
    ),
    "CVA": FeatureMetadata(
        name="CVA",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Cerebrovascular Accident (stroke/TIA) history",
        observed_range_or_values="'N' (298), 'Y' (5)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (98.3% negative).",
        clinical_notes="Polyvascular disease indicator."
    ),
    "Airway disease": FeatureMetadata(
        name="Airway disease",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Chronic airway disease (COPD / Asthma) history",
        observed_range_or_values="'N' (292), 'Y' (11)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (96.4% negative).",
        clinical_notes="Relevant for differential diagnosis of dyspnea."
    ),
    "Thyroid Disease": FeatureMetadata(
        name="Thyroid Disease",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Thyroid pathology history (hypo/hyperthyroidism)",
        observed_range_or_values="'N' (296), 'Y' (7)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (97.7% negative).",
        clinical_notes="Thyroid dysfunction impacts lipid metabolism and cardiovascular hemodynamics."
    ),
    "CHF": FeatureMetadata(
        name="CHF",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Congestive Heart Failure history",
        observed_range_or_values="'N' (302), 'Y' (1)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Extreme rarity: only 1 positive case (99.67% negative). High split instability.",
        clinical_notes="Retained in schema for simulator compatibility; requires tree regularizers."
    ),
    "DLP": FeatureMetadata(
        name="DLP",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Dyslipidemia history",
        observed_range_or_values="'N' (191), 'Y' (112)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Abnormal blood lipid profile; major atherogenic driver."
    ),

    # ------------------ PHYSICAL EXAM & SYMPTOMS ------------------
    "BP": FeatureMetadata(
        name="BP",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Systolic Blood Pressure (mmHg)",
        observed_range_or_values="90 to 190 (median 130)",
        stated_source_values="90–190 mmHg",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Resting systolic pressure measured in clinic."
    ),
    "PR": FeatureMetadata(
        name="PR",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Pulse Rate (beats per minute / ppm)",
        observed_range_or_values="50 to 110 (median 70)",
        stated_source_values="50–110 ppm",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Resting heart rate in beats per minute."
    ),
    "Edema": FeatureMetadata(
        name="Edema",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Peripheral edema on physical exam",
        observed_range_or_values="0 (291), 1 (12)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (96.0% zero).",
        clinical_notes="Sign of volume overload or heart failure."
    ),
    "Weak Peripheral Pulse": FeatureMetadata(
        name="Weak Peripheral Pulse",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Diminished peripheral arterial pulsation (radial/pedal)",
        observed_range_or_values="'N' (298), 'Y' (5)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (98.3% negative).",
        clinical_notes="Sign of peripheral vascular disease or poor systemic perfusion."
    ),
    "Lung rales": FeatureMetadata(
        name="Lung rales",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Auscultated pulmonary crackles / rales",
        observed_range_or_values="'N' (292), 'Y' (11)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (96.4% negative).",
        clinical_notes="Indicator of pulmonary venous congestion."
    ),
    "Systolic Murmur": FeatureMetadata(
        name="Systolic Murmur",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Cardiac systolic murmur on auscultation",
        observed_range_or_values="'N' (262), 'Y' (41)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Common with aortic stenosis or mitral regurgitation."
    ),
    "Diastolic Murmur": FeatureMetadata(
        name="Diastolic Murmur",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Cardiac diastolic murmur on auscultation",
        observed_range_or_values="'N' (294), 'Y' (9)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (97.0% negative).",
        clinical_notes="Aortic regurgitation or mitral stenosis; low prevalence."
    ),
    "Typical Chest Pain": FeatureMetadata(
        name="Typical Chest Pain",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="Classic anginal chest pain (substernal, exertional, relieved by rest/nitro)",
        observed_range_or_values="1 (164), 0 (139)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Highest single linear correlation with CAD (r=0.54) and LAD (r=0.46)."
    ),
    "Dyspnea": FeatureMetadata(
        name="Dyspnea",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Shortness of breath on exertion or rest",
        observed_range_or_values="'N' (169), 'Y' (134)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Anginal equivalent symptom."
    ),
    "Function Class": FeatureMetadata(
        name="Function Class",
        clinical_category="Clinical Examination",
        data_type="int64",
        source_description="New York Heart Association (NYHA) functional capacity class",
        observed_range_or_values="0 (170), 1 (7), 2 (91), 3 (35)",
        stated_source_values="1, 2, 3, 4",
        preprocessing_strategy="Ordinal integer scale (0, 1, 2, 3).",
        model_eligibility="Eligible",
        known_data_quality_issue="Dataset uses 0-3 encoding instead of 1-4 standard (0 indicates asymptomatic/no functional limitation).",
        clinical_notes="Reflects symptom severity relative to physical activity."
    ),
    "Atypical": FeatureMetadata(
        name="Atypical",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Atypical chest pain (meets 2 of 3 classical angina criteria)",
        observed_range_or_values="'N' (210), 'Y' (93)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Negatively correlated with obstructive CAD (r=-0.42)."
    ),
    "Nonanginal": FeatureMetadata(
        name="Nonanginal",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Nonanginal chest pain (meets <=1 classical angina criterion)",
        observed_range_or_values="'N' (287), 'Y' (16)",
        stated_source_values="Yes, no (labeled 'Nonanginal CP' in source text)",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (94.7% negative).",
        clinical_notes="Negatively correlated with CAD."
    ),
    "Exertional CP": FeatureMetadata(
        name="Exertional CP",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Chest pain provoked strictly by physical exertion",
        observed_range_or_values="'N' (303)",
        stated_source_values="Yes, no",
        preprocessing_strategy="ZERO VARIANCE. Strictly dropped from feature matrix X.",
        model_eligibility="Excluded (Zero Variance)",
        known_data_quality_issue="100% constant ('N' for all 303 samples). Contains zero discriminatory signal.",
        clinical_notes="Preserved in metadata registry and raw data for provenance; dropped inside pipeline."
    ),
    "LowTH Ang": FeatureMetadata(
        name="LowTH Ang",
        clinical_category="Clinical Examination",
        data_type="object",
        source_description="Low Threshold Angina (angina with minimal exertion)",
        observed_range_or_values="'N' (301), 'Y' (2)",
        stated_source_values="Yes, no (labeled 'Low Th Ang' in source text)",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Extreme rarity: only 2 positive cases (99.34% negative).",
        clinical_notes="Severe symptom threshold; low prevalence."
    ),

    # ------------------ 12-LEAD ECG ------------------
    "Q Wave": FeatureMetadata(
        name="Q Wave",
        clinical_category="ECG",
        data_type="int64",
        source_description="Pathological Q waves on resting ECG",
        observed_range_or_values="0 (287), 1 (16)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Hallmark of previous transmural myocardial infarction."
    ),
    "St Elevation": FeatureMetadata(
        name="St Elevation",
        clinical_category="ECG",
        data_type="int64",
        source_description="ST-segment elevation on resting ECG",
        observed_range_or_values="0 (289), 1 (14)",
        stated_source_values="Yes, no (labeled 'ST Elevation' in source text)",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (95.4% negative).",
        clinical_notes="Indicator of acute or subacute transmural ischemia / ventricular aneurysm."
    ),
    "St Depression": FeatureMetadata(
        name="St Depression",
        clinical_category="ECG",
        data_type="int64",
        source_description="ST-segment depression on resting ECG (>= 0.5 mm)",
        observed_range_or_values="0 (232), 1 (71)",
        stated_source_values="Yes, no (labeled 'ST Depression' in source text)",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Indicator of subendocardial myocardial ischemia."
    ),
    "Tinversion": FeatureMetadata(
        name="Tinversion",
        clinical_category="ECG",
        data_type="int64",
        source_description="T-wave inversion on resting ECG",
        observed_range_or_values="0 (213), 1 (90)",
        stated_source_values="Yes, no (labeled 'T inversion' in source text)",
        preprocessing_strategy="Binary indicator (already 0/1 integer).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Correlates with LAD stenosis (r=0.21)."
    ),
    "LVH": FeatureMetadata(
        name="LVH",
        clinical_category="ECG",
        data_type="object",
        source_description="Left Ventricular Hypertrophy voltage criteria on ECG (e.g., Sokolow-Lyon)",
        observed_range_or_values="'N' (283), 'Y' (20)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (93.4% negative).",
        clinical_notes="Chronic consequence of longstanding hypertension or aortic stenosis."
    ),
    "Poor R Progression": FeatureMetadata(
        name="Poor R Progression",
        clinical_category="ECG",
        data_type="object",
        source_description="Poor R wave progression across precordial leads (V1-V3)",
        observed_range_or_values="'N' (294), 'Y' (9)",
        stated_source_values="Yes, no",
        preprocessing_strategy="Map 'Y'->1, 'N'->0.",
        model_eligibility="Eligible",
        known_data_quality_issue="Near-constant (97.0% negative).",
        clinical_notes="Associated with anteroseptal myocardial infarction or conduction delay."
    ),
    "BBB": FeatureMetadata(
        name="BBB",
        clinical_category="ECG",
        data_type="object",
        source_description="Bundle Branch Block (Left, Right, or None)",
        observed_range_or_values="'N' (282), 'LBBB' (13), 'RBBB' (8)",
        stated_source_values="N, LBBB, RBBB",
        preprocessing_strategy="Nominal One-Hot Encoding (N, LBBB, RBBB).",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="LBBB obscures ischemic ECG changes; RBBB indicates conduction system involvement."
    ),

    # ------------------ LABORATORY ------------------
    "FBS": FeatureMetadata(
        name="FBS",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Fasting Blood Sugar (mg/dL)",
        observed_range_or_values="62 to 400 (median 98)",
        stated_source_values="62–400 mg/dl",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="30 IQR outliers; extreme hyperglycemia up to 400 mg/dL preserved.",
        clinical_notes="Reflects glycemic control; diabetes diagnostic marker."
    ),
    "CR": FeatureMetadata(
        name="CR",
        clinical_category="Laboratory",
        data_type="float64",
        source_description="Serum Creatinine (mg/dL)",
        observed_range_or_values="0.5 to 2.2 (median 1.0)",
        stated_source_values="0.5–2.2 mg/dl (labeled 'Cr' in source text)",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="8 IQR outliers; elevated levels reflect renal impairment.",
        clinical_notes="Marker of glomerular filtration and renal clearance."
    ),
    "TG": FeatureMetadata(
        name="TG",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Serum Triglycerides (mg/dL)",
        observed_range_or_values="37 to 1050 (median 122)",
        stated_source_values="37–1050 mg/dl",
        preprocessing_strategy="Numerical pass-through; RobustScaler recommended due to extreme positive skew.",
        model_eligibility="Eligible",
        known_data_quality_issue="16 IQR outliers (max 1050 mg/dL); severe hypertriglyceridemia preserved.",
        clinical_notes="Atherogenic dyslipidemia component."
    ),
    "LDL": FeatureMetadata(
        name="LDL",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Low-Density Lipoprotein cholesterol (mg/dL)",
        observed_range_or_values="18 to 232 (median 100)",
        stated_source_values="18–232 mg/dl",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Primary atherogenic particle in coronary plaque formation."
    ),
    "HDL": FeatureMetadata(
        name="HDL",
        clinical_category="Laboratory",
        data_type="float64",
        source_description="High-Density Lipoprotein cholesterol (mg/dL)",
        observed_range_or_values="15.9 to 111.0 (median 39.0)",
        stated_source_values="15–111 mg/dl",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Anti-atherogenic lipoprotein (reverse cholesterol transport)."
    ),
    "BUN": FeatureMetadata(
        name="BUN",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Blood Urea Nitrogen (mg/dL)",
        observed_range_or_values="6 to 52 (median 16)",
        stated_source_values="6–52 mg/dl",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="17 IQR outliers; elevated in dehydration and renal hypoperfusion.",
        clinical_notes="Urea nitrogen level."
    ),
    "ESR": FeatureMetadata(
        name="ESR",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Erythrocyte Sedimentation Rate (mm/hr)",
        observed_range_or_values="1 to 90 (median 15)",
        stated_source_values="1–90 mm/h",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="13 IQR outliers; non-specific inflammation up to 90 mm/hr.",
        clinical_notes="Systemic inflammation marker."
    ),
    "HB": FeatureMetadata(
        name="HB",
        clinical_category="Laboratory",
        data_type="float64",
        source_description="Hemoglobin concentration (g/dL)",
        observed_range_or_values="8.9 to 17.6 (median 13.2)",
        stated_source_values="8.9–17.6 g/dl",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Oxygen carrying capacity; anemia exacerbates myocardial ischemia."
    ),
    "K": FeatureMetadata(
        name="K",
        clinical_category="Laboratory",
        data_type="float64",
        source_description="Serum Potassium (mEq/L)",
        observed_range_or_values="3.0 to 6.6 (median 4.2)",
        stated_source_values="3.0–6.6 mEq/lit",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Electrolyte governing cardiac membrane potential."
    ),
    "Na": FeatureMetadata(
        name="Na",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Serum Sodium (mEq/L)",
        observed_range_or_values="128 to 156 (median 141)",
        stated_source_values="128–156 mEq/lit",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Serum osmolarity and fluid volume regulation."
    ),
    "WBC": FeatureMetadata(
        name="WBC",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="White Blood Cell count (cells/mcL)",
        observed_range_or_values="3700 to 18000 (median 7100)",
        stated_source_values="3700–18,000 cells/ml",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="9 IQR outliers; leukocytosis up to 18,000 cells/mcL.",
        clinical_notes="Elevated count reflects systemic atheroinflammatory state."
    ),
    "Lymph": FeatureMetadata(
        name="Lymph",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Lymphocyte percentage (%)",
        observed_range_or_values="7 to 60 (median 32)",
        stated_source_values="7–60 %",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Differential leukocyte parameter."
    ),
    "Neut": FeatureMetadata(
        name="Neut",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Neutrophil percentage (%)",
        observed_range_or_values="32 to 89 (median 60)",
        stated_source_values="32–89 %",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="None",
        clinical_notes="Neutrophil-to-lymphocyte ratio is a recognized coronary prognostic marker."
    ),
    "PLT": FeatureMetadata(
        name="PLT",
        clinical_category="Laboratory",
        data_type="int64",
        source_description="Platelet count (10^3 / mcL)",
        observed_range_or_values="25 to 742 (median 210)",
        stated_source_values="25–742 (1000/ml)",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="Extreme physiological span (25 thrombocytopenia to 742 thrombocytosis) preserved.",
        clinical_notes="Critical for thrombosis and plaque fissure response."
    ),

    # ------------------ ECHOCARDIOGRAPHY ------------------
    "EF-TTE": FeatureMetadata(
        name="EF-TTE",
        clinical_category="Echocardiographic",
        data_type="int64",
        source_description="Left Ventricular Ejection Fraction on Transthoracic Echocardiogram (%)",
        observed_range_or_values="15 to 60 (median 50)",
        stated_source_values="15–60 % (labeled 'EF' in source text)",
        preprocessing_strategy="Numerical pass-through; RobustScaler for linear models.",
        model_eligibility="Eligible",
        known_data_quality_issue="Severe systolic dysfunction down to 15% preserved.",
        clinical_notes="Inverse correlation with CAD and LAD stenosis (impaired LV contractility)."
    ),
    "Region RWMA": FeatureMetadata(
        name="Region RWMA",
        clinical_category="Echocardiographic",
        data_type="int64",
        source_description="Regional Wall Motion Abnormality score / count on echocardiography",
        observed_range_or_values="0 (225), 1 (22), 2 (26), 3 (13), 4 (17)",
        stated_source_values="0, 1, 2, 3, 4 (labeled 'Region with RWMA' in source text)",
        preprocessing_strategy="Numerical pass-through. Subject to controlled ablation study.",
        model_eligibility="Eligible",
        known_data_quality_issue="Echocardiographic finding, NOT 3D lesion coordinates. Must not be mapped as physical lesion coordinates.",
        clinical_notes="Reflects ischemic segments; highly associated with LAD stenosis (r=0.36)."
    ),
    "VHD": FeatureMetadata(
        name="VHD",
        clinical_category="Echocardiographic",
        data_type="object",
        source_description="Valvular Heart Disease severity on echocardiography",
        observed_range_or_values="'mild' (149), 'N' (116), 'Moderate' (27), 'Severe' (11)",
        stated_source_values="Normal, mild, moderate, severe",
        preprocessing_strategy="Normalize casing; benchmark BOTH One-Hot and Ordinal encodings.",
        model_eligibility="Eligible",
        known_data_quality_issue="Inconsistent casing in raw data ('mild' lowercase vs 'Severe', 'Moderate' uppercase).",
        clinical_notes="Coexisting valvular pathology."
    ),
}


# Explicit Feature Type Partitions for scikit-learn ColumnTransformer
FEATURE_PARTITIONS: Dict[str, List[str]] = {
    "numerical": [
        "Age", "Weight", "Length", "BMI", "BP", "PR", "FBS", "CR", "TG", "LDL",
        "HDL", "BUN", "ESR", "HB", "K", "Na", "WBC", "Lymph", "Neut", "PLT",
        "EF-TTE", "Region RWMA"
    ],
    "binary_integer": [
        "DM", "HTN", "Current Smoker", "EX-Smoker", "FH", "Edema",
        "Typical Chest Pain", "Q Wave", "St Elevation", "St Depression", "Tinversion"
    ],
    "binary_string": [
        "Obesity", "CRF", "CVA", "Airway disease", "Thyroid Disease", "CHF", "DLP",
        "Weak Peripheral Pulse", "Lung rales", "Systolic Murmur", "Diastolic Murmur",
        "Dyspnea", "Atypical", "Nonanginal", "LowTH Ang", "LVH", "Poor R Progression"
    ],
    "nominal_string": [
        "Sex", "BBB"
    ],
    "ordinal_candidate": [
        "Function Class", "VHD"
    ]
}


def get_feature_metadata(name: str) -> FeatureMetadata:
    """Retrieve metadata for a given feature by column name."""
    if name not in FEATURE_REGISTRY:
        raise KeyError(f"Feature '{name}' not found in CoroVista clinical registry.")
    return FEATURE_REGISTRY[name]


def get_eligible_feature_names() -> List[str]:
    """Returns the ordered list of 54 eligible predictive feature names."""
    return [col for col in ELIGIBLE_FEATURES if col not in TARGET_COLUMNS and col not in ZERO_VARIANCE_COLUMNS]


def assert_no_target_leakage(feature_cols: List[str]) -> None:
    """Automated leakage assertion: fails loudly if any target column is present."""
    leaked = [col for col in TARGET_COLUMNS if col in feature_cols]
    if leaked:
        raise ValueError(
            f"CRITICAL TARGET LEAKAGE DETECTED! Target columns {leaked} found in feature matrix X. "
            f"Training halted immediately to prevent invalid benchmark."
        )
