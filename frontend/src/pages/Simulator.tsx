import React, { useState, useCallback, useMemo } from "react"
import {
  Sliders,
  Sparkles,
  Info,
  Play,
  CheckCircle2,
  FileQuestion,
} from "lucide-react"
import { apiClient, ApiError } from "@/api/client"
import type { AnalysisResponse, PatientRecord } from "@/types/patient"
import type { TargetName } from "@/types/prediction"
import { DEMO_PATIENT } from "@/lib/demoPatient"
import { validatePatientRecord } from "@/lib/simulatorRegistry"
import { SimulatorForm } from "@/components/simulator/SimulatorForm"
import { SimulatorActions } from "@/components/simulator/SimulatorActions"
import { SimulatorStatus } from "@/components/simulator/SimulatorStatus"
import { AnalysisResults } from "@/components/simulator/AnalysisResults"

export const Simulator: React.FC = () => {
  // 1. Form state: editable clinical features
  const [formData, setFormData] = useState<PatientRecord>({ ...DEMO_PATIENT })
  const [lastSubmittedData, setLastSubmittedData] = useState<PatientRecord | null>(null)

  // 2. Analysis state: latest and previous successful responses
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null)
  const [previousAnalysis, setPreviousAnalysis] = useState<AnalysisResponse | null>(null)

  // 3. UI interaction state
  const [selectedTarget, setSelectedTarget] = useState<TargetName>("cath")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [fieldWarnings, setFieldWarnings] = useState<Record<string, string>>({})

  // Determine if form has unsaved/unsent edits compared to last analysis
  const isDirty = useMemo(() => {
    if (!lastSubmittedData) return false
    return JSON.stringify(formData) !== JSON.stringify(lastSubmittedData)
  }, [formData, lastSubmittedData])

  // Handle individual field updates
  const handleFieldChange = useCallback((name: string, value: string | number) => {
    setFormData((prev) => {
      const next = { ...prev, [name]: value }

      // Also automatically re-calculate BMI if Weight or Length is modified
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
    // 1. Validate form fields
    const { isValid, errors, warnings } = validatePatientRecord(formData)
    setFieldErrors(errors)
    setFieldWarnings(warnings)

    if (!isValid) {
      setError(
        new ApiError(
          "Please review and correct invalid or missing clinical fields before submitting.",
          "VALIDATION_ERROR",
          400
        )
      )
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Call authoritative backend endpoint POST /api/v1/analyze
      const res = await apiClient.analyzePatient(formData)

      // Shift previous analysis if a current analysis exists
      if (currentAnalysis) {
        setPreviousAnalysis(currentAnalysis)
      }

      setCurrentAnalysis(res)
      setLastSubmittedData({ ...formData })
      setError(null)
    } catch (err) {
      // Preserve previous analysis intact on failure!
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
    // Keep empty template
    const emptyRecord: PatientRecord = {}
    for (const key of Object.keys(DEMO_PATIENT)) {
      emptyRecord[key] = ""
    }
    setFormData(emptyRecord)
    setFieldErrors({})
    setFieldWarnings({})
  }, [])

  return (
    <div className="space-y-6 max-w-[1536px] w-full mx-auto px-1 sm:px-2" role="region" aria-label="Patient Simulator Workspace">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/60 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xs">
              <Sliders className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-foreground">
              Patient Simulator
            </h1>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="w-3 h-3" />
              <span>Educational / Decision-Support Simulation</span>
            </span>
          </div>

          <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
            Explore how clinical inputs influence model-predicted cardiovascular risk.
          </p>
        </div>

        {/* Compact Clinical Disclaimer Badge */}
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/40 border border-border/50 text-[11px] text-muted-foreground self-start sm:self-auto"
          role="note"
        >
          <Info className="w-3.5 h-3.5 text-primary shrink-0" />
          <span>
            <strong className="text-foreground/90 font-medium">Research Prototype:</strong> Model exploration only. Not a formal medical diagnosis.
          </span>
        </div>
      </div>

      {/* Main Workspace: 2-Column Responsive Split */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Column: Clinical Input Form (xl:col-span-5) */}
        <div className="xl:col-span-5 2xl:col-span-5 space-y-4">
          {/* Action Toolbar */}
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

          {/* Status & Feedback */}
          <SimulatorStatus
            isLoading={isLoading}
            isStale={isDirty && Boolean(currentAnalysis)}
            error={error}
            onRetry={handleAnalyze}
          />

          {/* 4-Category Clinical Form */}
          <SimulatorForm
            values={formData}
            onChange={handleFieldChange}
            errors={fieldErrors}
            warnings={fieldWarnings}
            disabled={isLoading}
          />
        </div>

        {/* Right Column: Live Synchronized Results (xl:col-span-7) */}
        <div className="xl:col-span-7 2xl:col-span-7 space-y-6 min-w-0">
          {!currentAnalysis ? (
            /* Initial Empty State */
            <div
              className="border border-border/80 bg-card rounded-xl p-8 text-center flex flex-col items-center justify-center min-h-[440px] space-y-4 shadow-sm"
              role="region"
              aria-label="Simulation Results Empty State"
            >
              <div className="w-14 h-14 rounded-2xl bg-secondary/80 border border-border flex items-center justify-center text-primary shadow-xs">
                <FileQuestion className="w-7 h-7" />
              </div>

              <div className="max-w-md space-y-1.5">
                <h3 className="text-base font-semibold text-foreground">
                  No Active Simulation Results
                </h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Configure patient baseline parameters on the left and click <strong>&ldquo;Analyze Patient&rdquo;</strong> to evaluate multi-target risk predictions, SHAP feature attributions, and 3D coronary anatomy visualization.
                </p>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={isLoading}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm cursor-pointer transition-colors"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run Initial Analysis (Demo Profile)</span>
                </button>
              </div>

              <div className="pt-4 border-t border-border/40 w-full max-w-sm text-left">
                <span className="text-[11px] font-medium text-foreground block mb-2">
                  Simulation Workflow Capabilities:
                </span>
                <ul className="text-xs text-muted-foreground space-y-1.5">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    <span>Four independent ML endpoints (Cath, LAD, LCX, RCA)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    <span>Continuous 3D coronary risk color mapping</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    <span>Local TreeSHAP log-odds feature attribution breakdown</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    <span>Consecutive run before/after sensitivity comparison</span>
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            /* Live Synchronized Results */
            <AnalysisResults
              analysis={currentAnalysis}
              previousAnalysis={previousAnalysis}
              selectedTarget={selectedTarget}
              onSelectTarget={setSelectedTarget}
            />
          )}
        </div>
      </div>
    </div>
  )
}
