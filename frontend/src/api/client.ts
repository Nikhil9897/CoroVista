import type {
  AnalysisResponse,
  ApiErrorEnvelope,
  ExplanationResponse,
  FeaturesResponse,
  HealthResponse,
  ModelsResponse,
  PatientRecord,
  PredictionResponse,
  TargetName,
} from "./types"

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export class ApiError extends Error {
  public code: string
  public status: number
  public details?: Array<Record<string, unknown>>

  constructor(message: string, code: string, status: number, details?: Array<Record<string, unknown>>) {
    super(message)
    this.name = "ApiError"
    this.code = code
    this.status = status
    this.details = details
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  }

  let response: Response
  try {
    response = await fetch(url, { ...options, headers })
  } catch {
    throw new ApiError(
      "Unable to connect to CoroVista API service. Please verify backend is running.",
      "NETWORK_ERROR",
      0
    )
  }

  if (!response.ok) {
    let errorEnvelope: ApiErrorEnvelope | null = null
    try {
      errorEnvelope = await response.json()
    } catch {
      // Non-JSON response
    }

    const message =
      errorEnvelope?.error?.message ||
      `HTTP error ${response.status}: ${response.statusText}`
    const code = errorEnvelope?.error?.code || "HTTP_ERROR"
    const details = errorEnvelope?.error?.details

    throw new ApiError(message, code, response.status, details)
  }

  return response.json()
}

export const apiClient = {
  getHealth: (): Promise<HealthResponse> => {
    return request<HealthResponse>("/api/v1/health")
  },

  getModels: (): Promise<ModelsResponse> => {
    return request<ModelsResponse>("/api/v1/models")
  },

  getFeatures: (): Promise<FeaturesResponse> => {
    return request<FeaturesResponse>("/api/v1/features")
  },

  predictPatient: (patient: PatientRecord): Promise<PredictionResponse> => {
    return request<PredictionResponse>("/api/v1/predict", {
      method: "POST",
      body: JSON.stringify({ patient }),
    })
  },

  explainPatient: (patient: PatientRecord, target: TargetName = "cath"): Promise<ExplanationResponse> => {
    return request<ExplanationResponse>("/api/v1/explain", {
      method: "POST",
      body: JSON.stringify({ patient, target }),
    })
  },

  analyzePatient: (patient: PatientRecord): Promise<AnalysisResponse> => {
    return request<AnalysisResponse>("/api/v1/analyze", {
      method: "POST",
      body: JSON.stringify({ patient }),
    })
  },
}
