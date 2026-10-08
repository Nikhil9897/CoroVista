import { useState, useEffect, useCallback } from "react"
import { apiClient, ApiError } from "@/api/client"
import type { AnalysisResponse, HealthResponse, ModelsResponse, PatientRecord } from "@/api/types"
import { DEMO_PATIENT } from "@/lib/demoPatient"

export function usePatientAnalysis() {
  const [patient, setPatient] = useState<PatientRecord | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [models, setModels] = useState<ModelsResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<ApiError | null>(null)

  // Initial health and model metadata check
  const fetchSystemStatus = useCallback(async () => {
    try {
      const [hRes, mRes] = await Promise.all([
        apiClient.getHealth(),
        apiClient.getModels().catch(() => null),
      ])
      setHealth(hRes)
      if (mRes) setModels(mRes)
    } catch (err) {
      if (err instanceof ApiError) {
        setHealth({
          status: "degraded",
          service: "corovista-api",
          version: "unknown",
          models_loaded: false,
        })
      }
    }
  }, [])

  useEffect(() => {
    let isMounted = true
    const check = async () => {
      try {
        const [hRes, mRes] = await Promise.all([
          apiClient.getHealth(),
          apiClient.getModels().catch(() => null),
        ])
        if (isMounted) {
          setHealth(hRes)
          if (mRes) setModels(mRes)
        }
      } catch (err) {
        if (isMounted && err instanceof ApiError) {
          setHealth({
            status: "degraded",
            service: "corovista-api",
            version: "unknown",
            models_loaded: false,
          })
        }
      }
    }
    void check()
    return () => {
      isMounted = false
    }
  }, [])

  const analyze = useCallback(async (data: PatientRecord) => {
    setIsLoading(true)
    setError(null)
    try {
      setPatient(data)
      const res = await apiClient.analyzePatient(data)
      setAnalysis(res)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err)
      } else {
        setError(new ApiError("An unexpected error occurred", "UNKNOWN_ERROR", 500))
      }
      setAnalysis(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadDemoPatient = useCallback(async () => {
    await analyze(DEMO_PATIENT)
  }, [analyze])

  const clearPatient = useCallback(() => {
    setPatient(null)
    setAnalysis(null)
    setError(null)
  }, [])

  return {
    patient,
    analysis,
    health,
    models,
    isLoading,
    error,
    analyze,
    loadDemoPatient,
    clearPatient,
    refetchSystemStatus: fetchSystemStatus,
  }
}
