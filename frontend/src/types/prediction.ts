export type TargetName = "cath" | "lad" | "lcx" | "rca"

export interface TargetPrediction {
  probability: number
  prediction: string
  threshold: number
  model_family?: string
  calibration?: string
}

export interface PredictionResponse {
  predictions: {
    cath: TargetPrediction
    lad: TargetPrediction
    lcx: TargetPrediction
    rca: TargetPrediction
  }
}

export interface ModelMetadataItem {
  target: TargetName
  model: string
  calibrated: boolean
  calibration: string
  threshold: number
  positive_label: string
  negative_label: string
  explanation_space: string
  version?: string
}

export interface ModelsResponse {
  models: ModelMetadataItem[]
}
