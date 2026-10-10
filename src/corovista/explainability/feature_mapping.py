"""
CoroVista - Feature Mapping & Human-Readable Metadata
Clinical Nomenclature & Unit Translation Service

Maps pipeline transformed feature names (e.g., 'BBB_RBBB', 'VHD_Moderate', 'Typical Chest Pain')
to human-readable clinical labels, unit descriptions, and category metadata suitable
for clinician review and future frontend UI cards.
"""

from typing import Dict, Optional

# Transformed feature name -> Human-readable label & units
FEATURE_LABEL_MAP: Dict[str, str] = {
    # Demographics & Anthropometrics
    "Age": "Patient Age (years)",
    "Weight": "Body Weight (kg)",
    "Length": "Height / Stature (cm)",
    "BMI": "Body Mass Index (kg/m²)",
    "Sex": "Biological Sex (Male = 1, Female = 0)",

    # Hemodynamics & Physical Exam
    "BP": "Systolic Blood Pressure (mmHg)",
    "PR": "Resting Heart Rate (bpm)",
    "Edema": "Peripheral Edema",
    "Weak Peripheral Pulse": "Diminished Peripheral Pulses",
    "Lung rales": "Pulmonary Rales / Crackles",
    "Systolic Murmur": "Auscultated Systolic Murmur",
    "Diastolic Murmur": "Auscultated Diastolic Murmur",

    # Symptoms & History
    "Typical Chest Pain": "Typical Anginal Chest Pain",
    "Dyspnea": "Exertional Dyspnea (Shortness of Breath)",
    "Function Class": "NYHA Functional Class (0–3)",
    "Atypical": "Atypical Angina Symptoms",
    "Nonanginal": "Non-Anginal Chest Pain",
    "LowTH Ang": "Low-Threshold Angina",
    "DM": "Diabetes Mellitus History",
    "HTN": "Hypertension History",
    "Current Smoker": "Current Tobacco Smoker",
    "EX-Smoker": "Former Tobacco Smoker",
    "FH": "Family History of Premature CAD",
    "Obesity": "Clinical Obesity (BMI > 25)",
    "CRF": "Chronic Renal Failure History",
    "CVA": "Cerebrovascular Accident (Stroke/TIA)",
    "Airway disease": "Chronic Airway Disease (COPD/Asthma)",
    "Thyroid Disease": "Thyroid Disease History",
    "CHF": "Congestive Heart Failure History",
    "DLP": "Dyslipidemia History",

    # 12-Lead ECG Findings
    "Q Wave": "Pathological Q Waves (ECG)",
    "St Elevation": "ST-Segment Elevation (ECG)",
    "St Depression": "ST-Segment Depression (ECG)",
    "Tinversion": "T-Wave Inversion (ECG)",
    "LVH": "Left Ventricular Hypertrophy Criteria (ECG)",
    "Poor R Progression": "Poor Precordial R-Wave Progression (ECG)",
    "BBB_N": "Normal Intraventricular Conduction (No BBB)",
    "BBB_RBBB": "Right Bundle Branch Block (ECG)",
    "BBB_LBBB": "Left Bundle Branch Block (ECG)",

    # Laboratory Biomarkers
    "FBS": "Fasting Blood Sugar (mg/dL)",
    "CR": "Serum Creatinine (mg/dL)",
    "TG": "Serum Triglycerides (mg/dL)",
    "LDL": "LDL Cholesterol (mg/dL)",
    "HDL": "HDL Cholesterol (mg/dL)",
    "BUN": "Blood Urea Nitrogen (mg/dL)",
    "ESR": "Erythrocyte Sedimentation Rate (mm/hr)",
    "HB": "Hemoglobin Concentration (g/dL)",
    "K": "Serum Potassium (mEq/L)",
    "Na": "Serum Sodium (mEq/L)",
    "WBC": "White Blood Cell Count (/µL)",
    "Lymph": "Lymphocyte Percentage (%)",
    "Neut": "Neutrophil Percentage (%)",
    "PLT": "Platelet Count (×10³/µL)",

    # Echocardiography
    "EF-TTE": "Left Ventricular Ejection Fraction (% Echo)",
    "Region RWMA": "Regional Wall Motion Abnormality Count (Echo)",
    "VHD": "Valvular Heart Disease Severity (Ordinal)",
    "VHD_Normal": "Normal Cardiac Valves (Echo)",
    "VHD_Mild": "Mild Valvular Heart Disease (Echo)",
    "VHD_Moderate": "Moderate Valvular Heart Disease (Echo)",
    "VHD_Severe": "Severe Valvular Heart Disease (Echo)",
}


def get_human_label(feature_name: str) -> str:
    """Returns a clean, human-readable clinical label for any pipeline feature."""
    # Strip any transformer prefixes (e.g., 'num__', 'bin__', 'cat__')
    clean_name = feature_name
    for prefix in ["num__", "bin__", "cat__", "remainder__"]:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]

    return FEATURE_LABEL_MAP.get(clean_name, clean_name)


def get_feature_description(feature_name: str) -> str:
    """Returns a clinical explanatory note for the feature."""
    label = get_human_label(feature_name)
    if "Echo" in label:
        return f"{label} obtained via pre-catheterization transthoracic echocardiography."
    elif "ECG" in label:
        return f"{label} observed on resting 12-lead electrocardiogram."
    elif "mg/dL" in label or "g/dL" in label or "mEq/L" in label:
        return f"{label} from pre-catheterization routine laboratory blood draw."
    else:
        return f"{label} documented during bedside clinical examination and history."
