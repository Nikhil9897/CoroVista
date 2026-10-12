/**
 * CoroVista — Clinical Feature Registry for Patient Simulator (Stage 5C)
 *
 * Source of truth for simulator input forms, validation rules, units,
 * and categories. Mirrors the backend GET /api/v1/features registry.
 * Strictly excludes target columns (Cath, LAD, LCX, RCA).
 */

export type ClinicalCategory =
  | "Demographic"
  | "Symptoms / Examination"
  | "ECG"
  | "Laboratory / Echo"

export type FeatureInputType =
  | "numeric"
  | "binary_yn"
  | "binary_01"
  | "categorical"

export interface SimulatorFeatureMeta {
  machine_name: string
  label: string
  category: ClinicalCategory
  type: FeatureInputType
  unit?: string
  range?: {
    min: number
    max: number
    step: number
  }
  observedRange?: string
  options?: Array<{ value: string | number; label: string }>
  description: string
  warningThresholds?: {
    low?: number
    high?: number
    warningText: string
  }
}

export const CATEGORY_METADATA: Record<
  ClinicalCategory,
  { title: string; description: string; icon: string }
> = {
  Demographic: {
    title: "Demographics & Medical History",
    description: "Baseline age, anthropometrics, co-morbidities, and lifestyle risk factors.",
    icon: "Users",
  },
  "Symptoms / Examination": {
    title: "Physical Exam & Angina Presentation",
    description: "Resting hemodynamics, physical signs of heart failure, and chest pain classification.",
    icon: "Stethoscope",
  },
  ECG: {
    title: "12-Lead Electrocardiography (ECG)",
    description: "Resting ischemic repolarization changes, pathological Q waves, and conduction blocks.",
    icon: "Activity",
  },
  "Laboratory / Echo": {
    title: "Laboratory Biomarkers & Echocardiography",
    description: "Metabolic panel, lipid panel, hematology, and transthoracic echo parameters.",
    icon: "FlaskConical",
  },
}

export const SIMULATOR_FEATURES: SimulatorFeatureMeta[] = [
  // ==========================================
  // 1. DEMOGRAPHICS & MEDICAL HISTORY (17)
  // ==========================================
  {
    machine_name: "Age",
    label: "Patient Age",
    category: "Demographic",
    type: "numeric",
    unit: "years",
    range: { min: 18, max: 100, step: 1 },
    observedRange: "30 to 86 (mean 58.9)",
    description: "Chronological age in years.",
    warningThresholds: { low: 25, high: 90, warningText: "Patient age is outside typical coronary cohort age range." },
  },
  {
    machine_name: "Sex",
    label: "Biological Sex",
    category: "Demographic",
    type: "categorical",
    options: [
      { value: "Male", label: "Male" },
      { value: "Female", label: "Female" },
    ],
    observedRange: "Male (176), Female (127)",
    description: "Biological sex.",
  },
  {
    machine_name: "Weight",
    label: "Body Weight",
    category: "Demographic",
    type: "numeric",
    unit: "kg",
    range: { min: 30, max: 200, step: 1 },
    observedRange: "48 to 120 kg (mean 73.8)",
    description: "Current patient weight.",
  },
  {
    machine_name: "Length",
    label: "Height (Stature)",
    category: "Demographic",
    type: "numeric",
    unit: "cm",
    range: { min: 120, max: 220, step: 1 },
    observedRange: "140 to 188 cm (mean 164.7)",
    description: "Patient height in centimeters.",
  },
  {
    machine_name: "BMI",
    label: "Body Mass Index",
    category: "Demographic",
    type: "numeric",
    unit: "kg/m²",
    range: { min: 14, max: 60, step: 0.1 },
    observedRange: "18.1 to 41.0 (mean 27.2)",
    description: "Calculated BMI (Weight / Length²).",
    warningThresholds: { high: 45, warningText: "Severe Class III obesity (BMI > 45)." },
  },
  {
    machine_name: "DM",
    label: "Diabetes Mellitus",
    category: "Demographic",
    type: "binary_01",
    options: [
      { value: 0, label: "No (0)" },
      { value: 1, label: "Yes (1)" },
    ],
    observedRange: "0 = 213 (70.3%), 1 = 90 (29.7%)",
    description: "Diagnosed diabetes mellitus or fasting glucose ≥ 126 mg/dL.",
  },
  {
    machine_name: "HTN",
    label: "Systemic Hypertension",
    category: "Demographic",
    type: "binary_01",
    options: [
      { value: 0, label: "No (0)" },
      { value: 1, label: "Yes (1)" },
    ],
    observedRange: "0 = 124 (40.9%), 1 = 179 (59.1%)",
    description: "History of hypertension or chronic antihypertensive therapy.",
  },
  {
    machine_name: "Current Smoker",
    label: "Current Smoker",
    category: "Demographic",
    type: "binary_01",
    options: [
      { value: 0, label: "No (0)" },
      { value: 1, label: "Yes (1)" },
    ],
    observedRange: "0 = 240 (79.2%), 1 = 63 (20.8%)",
    description: "Active tobacco smoking within the preceding 12 months.",
  },
  {
    machine_name: "EX-Smoker",
    label: "Former Smoker (Ex-Smoker)",
    category: "Demographic",
    type: "binary_01",
    options: [
      { value: 0, label: "No (0)" },
      { value: 1, label: "Yes (1)" },
    ],
    observedRange: "0 = 293 (96.7%), 1 = 10 (3.3%)",
    description: "History of smoking with cessation > 12 months.",
  },
  {
    machine_name: "FH",
    label: "Family History of CAD",
    category: "Demographic",
    type: "binary_01",
    options: [
      { value: 0, label: "No (0)" },
      { value: 1, label: "Yes (1)" },
    ],
    observedRange: "0 = 255 (84.2%), 1 = 48 (15.8%)",
    description: "First-degree relative with premature cardiovascular disease.",
  },
  {
    machine_name: "Obesity",
    label: "Clinical Obesity (BMI > 25)",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "Y = 205 (67.7%), N = 98 (32.3%)",
    description: "Categorical clinical obesity flag.",
  },
  {
    machine_name: "CRF",
    label: "Chronic Renal Failure",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 299 (98.7%), Y = 4 (1.3%)",
    description: "Known chronic renal disease or sustained elevated creatinine.",
  },
  {
    machine_name: "CVA",
    label: "Cerebrovascular Accident (Stroke)",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 297 (98.0%), Y = 6 (2.0%)",
    description: "Prior stroke or transient ischemic attack (TIA).",
  },
  {
    machine_name: "Airway disease",
    label: "Chronic Airway Disease",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 286 (94.4%), Y = 17 (5.6%)",
    description: "History of COPD or chronic asthma.",
  },
  {
    machine_name: "Thyroid Disease",
    label: "Thyroid Disease",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 298 (98.3%), Y = 5 (1.7%)",
    description: "Hypothyroidism or hyperthyroidism history.",
  },
  {
    machine_name: "CHF",
    label: "Congestive Heart Failure",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 302 (99.7%), Y = 1 (0.3%)",
    description: "Prior diagnosis of congestive heart failure.",
  },
  {
    machine_name: "DLP",
    label: "Dyslipidemia",
    category: "Demographic",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "Y = 200 (66.0%), N = 103 (34.0%)",
    description: "Documented history of hyperlipidemia or active lipid therapy.",
  },

  // ==========================================
  // 2. SYMPTOMS & PHYSICAL EXAM (14)
  // ==========================================
  {
    machine_name: "BP",
    label: "Systolic Blood Pressure",
    category: "Symptoms / Examination",
    type: "numeric",
    unit: "mmHg",
    range: { min: 70, max: 240, step: 1 },
    observedRange: "90 to 190 mmHg (mean 129.5)",
    description: "Resting systolic blood pressure.",
    warningThresholds: { high: 180, low: 85, warningText: "Severe hemodynamic pressure range (< 85 or > 180 mmHg)." },
  },
  {
    machine_name: "PR",
    label: "Resting Pulse Rate",
    category: "Symptoms / Examination",
    type: "numeric",
    unit: "bpm",
    range: { min: 40, max: 180, step: 1 },
    observedRange: "50 to 110 bpm (mean 75.1)",
    description: "Resting cardiac rate in beats per minute.",
    warningThresholds: { high: 140, low: 45, warningText: "Marked tachycardia or severe bradycardia." },
  },
  {
    machine_name: "Edema",
    label: "Peripheral Edema",
    category: "Symptoms / Examination",
    type: "binary_01",
    options: [
      { value: 0, label: "Absent (0)" },
      { value: 1, label: "Present (1)" },
    ],
    observedRange: "0 = 291 (96.0%), 1 = 12 (4.0%)",
    description: "Lower extremity pitting edema on examination.",
  },
  {
    machine_name: "Weak Peripheral Pulse",
    label: "Weak Peripheral Pulse",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "Normal (N)" },
      { value: "Y", label: "Weak / Absent (Y)" },
    ],
    observedRange: "N = 274 (90.4%), Y = 29 (9.6%)",
    description: "Diminished dorsalis pedis or radial pulses.",
  },
  {
    machine_name: "Lung rales",
    label: "Pulmonary Rales (Crackles)",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "Absent (N)" },
      { value: "Y", label: "Present (Y)" },
    ],
    observedRange: "N = 289 (95.4%), Y = 14 (4.6%)",
    description: "Auscultated pulmonary crackles suggestive of pulmonary congestion.",
  },
  {
    machine_name: "Systolic Murmur",
    label: "Systolic Heart Murmur",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "Absent (N)" },
      { value: "Y", label: "Present (Y)" },
    ],
    observedRange: "N = 281 (92.7%), Y = 22 (7.3%)",
    description: "Auscultated systolic cardiac murmur.",
  },
  {
    machine_name: "Diastolic Murmur",
    label: "Diastolic Heart Murmur",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "Absent (N)" },
      { value: "Y", label: "Present (Y)" },
    ],
    observedRange: "N = 290 (95.7%), Y = 13 (4.3%)",
    description: "Auscultated diastolic cardiac murmur.",
  },
  {
    machine_name: "Typical Chest Pain",
    label: "Typical Anginal Chest Pain",
    category: "Symptoms / Examination",
    type: "binary_01",
    options: [
      { value: 0, label: "No (0)" },
      { value: 1, label: "Yes (1)" },
    ],
    observedRange: "1 = 164 (54.1%), 0 = 139 (45.9%)",
    description: "Substernal pressure precipitated by exertion and relieved by rest or nitroglycerin.",
  },
  {
    machine_name: "Dyspnea",
    label: "Exertional Dyspnea",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 241 (79.5%), Y = 62 (20.5%)",
    description: "Shortness of breath on mild to moderate physical exertion.",
  },
  {
    machine_name: "Function Class",
    label: "NYHA Functional Class",
    category: "Symptoms / Examination",
    type: "numeric",
    range: { min: 0, max: 3, step: 1 },
    options: [
      { value: 0, label: "Class 0 / None (0)" },
      { value: 1, label: "Class I (1)" },
      { value: 2, label: "Class II (2)" },
      { value: 3, label: "Class III (3)" },
    ],
    observedRange: "0 to 3 (median 2)",
    description: "New York Heart Association symptomatic limitation score.",
  },
  {
    machine_name: "Atypical",
    label: "Atypical Chest Pain",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 217 (71.6%), Y = 86 (28.4%)",
    description: "Chest discomfort with only 2 of 3 typical anginal criteria.",
  },
  {
    machine_name: "Nonanginal",
    label: "Non-Anginal Chest Pain",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 287 (94.7%), Y = 16 (5.3%)",
    description: "Chest pain lacking typical anginal characteristics.",
  },

  {
    machine_name: "LowTH Ang",
    label: "Low-Threshold Angina",
    category: "Symptoms / Examination",
    type: "binary_yn",
    options: [
      { value: "N", label: "No (N)" },
      { value: "Y", label: "Yes (Y)" },
    ],
    observedRange: "N = 301 (99.3%), Y = 2 (0.7%)",
    description: "Angina provoked by minimal physical exertion.",
  },

  // ==========================================
  // 3. 12-LEAD ECG (7)
  // ==========================================
  {
    machine_name: "Q Wave",
    label: "Pathological Q Waves",
    category: "ECG",
    type: "binary_01",
    options: [
      { value: 0, label: "Absent (0)" },
      { value: 1, label: "Present (1)" },
    ],
    observedRange: "0 = 286 (94.4%), 1 = 17 (5.6%)",
    description: "Pathological Q waves indicative of prior myocardial necrosis.",
  },
  {
    machine_name: "St Elevation",
    label: "ST-Segment Elevation",
    category: "ECG",
    type: "binary_01",
    options: [
      { value: 0, label: "Absent (0)" },
      { value: 1, label: "Present (1)" },
    ],
    observedRange: "0 = 289 (95.4%), 1 = 14 (4.6%)",
    description: "Acute or persistent ST-segment elevation on resting ECG.",
  },
  {
    machine_name: "St Depression",
    label: "ST-Segment Depression",
    category: "ECG",
    type: "binary_01",
    options: [
      { value: 0, label: "Absent (0)" },
      { value: 1, label: "Present (1)" },
    ],
    observedRange: "0 = 232 (76.6%), 1 = 71 (23.4%)",
    description: "Horizontal or downsloping ST depression ≥ 0.5 mm.",
  },
  {
    machine_name: "Tinversion",
    label: "T-Wave Inversion",
    category: "ECG",
    type: "binary_01",
    options: [
      { value: 0, label: "Absent (0)" },
      { value: 1, label: "Present (1)" },
    ],
    observedRange: "0 = 221 (72.9%), 1 = 82 (27.1%)",
    description: "Symmetric T-wave inversion in 2 or more contiguous leads.",
  },
  {
    machine_name: "LVH",
    label: "Left Ventricular Hypertrophy (ECG)",
    category: "ECG",
    type: "binary_yn",
    options: [
      { value: "N", label: "Absent (N)" },
      { value: "Y", label: "Present (Y)" },
    ],
    observedRange: "N = 277 (91.4%), Y = 26 (8.6%)",
    description: "Sokolow-Lyon or Cornell voltage criteria for LVH on ECG.",
  },
  {
    machine_name: "Poor R Progression",
    label: "Poor Precordial R Progression",
    category: "ECG",
    type: "binary_yn",
    options: [
      { value: "N", label: "Normal (N)" },
      { value: "Y", label: "Poor Progression (Y)" },
    ],
    observedRange: "N = 285 (94.1%), Y = 18 (5.9%)",
    description: "Failure of R-wave amplitude to increase appropriately from V1 to V3.",
  },
  {
    machine_name: "BBB",
    label: "Bundle Branch Block",
    category: "ECG",
    type: "categorical",
    options: [
      { value: "N", label: "None / Normal (N)" },
      { value: "LBBB", label: "Left Bundle Branch Block (LBBB)" },
      { value: "RBBB", label: "Right Bundle Branch Block (RBBB)" },
    ],
    observedRange: "N = 287, LBBB = 9, RBBB = 7",
    description: "Intraventricular conduction delay (QRS duration ≥ 120 ms).",
  },

  // ==========================================
  // 4. LABORATORY & ECHOCARDIOGRAPHY (17)
  // ==========================================
  {
    machine_name: "FBS",
    label: "Fasting Blood Sugar",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mg/dL",
    range: { min: 40, max: 500, step: 1 },
    observedRange: "62 to 400 mg/dL (mean 119.1)",
    description: "Serum fasting glucose concentration.",
    warningThresholds: { high: 250, low: 55, warningText: "Marked hyperglycemia or hypoglycemia." },
  },
  {
    machine_name: "CR",
    label: "Serum Creatinine",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mg/dL",
    range: { min: 0.2, max: 15.0, step: 0.1 },
    observedRange: "0.5 to 2.2 mg/dL (mean 1.05)",
    description: "Renal filtration marker.",
    warningThresholds: { high: 3.5, warningText: "Significantly elevated creatinine indicative of renal impairment." },
  },
  {
    machine_name: "TG",
    label: "Serum Triglycerides",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mg/dL",
    range: { min: 20, max: 1000, step: 1 },
    observedRange: "47 to 1050 mg/dL (mean 150.3)",
    description: "Fasting serum triglyceride concentration.",
    warningThresholds: { high: 500, warningText: "Severe hypertriglyceridemia (> 500 mg/dL)." },
  },
  {
    machine_name: "LDL",
    label: "LDL Cholesterol",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mg/dL",
    range: { min: 20, max: 400, step: 1 },
    observedRange: "18 to 232 mg/dL (mean 104.6)",
    description: "Low-density lipoprotein cholesterol.",
    warningThresholds: { high: 190, warningText: "Very high LDL cholesterol (≥ 190 mg/dL)." },
  },
  {
    machine_name: "HDL",
    label: "HDL Cholesterol",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mg/dL",
    range: { min: 10, max: 120, step: 1 },
    observedRange: "15 to 111 mg/dL (mean 40.2)",
    description: "High-density lipoprotein cholesterol.",
    warningThresholds: { low: 25, warningText: "Severely depressed protective HDL (< 25 mg/dL)." },
  },
  {
    machine_name: "BUN",
    label: "Blood Urea Nitrogen",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mg/dL",
    range: { min: 4, max: 150, step: 1 },
    observedRange: "6 to 52 mg/dL (mean 17.5)",
    description: "Blood urea nitrogen.",
  },
  {
    machine_name: "ESR",
    label: "Erythrocyte Sedimentation Rate",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mm/hr",
    range: { min: 1, max: 120, step: 1 },
    observedRange: "1 to 90 mm/hr (mean 19.5)",
    description: "Inflammatory non-specific sedimentation marker.",
  },
  {
    machine_name: "HB",
    label: "Hemoglobin Concentration",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "g/dL",
    range: { min: 5.0, max: 22.0, step: 0.1 },
    observedRange: "8.9 to 17.6 g/dL (mean 13.1)",
    description: "Circulating hemoglobin.",
    warningThresholds: { low: 9.0, high: 18.5, warningText: "Anemia or secondary polycythemia." },
  },
  {
    machine_name: "K",
    label: "Serum Potassium",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mEq/L",
    range: { min: 2.0, max: 8.0, step: 0.1 },
    observedRange: "3.0 to 6.6 mEq/L (mean 4.23)",
    description: "Serum electrolyte potassium.",
    warningThresholds: { low: 3.2, high: 5.8, warningText: "Arrhythmogenic hypokalemia or hyperkalemia." },
  },
  {
    machine_name: "Na",
    label: "Serum Sodium",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "mEq/L",
    range: { min: 110, max: 160, step: 1 },
    observedRange: "128 to 156 mEq/L (mean 140.3)",
    description: "Serum electrolyte sodium.",
  },
  {
    machine_name: "WBC",
    label: "White Blood Cell Count",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "cells/µL",
    range: { min: 1000, max: 30000, step: 100 },
    observedRange: "3700 to 18000 (mean 7562)",
    description: "Total circulating leukocyte count.",
  },
  {
    machine_name: "Lymph",
    label: "Lymphocyte Percentage",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "%",
    range: { min: 5, max: 90, step: 1 },
    observedRange: "7 to 60% (mean 32.4%)",
    description: "Differential lymphocyte percentage.",
  },
  {
    machine_name: "Neut",
    label: "Neutrophil Percentage",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "%",
    range: { min: 10, max: 95, step: 1 },
    observedRange: "32 to 89% (mean 60.1%)",
    description: "Differential neutrophil percentage.",
  },
  {
    machine_name: "PLT",
    label: "Platelet Count",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "×10³/µL",
    range: { min: 20, max: 1000, step: 1 },
    observedRange: "25 to 742 (mean 221.5)",
    description: "Thrombocyte count per microliter.",
  },
  {
    machine_name: "EF-TTE",
    label: "Ejection Fraction (Echocardiography)",
    category: "Laboratory / Echo",
    type: "numeric",
    unit: "%",
    range: { min: 10, max: 80, step: 1 },
    observedRange: "15 to 60% (mean 47.2%)",
    description: "Left ventricular ejection fraction on transthoracic echocardiogram.",
    warningThresholds: { low: 30, warningText: "Severely reduced LV ejection fraction (HFrEF, EF < 30%)." },
  },
  {
    machine_name: "Region RWMA",
    label: "Regional Wall Motion Abnormality Count",
    category: "Laboratory / Echo",
    type: "numeric",
    range: { min: 0, max: 4, step: 1 },
    options: [
      { value: 0, label: "0 Segments (Normal)" },
      { value: 1, label: "1 Segment" },
      { value: 2, label: "2 Segments" },
      { value: 3, label: "3 Segments" },
      { value: 4, label: "4+ Segments" },
    ],
    observedRange: "0 to 4 (median 0)",
    description: "Number of myocardial segments exhibiting hypokinesis or akinesis on echo.",
  },
  {
    machine_name: "VHD",
    label: "Valvular Heart Disease Severity",
    category: "Laboratory / Echo",
    type: "categorical",
    options: [
      { value: "Normal", label: "Normal (No VHD)" },
      { value: "Mild", label: "Mild VHD" },
      { value: "Moderate", label: "Moderate VHD" },
      { value: "Severe", label: "Severe VHD" },
    ],
    observedRange: "Normal = 217, Mild = 64, Moderate = 21, Severe = 1",
    description: "Echocardiographic degree of valvular disease.",
  },
]

export const FORBIDDEN_TARGET_NAMES = new Set(["Cath", "LAD", "LCX", "RCA", "cath", "lad", "lcx", "rca"])

/**
 * Validates patient form inputs against the clinical registry contract.
 */
export function validatePatientRecord(data: Record<string, unknown>): {
  isValid: boolean
  errors: Record<string, string>
  warnings: Record<string, string>
} {
  const errors: Record<string, string> = {}
  const warnings: Record<string, string> = {}

  // 1. Target leakage gate
  for (const key of Object.keys(data)) {
    if (FORBIDDEN_TARGET_NAMES.has(key)) {
      errors[key] = `Target leakage: Ground truth column '${key}' must not be submitted.`
    }
  }

  // 2. Feature validation
  for (const feat of SIMULATOR_FEATURES) {
    const val = data[feat.machine_name]

    if (val === undefined || val === null || val === "") {
      errors[feat.machine_name] = `${feat.label} is required.`
      continue
    }

    if (feat.type === "numeric") {
      const num = Number(val)
      if (isNaN(num)) {
        errors[feat.machine_name] = `${feat.label} must be a valid number.`
      } else {
        // Warning if outside plausible range
        if (feat.warningThresholds) {
          if (feat.warningThresholds.low !== undefined && num < feat.warningThresholds.low) {
            warnings[feat.machine_name] = feat.warningThresholds.warningText
          } else if (feat.warningThresholds.high !== undefined && num > feat.warningThresholds.high) {
            warnings[feat.machine_name] = feat.warningThresholds.warningText
          }
        }
      }
    } else if (feat.type === "categorical" || feat.type === "binary_yn" || feat.type === "binary_01") {
      if (feat.options) {
        const allowedVals = feat.options.map((o) => String(o.value).toLowerCase())
        if (!allowedVals.includes(String(val).toLowerCase())) {
          errors[feat.machine_name] = `Invalid selection for ${feat.label}.`
        }
      }
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    warnings,
  }
}
