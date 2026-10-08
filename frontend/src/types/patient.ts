import type { PredictionResponse } from "./prediction"
import type { ExplanationResponse } from "./explanation"

export type PatientRecord = Record<string, string | number | boolean>

export interface AnalysisResponse {
  predictions: PredictionResponse["predictions"]
  explanations: {
    cath: ExplanationResponse
    lad: ExplanationResponse
    lcx: ExplanationResponse
    rca: ExplanationResponse
  }
  clinical_disclaimer: string
  visualization_note: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
  models_loaded: boolean
}

export interface FeatureRange {
  min: number
  max: number
  step?: number
}

export interface FeatureMetadataItem {
  machine_name: string
  human_readable_label: string
  type: "numeric" | "binary" | "categorical"
  category: "Demographic" | "Symptoms / Examination" | "ECG" | "Laboratory / Echo"
  allowed_values: string[] | null
  dataset_observed_range: string | null
  simulator_validation_range: FeatureRange | null
  is_required: boolean
  description: string | null
}

export interface FeaturesResponse {
  features: FeatureMetadataItem[]
  total_features: number
}

export interface ApiErrorEnvelope {
  error: {
    code: string
    message: string
    details?: Array<Record<string, unknown>>
  }
}
