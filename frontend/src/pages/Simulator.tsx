import React, { useState, useCallback, useMemo } from "react"
import { Play, Sparkles } from "lucide-react"
import { apiClient, ApiError } from "@/api/client"
import type { AnalysisResponse, PatientRecord } from "@/types/patient"
import type { TargetName } from "@/types/prediction"
import { DEMO_PATIENT } from "@/lib/demoPatient"
import { validatePatientRecord } from "@/lib/simulatorRegistry"
import { SimulatorForm } from "@/components/simulator/SimulatorForm"
import { SimulatorActions } from "@/components/simulator/SimulatorActions"
import { SimulatorStatus } from "@/components/simulator/SimulatorStatus"
import { SimulatorResultPanel } from "@/components/simulator/SimulatorResultPanel"

export const Simulator: React.FC = () => {
  // 1. Form state: editable clinical features
  const [formData, setFormData] = useState<PatientRecord>({ ...DEMO_PATIENT })
  const [lastSubmittedData, setLastSubmittedData] = useState<PatientRecord | null>(null)

  // 2. Analysis state: latest and previous responses
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null)
  const [previousAnalysis, setPreviousAnalysis] = useState<AnalysisResponse | null>(null)

  // 3. UI interaction state
  const [selectedTarget, setSelectedTarget] = useState<TargetName>("cath")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [fieldWarnings, setFieldWarnings] = useState<Record<string, string>>({})

  // Determine if form has unsent edits
  const isDirty = useMemo(() => {
    if (!lastSubmittedData) return false
    return JSON.stringify(formData) !== JSON.stringify(lastSubmittedData)
  }, [formData, lastSubmittedData])

  // Handle individual field updates
  const handleFieldChange = useCallback((name: string, value: string | number) => {
    setFormData((prev) => {
      const next = { ...prev, [name]: value }

      // Automatically re-calculate BMI if Weight or Length is modified
      if (name === "Weight" || name === "Length") {
        const wt = name === "Weight" ? Number(value) : Number(prev.Weight)
        const len = name === "Length" ? Number(value) : Number(prev.Length)
        if (wt > 0 && len > 0) {
          const heightM = len / 100
          next.BMI = Number((wt / (heightM * heightM)).toFixed(2))
        }
      }
      return next
    })

    // Clear field-level error on change
    setFieldErrors((prev) => {
      if (!prev[name]) return prev
      const next = { ...prev }
      delete next[name]
      return next
    })
  }, [])

  // Execute Analysis via API
  const handleAnalyze = useCallback(async () => {
    const { isValid, errors, warnings } = validatePatientRecord(formData)
    setFieldErrors(errors)
    setFieldWarnings(warnings)

    if (!isValid) {
      setError(
        new ApiError(
          "Please review and correct invalid clinical fields before submitting.",
          "VALIDATION_ERROR",
          400
        )
      )
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const res = await apiClient.analyzePatient(formData)
      if (currentAnalysis) {
        setPreviousAnalysis(currentAnalysis)
      }
      setCurrentAnalysis(res)
      setLastSubmittedData({ ...formData })
      setError(null)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err)
      } else {
        setError(
          new ApiError(
            "An unexpected error occurred while communicating with the CoroVista API service.",
            "UNKNOWN_ERROR",
            500
          )
        )
      }
    } finally {
      setIsLoading(false)
    }
  }, [formData, currentAnalysis])

  // Reset to Demo Values
  const handleResetDemo = useCallback(() => {
    setFormData({ ...DEMO_PATIENT })
    setFieldErrors({})
    setFieldWarnings({})
    setError(null)
  }, [])

  // Clear Form
  const handleClearForm = useCallback(() => {
    const emptyRecord: PatientRecord = {}
    for (const key of Object.keys(DEMO_PATIENT)) {
      emptyRecord[key] = ""
    }
    setFormData(emptyRecord)
    setFieldErrors({})
    setFieldWarnings({})
  }, [])

  return (
    <div
      className="min-h-[calc(100vh-44px)] clinical-instrument px-4 lg:px-8 py-6 max-w-[1600px] w-full mx-auto space-y-6"
      role="region"
      aria-label="Patient Simulator Workspace"
    >
      {/* Calm Header: Serif title + one quiet subtitle line */}
      <div className="pb-3 border-b border-[#7C9692]/15">
        <h1 className="font-display text-3xl sm:text-4xl text-[#E8F1EE] tracking-tight">
          Patient Simulator
        </h1>
        <p className="text-xs text-[#7C9692] mt-1 leading-relaxed">
          Simulate coronary disease risk trajectories and observe real-time 3D anatomical vessel responses. Explore how clinical inputs influence model-predicted cardiovascular risk.
        </p>
      </div>

      {/* Main 2-Column Responsive Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (≈40%): Patient inputs */}
        <div className="lg:col-span-5 space-y-4">
          <SimulatorActions
            onAnalyze={handleAnalyze}
            onLoadDemo={handleResetDemo}
            onResetDemo={handleResetDemo}
            onClearForm={handleClearForm}
            isLoading={isLoading}
            isDirty={isDirty}
            hasResults={Boolean(currentAnalysis)}
            hasErrors={Object.keys(fieldErrors).length > 0}
          />

          <SimulatorStatus
            isLoading={isLoading}
            isStale={isDirty && Boolean(currentAnalysis)}
            error={error}
            onRetry={handleAnalyze}
          />

          <SimulatorForm
            values={formData}
            onChange={handleFieldChange}
            errors={fieldErrors}
            warnings={fieldWarnings}
            disabled={isLoading}
          />
        </div>

        {/* Right Column (≈60%): Sticky Live Result + 3D Model */}
        <div className="lg:col-span-7 lg:sticky lg:top-14 space-y-4 min-w-0">
          {!currentAnalysis ? (
            /* Initial Empty State */
            <div
              className="instrument-surface rounded-2xl p-8 sm:p-12 text-center flex flex-col items-center justify-center min-h-[500px] space-y-4 select-none"
              role="region"
              aria-label="Simulation Results Empty State"
            >
              <div className="relative mb-2">
                <div className="w-16 h-16 rounded-2xl bg-[#0A1514] border border-[#7C9692]/20 flex items-center justify-center text-[#F26F69] shadow-lg">
                  <Sparkles className="w-8 h-8" />
                </div>
              </div>

              <div className="max-w-md space-y-1.5">
                <h3 className="font-display text-2xl text-[#E8F1EE] tracking-tight">
                  No Active Simulation Results
                </h3>
                <p className="text-xs text-[#7C9692] leading-relaxed">
                  Adjust clinical variables on the left and click <strong>&ldquo;Analyze patient&rdquo;</strong> to calculate multi-target risk predictions, SHAP feature attributions, and in-scene 3D coronary anatomy visualization.
                </p>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={isLoading}
                  className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full text-xs font-semibold bg-[#F26F69] hover:bg-[#F26F69]/90 text-[#0A1514] shadow-md transition-all active:scale-95 cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Analyze demo patient profile</span>
                </button>
              </div>

              <p className="pt-4 text-[11px] font-mono text-[#7C9692]/50">
                Four independent machine-learning endpoints: Cath &bull; LAD &bull; LCX &bull; RCA
              </p>
            </div>
          ) : (
            /* Live Synchronized Result Panel */
            <SimulatorResultPanel
              analysis={currentAnalysis}
              previousAnalysis={previousAnalysis}
              selectedTarget={selectedTarget}
              onSelectTarget={setSelectedTarget}
            />
          )}
        </div>
      </div>

      {/* Single quiet disclaimer footer */}
      <footer className="pt-8 pb-4 text-center">
        <p className="text-[11px] text-[#7C9692]/60 font-normal">
          <strong className="text-[#E8F1EE]/70 font-medium">Educational / Decision-Support Simulation:</strong> Model exploration only. Not a formal medical diagnosis.
        </p>
      </footer>
    </div>
  )
}
