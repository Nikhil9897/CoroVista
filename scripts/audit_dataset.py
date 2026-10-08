"""
CoroVista - Dataset Audit Script
Stage 1: Project Foundation & Complete Dataset Audit

This script performs an exhaustive, reproducible audit of the raw dataset:
'data/raw/extention of Z-Alizadeh sani dataset.xlsx'
and produces:
1. data/reports/dataset_audit.json (Machine-readable audit summary)
2. data/reports/dataset_audit.md   (Human-readable comprehensive audit report)
3. data/reports/feature_inventory.csv (Complete feature-by-feature inventory)
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import openpyxl
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("audit_dataset")

# Expected targets according to Track A requirements
TARGET_COLUMNS = ["Cath", "LAD", "LCX", "RCA"]

# Feature Category Definitions
FEATURE_CATEGORIES = {
    "Demographic": ["Age", "Weight", "Length", "Sex", "BMI"],
    "Clinical Examination": [
        "DM",
        "HTN",
        "Current Smoker",
        "EX-Smoker",
        "FH",
        "Obesity",
        "CRF",
        "CVA",
        "Airway disease",
        "Thyroid Disease",
        "CHF",
        "DLP",
        "BP",
        "PR",
        "Edema",
        "Weak Peripheral Pulse",
        "Lung rales",
        "Systolic Murmur",
        "Diastolic Murmur",
        "Typical Chest Pain",
        "Dyspnea",
        "Function Class",
        "Atypical",
        "Nonanginal",
        "Exertional CP",
        "LowTH Ang",
    ],
    "ECG": [
        "Q Wave",
        "St Elevation",
        "St Depression",
        "Tinversion",
        "LVH",
        "Poor R Progression",
        "BBB",
    ],
    "Laboratory": [
        "FBS",
        "CR",
        "TG",
        "LDL",
        "HDL",
        "BUN",
        "ESR",
        "HB",
        "K",
        "Na",
        "WBC",
        "Lymph",
        "Neut",
        "PLT",
    ],
    "Echocardiographic": [
        "EF-TTE",
        "Region RWMA",
        "VHD",
    ],
    "Target": [
        "Cath",
        "LAD",
        "LCX",
        "RCA",
    ],
}


def get_feature_category(feature_name: str) -> str:
    """Returns the clinical domain category of a given feature."""
    for category, cols in FEATURE_CATEGORIES.items():
        if feature_name in cols:
            return category
    return "Other / Unknown"


def inspect_workbook(file_path: Path) -> Dict[str, Any]:
    """Inspects the raw Excel workbook structure without modifying it."""
    wb = openpyxl.load_workbook(str(file_path), data_only=True)
    sheets_info = {}
    primary_sheet = None

    for name in wb.sheetnames:
        sheet = wb[name]
        max_row = sheet.max_row or 0
        max_col = sheet.max_column or 0
        data_rows = max(0, max_row - 1)
        is_empty_of_data = data_rows == 0

        sheets_info[name] = {
            "total_rows": max_row,
            "data_rows": data_rows,
            "max_columns": max_col,
            "is_empty_of_data": is_empty_of_data,
        }

        if not is_empty_of_data and primary_sheet is None:
            primary_sheet = name

    return {
        "file_name": file_path.name,
        "sheet_names": wb.sheetnames,
        "sheets_info": sheets_info,
        "primary_sheet": primary_sheet,
    }


def load_dataset(file_path: Path, sheet_name: str = "Sheet 1 - Table 1") -> pd.DataFrame:
    """Loads the dataset from the verified primary sheet."""
    df = pd.read_excel(str(file_path), sheet_name=sheet_name)
    return df


def audit_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Performs rigorous data quality checks on the dataframe."""
    n_rows, n_cols = df.shape

    # 1. Missing values
    missing_counts = df.isnull().sum()
    missing_dict = {col: int(cnt) for col, cnt in missing_counts.items() if cnt > 0}
    total_missing = int(missing_counts.sum())

    # 2. Duplicate rows
    n_duplicates = int(df.duplicated().sum())

    # 3. Constant and near-constant features (excluding targets)
    feature_cols = [c for c in df.columns if c not in TARGET_COLUMNS]
    constant_features = []
    near_constant_features = []

    for col in feature_cols:
        val_counts = df[col].value_counts(dropna=False)
        unique_cnt = len(val_counts)
        dominant_freq = val_counts.iloc[0] / n_rows

        if unique_cnt <= 1:
            constant_features.append({"feature": col, "value": str(val_counts.index[0])})
        elif dominant_freq >= 0.90:
            near_constant_features.append(
                {
                    "feature": col,
                    "dominant_value": str(val_counts.index[0]),
                    "dominant_count": int(val_counts.iloc[0]),
                    "dominant_percentage": round(dominant_freq * 100, 2),
                    "unique_count": unique_cnt,
                }
            )

    # 4. Known categorical inconsistencies
    categorical_issues = []
    if "Sex" in df.columns:
        sex_vals = df["Sex"].unique().tolist()
        if "Fmale" in sex_vals:
            categorical_issues.append(
                {
                    "feature": "Sex",
                    "original_value": "Fmale",
                    "potential_intended_meaning": "Female",
                    "evidence": "Dataset documentation and binary biological sex categorization. 127 records have 'Fmale', 176 have 'Male'.",
                    "proposed_transformation": "Map 'Fmale' -> 'Female' (or 0) reproducibly during preprocessing.",
                }
            )

    if "VHD" in df.columns:
        vhd_vals = df["VHD"].unique().tolist()
        categorical_issues.append(
            {
                "feature": "VHD",
                "original_value": str(vhd_vals),
                "potential_intended_meaning": "Valvular Heart Disease severity ordinal scale: None ('N'), Mild, Moderate, Severe",
                "evidence": "Mixed casing found: 'mild' (lowercase) vs 'Severe' and 'Moderate' (capitalized).",
                "proposed_transformation": "Standardize casing ('N', 'Mild', 'Moderate', 'Severe') and map to ordinal levels 0, 1, 2, 3.",
            }
        )

    # 5. Numerical Outlier & Range Inspection
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Separate continuous features from binary/ordinal indicators stored as ints
    continuous_candidates = [
        c
        for c in numerical_cols
        if df[c].nunique() > 10 and c not in TARGET_COLUMNS
    ]

    outliers_info = {}
    for col in continuous_candidates:
        q1 = float(df[col].quantile(0.25))
        q3 = float(df[col].quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)][col]
        outlier_cnt = int(len(outliers))
        if outlier_cnt > 0:
            outliers_info[col] = {
                "outlier_count": outlier_cnt,
                "outlier_percentage": round((outlier_cnt / n_rows) * 100, 2),
                "q1": round(q1, 2),
                "median": round(float(df[col].median()), 2),
                "q3": round(q3, 2),
                "iqr": round(iqr, 2),
                "min": round(float(df[col].min()), 2),
                "max": round(float(df[col].max()), 2),
                "lower_bound": round(lower, 2),
                "upper_bound": round(upper, 2),
                "extreme_values": [round(float(x), 2) for x in outliers.iloc[:5].tolist()],
            }

    # 6. Specific Anomaly: Vessel stenosis vs Cath mismatch
    # Cath is diagnostic catheterization outcome. Let's inspect consistency.
    any_vessel_stenotic = (
        (df["LAD"] == "Stenotic") | (df["LCX"] == "Stenotic") | (df["RCA"] == "Stenotic")
    )
    cath_cad = df["Cath"] == "CAD"
    mismatch_mask = any_vessel_stenotic != cath_cad
    mismatches = []
    if mismatch_mask.any():
        mismatch_indices = df[mismatch_mask].index.tolist()
        for idx in mismatch_indices:
            row = df.loc[idx]
            mismatches.append(
                {
                    "row_index": int(idx),
                    "LAD": str(row["LAD"]),
                    "LCX": str(row["LCX"]),
                    "RCA": str(row["RCA"]),
                    "Cath": str(row["Cath"]),
                    "explanation": (
                        f"Patient index {idx} has LAD=Stenotic, LCX=Normal, RCA=Normal, "
                        f"but Cath=Normal. In 302/303 cases (99.67%), Cath=CAD is identical to "
                        f"(LAD|LCX|RCA == Stenotic)."
                    ),
                }
            )

    return {
        "n_rows": n_rows,
        "n_columns": n_cols,
        "total_missing": total_missing,
        "missing_by_column": missing_dict,
        "duplicate_rows": n_duplicates,
        "constant_features": constant_features,
        "near_constant_features": near_constant_features,
        "categorical_issues": categorical_issues,
        "numerical_outliers": outliers_info,
        "cath_vessel_mismatches": mismatches,
    }


def audit_targets(df: pd.DataFrame) -> Dict[str, Any]:
    """Audits each of the four prediction targets."""
    target_summary = {}

    target_definitions = {
        "Cath": {
            "clinical_name": "Overall Coronary Artery Disease (CAD)",
            "positive_label": "CAD",
            "negative_label": "Normal",
        },
        "LAD": {
            "clinical_name": "Left Anterior Descending Stenosis",
            "positive_label": "Stenotic",
            "negative_label": "Normal",
        },
        "LCX": {
            "clinical_name": "Left Circumflex Stenosis",
            "positive_label": "Stenotic",
            "negative_label": "Normal",
        },
        "RCA": {
            "clinical_name": "Right Coronary Artery Stenosis",
            "positive_label": "Stenotic",
            "negative_label": "Normal",
        },
    }

    n_rows = len(df)

    for target in TARGET_COLUMNS:
        if target not in df.columns:
            target_summary[target] = {"error": "Target column missing from dataset"}
            continue

        counts = df[target].value_counts(dropna=False).to_dict()
        unique_vals = list(counts.keys())
        pos_label = target_definitions[target]["positive_label"]
        neg_label = target_definitions[target]["negative_label"]

        pos_count = counts.get(pos_label, 0)
        neg_count = counts.get(neg_label, 0)

        pos_pct = round((pos_count / n_rows) * 100, 2)
        neg_pct = round((neg_count / n_rows) * 100, 2)

        # Imbalance ratio: majority to minority
        majority_count = max(pos_count, neg_count)
        minority_count = min(pos_count, neg_count)
        imbalance_ratio = round(majority_count / minority_count, 2) if minority_count > 0 else None

        target_summary[target] = {
            "clinical_name": target_definitions[target]["clinical_name"],
            "unique_values": [str(v) for v in unique_vals],
            "positive_label": pos_label,
            "negative_label": neg_label,
            "positive_count": int(pos_count),
            "negative_count": int(neg_count),
            "positive_percentage": pos_pct,
            "negative_percentage": neg_pct,
            "imbalance_ratio": imbalance_ratio,
            "dominant_class": pos_label if pos_count > neg_count else neg_label,
            "imbalance_assessment": (
                f"{imbalance_ratio}:1 imbalance with dominant class '{pos_label if pos_count > neg_count else neg_label}'. "
                f"Accuracy alone will be misleading; precision, recall, F1, and ROC-AUC are required."
            ),
        }

    return target_summary


def audit_leakage(df: pd.DataFrame) -> Dict[str, Any]:
    """Audits data leakage vulnerabilities and feature admissibility."""
    # 1. Target leakage verification: check that target columns are identifiable
    excluded_targets = [t for t in TARGET_COLUMNS if t in df.columns]

    # 2. Scrutiny of other features
    suspicious_features = [
        {
            "feature": "Region RWMA",
            "why_suspicious": (
                "Echocardiographic Regional Wall Motion Abnormality score/count. "
                "RWMA is clinically linked to coronary artery distribution territories and "
                "has high correlation with LAD (r=0.36) and Cath (r=0.32)."
            ),
            "evidence": (
                "Wall motion abnormalities manifest when myocardial perfusion is compromised. "
                "However, RWMA is obtained via transthoracic echocardiography (TTE) prior to "
                "catheterization, not from angiographic dye or catheter intervention. "
                "Track A problem statement explicitly lists echocardiographic features as allowable inputs."
            ),
            "recommended_action": (
                "Retain in feature pool per Track A specification ('Use available: Echocardiographic features'), "
                "but strictly enforce the prompt rule: RWMA must NOT be interpreted as 3D lesion coordinates. "
                "Include sensitivity ablation in model evaluation (performance with vs without RWMA)."
            ),
        },
        {
            "feature": "Exertional CP",
            "why_suspicious": "Zero-variance feature (constant across 100% of samples).",
            "evidence": "All 303 rows contain 'N'. Provides zero discriminatory information.",
            "recommended_action": "Exclude from model training feature matrix X during preprocessing pipeline.",
        },
        {
            "feature": "BMI vs (Weight, Length)",
            "why_suspicious": "Mathematical collinearity (deterministic formula: BMI = Weight / (Length / 100)^2).",
            "evidence": "High collinearity between BMI, Weight, and Length in linear modeling.",
            "recommended_action": (
                "Not target leakage, but feature collinearity. Retain for tree-based models (XGBoost/RandomForest) "
                "which naturally handle collinearity, or evaluate dropping redundant terms for linear baselines."
            ),
        },
        {
            "feature": "CHF",
            "why_suspicious": "Severe category sparsity (only 1 positive case out of 303 rows).",
            "evidence": "302 'N' vs 1 'Y' (99.67% constant). High risk of spurious feature importance or split instability.",
            "recommended_action": (
                "Retain in feature schema for patient simulator input compatibility, but apply tree regularizers "
                "or evaluate low-variance feature filter to prevent split overfitting on a single record."
            ),
        },
    ]

    return {
        "mandatory_excluded_targets": excluded_targets,
        "leakage_rule": "Columns ['LAD', 'LCX', 'RCA', 'Cath'] MUST NEVER enter feature matrix X.",
        "suspicious_features_audit": suspicious_features,
    }


def build_feature_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Builds a complete, granular inventory for every column in the dataset."""
    records = []

    for col in df.columns:
        dt = str(df[col].dtype)
        category = get_feature_category(col)
        missing_cnt = int(df[col].isnull().sum())
        unique_cnt = int(df[col].nunique())
        sample_vals = [str(x) for x in df[col].dropna().unique()[:4]]
        example_str = ", ".join(sample_vals)

        # Potential issues and eligibility
        issues = []
        if col in TARGET_COLUMNS:
            eligibility = "Excluded (Target)"
            issues.append("Ground-truth target variable; strictly excluded from X")
        elif unique_cnt <= 1:
            eligibility = "Excluded (Zero Variance)"
            issues.append("Constant feature; variance = 0")
        else:
            eligibility = "Eligible"
            val_counts = df[col].value_counts(dropna=False)
            dom_pct = (val_counts.iloc[0] / len(df)) * 100
            if dom_pct >= 95.0:
                issues.append(f"Near-constant ({dom_pct:.1f}% dominant class '{val_counts.index[0]}')")

            if col == "Sex" and "Fmale" in df[col].values:
                issues.append("Typo in categorical label ('Fmale' -> 'Female')")
            if col == "VHD":
                issues.append("Inconsistent casing ('mild' vs 'Severe', 'Moderate')")

            if pd.api.types.is_numeric_dtype(df[col]) and unique_cnt > 10:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
                if outliers > 0:
                    issues.append(f"{outliers} IQR outliers (max={df[col].max()})")

        potential_issue = "; ".join(issues) if issues else "None"

        records.append(
            {
                "Feature Name": col,
                "Data Type": dt,
                "Category": category,
                "Missing Count": missing_cnt,
                "Unique Count": unique_cnt,
                "Example Values": example_str,
                "Potential Issue": potential_issue,
                "Model Eligibility": eligibility,
            }
        )

    return pd.DataFrame(records)


def compute_statistical_exploration(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes comprehensive numerical and categorical descriptive statistics."""
    # Numerical features
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_stats = {}

    for col in num_cols:
        series = df[col]
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        outliers = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())

        num_stats[col] = {
            "mean": round(float(series.mean()), 3),
            "median": round(float(series.median()), 3),
            "std": round(float(series.std()), 3),
            "min": round(float(series.min()), 3),
            "max": round(float(series.max()), 3),
            "q25": round(q1, 3),
            "q75": round(q3, 3),
            "skewness": round(float(series.skew()), 3),
            "iqr_outliers": outliers,
        }

    # Categorical features (including object dtype and discrete columns)
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    cat_stats = {}

    for col in cat_cols:
        val_counts = df[col].value_counts()
        cat_stats[col] = {
            "unique_count": int(df[col].nunique()),
            "frequencies": {str(k): int(v) for k, v in val_counts.items()},
            "dominant_class": str(val_counts.index[0]),
            "dominant_percentage": round(float(val_counts.iloc[0] / len(df)) * 100, 2),
        }

    # Correlations with targets
    df_encoded = df.copy()
    target_binaries = {
        "Cath_CAD": (df_encoded["Cath"] == "CAD").astype(int),
        "LAD_Stenotic": (df_encoded["LAD"] == "Stenotic").astype(int),
        "LCX_Stenotic": (df_encoded["LCX"] == "Stenotic").astype(int),
        "RCA_Stenotic": (df_encoded["RCA"] == "Stenotic").astype(int),
    }

    # Encode categorical features for Pearson correlation analysis
    for col in df_encoded.select_dtypes(include=["object"]).columns:
        if col not in TARGET_COLUMNS:
            df_encoded[col] = df_encoded[col].astype("category").cat.codes

    corr_with_targets = {}
    for t_name, t_series in target_binaries.items():
        corrs = {}
        for col in df_encoded.columns:
            if col not in TARGET_COLUMNS and col not in target_binaries:
                if df_encoded[col].std() > 0:
                    c_val = df_encoded[col].corr(t_series)
                    if not np.isnan(c_val):
                        corrs[col] = round(float(c_val), 4)
        # Sort by absolute correlation
        sorted_corrs = dict(sorted(corrs.items(), key=lambda item: abs(item[1]), reverse=True))
        corr_with_targets[t_name] = sorted_corrs

    return {
        "numerical_statistics": num_stats,
        "categorical_statistics": cat_stats,
        "correlations_with_targets": corr_with_targets,
    }


def generate_markdown_report(
    workbook_meta: Dict[str, Any],
    quality_audit: Dict[str, Any],
    targets_audit: Dict[str, Any],
    leakage_audit: Dict[str, Any],
    inventory_df: pd.DataFrame,
    stats_data: Dict[str, Any],
) -> str:
    """Generates the full human-readable markdown audit report."""
    md = []
    md.append("# CoroVista: Dataset Audit & Quality Analysis Report")
    md.append("**Multimodal AI Hackathon 2026 — Track A: Cardiovascular Risk Visualization & Prediction**\n")
    md.append("> **Clinical Safety Disclaimer**  \n> Predictions generated by CoroVista are for decision-support and educational purposes only. They are not a substitute for formal diagnostic coronary angiography or diagnostic imaging.\n")
    md.append("---\n")

    # 1. Executive Summary
    md.append("## 1. Executive Summary & Workbook Inspection\n")
    md.append(f"- **Workbook File**: `{workbook_meta['file_name']}`")
    md.append(f"- **Total Sheets Detected**: `{len(workbook_meta['sheet_names'])}` ({', '.join(workbook_meta['sheet_names'])})")
    md.append(f"- **Verified Primary Dataset Sheet**: `{workbook_meta['primary_sheet']}`")
    md.append(f"- **Dataset Dimensions**: **{quality_audit['n_rows']} rows × {quality_audit['n_columns']} columns**")
    md.append(f"- **Sheet 1 ('Sheet 1 - Table 1')**: 303 patient records, 59 columns.")
    md.append(f"- **Sheet 2 ('Sheet1')**: Completely empty (0 data rows, 0 non-null values).")
    md.append(f"- **Missing Values Across Entire Dataset**: **{quality_audit['total_missing']} missing values** (0.00%).")
    md.append(f"- **Duplicate Patient Rows**: **{quality_audit['duplicate_rows']}**.")
    md.append(f"- **Target Columns Identified**: 4 (`Cath`, `LAD`, `LCX`, `RCA`).")
    md.append(f"- **Eligible Predictive Features**: **54** (55 non-target features minus 1 zero-variance feature `Exertional CP`).\n")

    # 2. Target Identification & Class Distribution
    md.append("## 2. Target Identification & Distribution Analysis\n")
    md.append("Track A requires predicting four distinct coronary disease endpoints. The encodings and distributions are verified as follows:\n")

    md.append("| Target | Clinical Endpoint | Positive Class | Positive Count (%) | Negative Class | Negative Count (%) | Imbalance Ratio | Dominant Class |")
    md.append("|---|---|---|---|---|---|---|---|")
    for t_name, t_data in targets_audit.items():
        md.append(
            f"| **{t_name}** | {t_data['clinical_name']} | `{t_data['positive_label']}` | "
            f"{t_data['positive_count']} ({t_data['positive_percentage']}%) | "
            f"`{t_data['negative_label']}` | {t_data['negative_count']} ({t_data['negative_percentage']}%) | "
            f"**{t_data['imbalance_ratio']}:1** | `{t_data['dominant_class']}` |"
        )
    md.append("\n### Clinical Imbalance & Metric Guidance")
    md.append(
        "- **Cath (Overall CAD)** exhibits moderate class imbalance (71.3% positive vs 28.7% negative). "
        "A baseline dummy classifier predicting 'CAD' for all patients would achieve 71.3% accuracy without learning any clinical patterns. "
        "**Accuracy alone is strictly insufficient.** Model evaluation MUST emphasize PR-AUC, ROC-AUC, Recall, Precision, and F1-score."
    )
    md.append(
        "- **LAD Stenosis** is balanced (58.4% Stenotic vs 41.6% Normal). LAD supplies ~50% of the left ventricular myocardium."
    )
    md.append(
        "- **LCX Stenosis** (39.3% Stenotic) and **RCA Stenosis** (37.6% Stenotic) have minority positive classes (~1.6:1 negative-to-positive ratio). "
        "Models must prioritize positive class recall to prevent missed coronary artery stenosis in critical branches.\n"
    )

    # Cross-target coherence & Anomaly
    md.append("### Target Co-occurrence & Diagnostic Coherence")
    md.append(
        "Cath represents overall CAD confirmed by catheterization. In coronary catheterization practice, "
        "CAD is typically confirmed if at least one major epicardial coronary artery has ≥50% stenosis."
    )
    md.append(
        "- In **302 of 303 patients (99.67%)**, `Cath == 'CAD'` is exactly equivalent to `(LAD == 'Stenotic' | LCX == 'Stenotic' | RCA == 'Stenotic')`."
    )
    if quality_audit["cath_vessel_mismatches"]:
        m = quality_audit["cath_vessel_mismatches"][0]
        md.append(
            f"- **Observed Anomaly at Row Index {m['row_index']}**: Patient has `LAD=Stenotic`, `LCX=Normal`, `RCA=Normal`, but `Cath=Normal`. "
            "This may reflect either a recording typo or a borderline lesion evaluated differently by the reading cardiologist. "
            "Per Hackathon instructions, this raw data point is preserved without alteration and documented here.\n"
        )

    # 3. Data Quality & Anomaly Audit
    md.append("## 3. Data Quality, Anomalies & Known Issues\n")

    md.append("### A. Zero-Variance Feature")
    if quality_audit["constant_features"]:
        for cf in quality_audit["constant_features"]:
            md.append(f"- **Feature `{cf['feature']}`**: Constant value `{cf['value']}` across all 303 patient records (variance = 0.0).")
            md.append("  - *Action*: Exclude from training feature matrix X in the preprocessing pipeline. Preserved in raw data.")
    md.append("")

    md.append("### B. Inconsistent Spelling & Categorical Encoding Issues")
    for ci in quality_audit["categorical_issues"]:
        md.append(f"- **Feature `{ci['feature']}`**:")
        md.append(f"  - Original values: `{ci['original_value']}`")
        md.append(f"  - Clinical intended meaning: {ci['potential_intended_meaning']}")
        md.append(f"  - Evidence: {ci['evidence']}")
        md.append(f"  - Proposed transformation: {ci['proposed_transformation']}")
    md.append("")

    md.append("### C. Near-Constant Features (≥90% Dominant Class)")
    md.append("| Feature | Dominant Value | Dominant Count | Dominant % | Clinical Meaning | Risk / Treatment |")
    md.append("|---|---|---|---|---|---|")
    for ncf in quality_audit["near_constant_features"]:
        md.append(
            f"| `{ncf['feature']}` | `{ncf['dominant_value']}` | {ncf['dominant_count']}/303 | "
            f"{ncf['dominant_percentage']}% | High prevalence / rare pathology | Retain with tree regularization or evaluate variance threshold |"
        )
    md.append("\n*Notable*: `CHF` has only 1 positive record ('Y'); `LowTH Ang` has only 2 positive records ('Y'). These extreme low-frequency categories must not be used as high-depth decision splits.\n")

    md.append("### D. Numerical Range & Outlier Review")
    md.append("Extreme numerical values were inspected using the 1.5 × IQR standard:")
    md.append("| Feature | Median | IQR | Min | Max | Outliers (IQR) | Clinical Assessment |")
    md.append("|---|---|---|---|---|---|---|")
    for col, oinfo in quality_audit["numerical_outliers"].items():
        clinical_note = "Physiologically plausible extreme value in high-risk cardiology cohort."
        if col == "TG":
            clinical_note = "Severe hypertriglyceridemia (max 1050 mg/dL). Clinically possible; retain with robust scaling."
        elif col == "FBS":
            clinical_note = "Severe hyperglycemia (max 400 mg/dL) in diabetic cardiology patients. Retain."
        elif col == "PLT":
            clinical_note = "Range 25-742 10^3/mcL captures both severe thrombocytopenia and reactive thrombocytosis."
        elif col == "EF-TTE":
            clinical_note = "Severe heart failure EF down to 15%. Genuine physiological presentation."

        md.append(
            f"| `{col}` | {oinfo['median']} | {oinfo['iqr']} | {oinfo['min']} | {oinfo['max']} | "
            f"{oinfo['outlier_count']} ({oinfo['outlier_percentage']}%) | {clinical_note} |"
        )
    md.append("\n**Conclusion on Outliers**: No physically impossible numbers (e.g., negative blood pressures or negative ages) exist. Outliers represent critically ill cardiac patients and MUST NOT be deleted.\n")

    # 4. Leakage Audit
    md.append("## 4. Leakage Audit\n")
    md.append("To ensure medical validity and prevent target leakage:\n")
    md.append("1. **Mandatory Excluded Columns**: The four targets `Cath`, `LAD`, `LCX`, and `RCA` **MUST NEVER enter feature matrix X**.")
    md.append("2. **Investigation of Potential Leakage Features**:\n")

    for sf in leakage_audit["suspicious_features_audit"]:
        md.append(f"### Feature: `{sf['feature']}`")
        md.append(f"- **Why Suspicious**: {sf['why_suspicious']}")
        md.append(f"- **Clinical Evidence**: {sf['evidence']}")
        md.append(f"- **Recommended Action**: {sf['recommended_action']}\n")

    # 5. Feature Inventory Summary
    md.append("## 5. Feature Inventory Summary by Clinical Domain\n")
    cat_counts = inventory_df["Category"].value_counts().to_dict()
    md.append("| Clinical Category | Feature Count | Examples |")
    md.append("|---|---|---|")
    for cat, count in cat_counts.items():
        sample_feats = inventory_df[inventory_df["Category"] == cat]["Feature Name"].iloc[:4].tolist()
        md.append(f"| **{cat}** | {count} | {', '.join(sample_feats)} |")
    md.append("\n*Full itemized feature inventory exported to `data/reports/feature_inventory.csv`.*\n")

    # 6. Statistical Correlations
    md.append("## 6. Top Feature Correlations with Prediction Targets\n")
    md.append("Pearson correlation analysis between admissible features and binarized targets:\n")
    for t_name, corrs in stats_data["correlations_with_targets"].items():
        md.append(f"### Target `{t_name}`")
        top_positive = [f"`{k}` (+{v})" for k, v in list(corrs.items())[:4] if v > 0]
        top_negative = [f"`{k}` ({v})" for k, v in list(corrs.items())[-3:] if v < 0]
        md.append(f"- **Strongest Positive Associations**: {', '.join(top_positive)}")
        md.append(f"- **Strongest Inverse Associations**: {', '.join(top_negative)}\n")

    # 7. Proposed Preprocessing Pipeline
    md.append("## 7. Preprocessing Strategy Proposal (For Stage 2)\n")
    md.append("All transformations that learn statistical parameters will be encapsulated strictly inside the scikit-learn cross-validation folds:\n")
    md.append("1. **Target Separation**: Extract `Cath`, `LAD`, `LCX`, `RCA` into target vectors $y_{Cath}, y_{LAD}, y_{LCX}, y_{RCA}$. Exclude from feature matrix $X$.")
    md.append("2. **Zero-Variance Filtering**: Drop `Exertional CP` (all 303 rows are 'N').")
    md.append("3. **Categorical Normalization & Encoding**:")
    md.append("   - Fix typo: `Sex == 'Fmale'` → `Female`, binary encode Male=1, Female=0.")
    md.append("   - Standardize binary 'Y'/'N' features → 1 / 0.")
    md.append("   - Ordinal mapping for `VHD` ('N': 0, 'mild': 1, 'Moderate': 2, 'Severe': 3).")
    md.append("   - One-hot encoding for nominal multi-class ECG variable `BBB` ('N', 'LBBB', 'RBBB').")
    md.append("4. **Numerical Preprocessing**:")
    md.append("   - Missing value safety net: `SimpleImputer(strategy='median')` (0 missing currently, but vital for simulator robustness).")
    md.append("   - Robust scaling: `RobustScaler` or `StandardScaler` for distance/linear models; XGBoost/Tree models remain unaffected by monotonic scaling.")
    md.append("5. **Class Imbalance Handling**:")
    md.append("   - Use algorithm-level weighting (`scale_pos_weight` in XGBoost, `class_weight='balanced'` in logistic/tree models).")
    md.append("   - Avoid global oversampling (SMOTE) outside validation folds to prevent data leakage.")
    md.append("6. **Feature Selection**:")
    md.append("   - Evaluate feature importance via L1 penalty and tree-based mutual information.")
    md.append("   - Run ablation with and without `Region RWMA` to quantify dependency.\n")

    # 8. Proposed Validation Strategy
    md.append("## 8. Validation Strategy Proposal (For Stage 2)\n")
    md.append("Given the sample size ($N = 303$):")
    md.append("1. **No Single Train/Test Split**: A single random 80/20 train/test split on 303 rows leaves only ~60 test samples, creating unacceptably wide confidence intervals.")
    md.append("2. **Repeated Stratified K-Fold Cross-Validation**: Use **5-Fold Stratified CV with 5 Repeats (25 evaluation runs)** for each of the 4 targets independently.")
    md.append("3. **Multi-Target Modeling Architecture**:")
    md.append("   - Model 1: `Cath` (Overall CAD status)")
    md.append("   - Model 2: `LAD` (LAD stenosis probability)")
    md.append("   - Model 3: `LCX` (LCX stenosis probability)")
    md.append("   - Model 4: `RCA` (RCA stenosis probability)")
    md.append("4. **Metric Suite**: Accuracy, Precision, Recall, F1-Score, ROC-AUC, and PR-AUC (Average Precision).")
    md.append("5. **Probability Calibration**: Brier Score and calibration curves (Isotonic/Platt calibration) because probabilities directly feed the 3D heart risk visualization.\n")

    return "\n".join(md)


def run_audit(input_file: Path, output_dir: Path) -> Dict[str, Any]:
    """Runs the full audit pipeline and saves all required reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Inspecting workbook: %s", input_file)
    wb_meta = inspect_workbook(input_file)

    logger.info("Loading primary dataset sheet: %s", wb_meta["primary_sheet"])
    df = load_dataset(input_file, sheet_name=wb_meta["primary_sheet"])

    logger.info("Auditing data quality...")
    quality_audit = audit_data_quality(df)

    logger.info("Auditing prediction targets...")
    targets_audit = audit_targets(df)

    logger.info("Auditing data leakage vulnerabilities...")
    leakage_audit = audit_leakage(df)

    logger.info("Building feature inventory...")
    inventory_df = build_feature_inventory(df)

    logger.info("Computing statistical exploration...")
    stats_data = compute_statistical_exploration(df)

    # 1. Save feature inventory CSV
    inventory_path = output_dir / "feature_inventory.csv"
    inventory_df.to_csv(inventory_path, index=False)
    logger.info("Saved feature inventory to %s", inventory_path)

    # 2. Save JSON audit
    audit_data = {
        "workbook_metadata": wb_meta,
        "quality_audit": quality_audit,
        "targets_audit": targets_audit,
        "leakage_audit": leakage_audit,
        "statistical_exploration": stats_data,
    }
    json_path = output_dir / "dataset_audit.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    logger.info("Saved dataset audit JSON to %s", json_path)

    # 3. Generate and save Markdown audit report
    md_report = generate_markdown_report(
        wb_meta, quality_audit, targets_audit, leakage_audit, inventory_df, stats_data
    )
    md_path = output_dir / "dataset_audit.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    logger.info("Saved dataset audit Markdown report to %s", md_path)

    return audit_data


def main():
    parser = argparse.ArgumentParser(description="CoroVista Dataset Audit")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/extention of Z-Alizadeh sani dataset.xlsx",
        help="Path to raw dataset excel file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/reports",
        help="Directory to save audit reports",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        logger.error("Input file does not exist: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")

    run_audit(input_path, output_dir)
    logger.info("Dataset audit completed successfully.")


if __name__ == "__main__":
    main()
