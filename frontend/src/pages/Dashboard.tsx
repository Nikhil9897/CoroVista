import React, { useState, Suspense, lazy } from "react"
import { usePatientAnalysis } from "@/hooks/usePatientAnalysis"
import type { TargetName } from "@/types/prediction"
import { PatientSummaryHeader } from "@/components/dashboard/PatientSummaryHeader"
import { CadRiskCard } from "@/components/predictions/CadRiskCard"
import { VesselRiskOverview } from "@/components/predictions/VesselRiskOverview"
import { ViewerLoadingFallback } from "@/components/viewer/ViewerLoadingFallback"
import { ExplanationPanel } from "@/components/explanations/ExplanationPanel"
import { EmptyState } from "@/components/common/EmptyState"
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner"

const CoronaryViewer = lazy(() =>
  import("@/components/viewer/CoronaryViewer").then((m) => ({ default: m.CoronaryViewer }))
)

export const Dashboard: React.FC = () => {
  const {
    patient,
    analysis,
    isLoading,
    error,
    loadDemoPatient,
    clearPatient,
    analyze,
  } = usePatientAnalysis()

  const [selectedTarget, setSelectedTarget] = useState<TargetName>("cath")

  return (
    <div className="min-h-[calc(100vh-44px)]" role="region" aria-label="Clinical Risk Dashboard">
      {/* Error Banner */}
      {error && (
        <div className="px-4 lg:px-6 pt-3">
          <ErrorAlert
            error={error}
            onRetry={patient ? () => analyze(patient) : loadDemoPatient}
          />
        </div>
      )}

      {/* Main Content Area: Loading vs Empty vs Results */}
      {isLoading ? (
        <div className="px-4 lg:px-6 py-6">
          <LoadingSkeleton />
        </div>
      ) : !analysis ? (
        <div className="px-4 lg:px-6 py-6 max-w-7xl mx-auto space-y-6">
          <PatientSummaryHeader
            patient={patient}
            isLoading={isLoading}
            onLoadDemo={loadDemoPatient}
            onClear={clearPatient}
          />
          <div className="mt-4">
            <EmptyState onLoadDemo={loadDemoPatient} isLoading={isLoading} />
          </div>
        </div>
      ) : (
      ) : (
        /* ── Clinical Anatomy-Led Workstation Layout ── */
        <div className="spatial-fade-up px-4 lg:px-6 py-4 max-w-[1600px] mx-auto space-y-5">
          {/* Header Row: Patient Profile Bar */}
          <PatientSummaryHeader
            patient={patient}
            isLoading={isLoading}
            onLoadDemo={loadDemoPatient}
            onClear={clearPatient}
            className="glass-panel shadow-spatial"
          />

          {/* Primary Workstation Split: Clinical Risk Panels (Left) + 3D Anatomy (Right) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
            {/* Left Column: Multi-Target Risk Synthesis */}
            <div className="lg:col-span-5 xl:col-span-4 flex flex-col justify-between space-y-4">
              <div className="spatial-fade-up">
                <CadRiskCard
                  prediction={analysis.predictions.cath}
                  className="glass-panel shadow-spatial"
                />
              </div>

              <div className="spatial-fade-up" style={{ animationDelay: "0.1s" }}>
                <VesselRiskOverview
                  predictions={analysis.predictions}
                  selectedTarget={selectedTarget}
                  onSelectTarget={(target) => setSelectedTarget(target)}
                />
              </div>
            </div>

            {/* Right Column: Hero 3D Coronary Anatomy Viewport */}
            <div className="lg:col-span-7 xl:col-span-8 flex flex-col">
              <div
                className="relative rounded-2xl overflow-hidden border border-border/70 shadow-spatial-lg bg-surface-0 flex-1 min-h-[520px] lg:min-h-[580px] xl:min-h-[640px]"
              >
                <Suspense fallback={<ViewerLoadingFallback className="h-full w-full rounded-none border-0" />}>
                  <CoronaryViewer
                    predictions={analysis.predictions}
                    selectedTarget={selectedTarget}
                    onSelectTarget={(target) => setSelectedTarget(target)}
                    className="h-full w-full rounded-none border-0"
                  />
                </Suspense>
              </div>
            </div>
          </div>

          {/* Bottom Section: Local SHAP Feature Explanations */}
          <div className="spatial-fade-up pt-1" style={{ animationDelay: "0.15s" }}>
            <ExplanationPanel
              explanations={analysis.explanations}
              selectedTarget={selectedTarget}
              onSelectTarget={(target) => setSelectedTarget(target)}
            />
          </div>

          <DisclaimerBanner className="mt-2" />
        </div>
      )}
    </div>
  )
}
