import type { TargetName } from "./prediction"

export interface FeatureContributionItem {
  feature: string
  label: string
  value: number
  shap_value: number
  direction: "positive" | "negative"
}

export interface ExplanationResponse {
  target: TargetName
  explanation_space: string
  calibration_disclosure: string
  base_value: number
  features: FeatureContributionItem[]
  positive_contributors: FeatureContributionItem[]
  negative_contributors: FeatureContributionItem[]
}
