import React, { useState, Suspense, lazy } from "react"
import { useNavigate } from "react-router-dom"
import { RefreshCw, Trash2, User, ShieldCheck } from "lucide-react"
import { usePatientAnalysis } from "@/hooks/usePatientAnalysis"
import type { TargetName } from "@/types/prediction"
import { DashboardEmptyState } from "@/components/dashboard/DashboardEmptyState"
import { DashboardHero } from "@/components/dashboard/DashboardHero"
import { VesselRiskRow } from "@/components/dashboard/VesselRiskRow"
import { ShapDriversChart } from "@/components/dashboard/ShapDriversChart"
import { ViewerLoadingFallback } from "@/components/viewer/ViewerLoadingFallback"
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { DEMO_PATIENT_METADATA } from "@/lib/demoPatient"

const CoronaryViewer = lazy(() =>
  import("@/components/viewer/CoronaryViewer").then((m) => ({ default: m.CoronaryViewer }))
)

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()
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
  const [hoveredTarget, setHoveredTarget] = useState<TargetName | null>(null)

  // Use hovered target if present, otherwise selectedTarget for 3D emphasis
  const effectiveTarget = hoveredTarget || selectedTarget

  return (
    <div
      className="min-h-[calc(100vh-44px)] clinical-instrument"
      role="region"
      aria-label="Clinical Risk Dashboard"
    >
      {/* Error Alert */}
      {error && (
        <div className="px-4 lg:px-8 pt-4 max-w-7xl mx-auto">
          <ErrorAlert
            error={error}
            onRetry={patient ? () => analyze(patient) : loadDemoPatient}
          />
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading ? (
        <div className="px-4 lg:px-8 py-8 max-w-7xl mx-auto">
          <LoadingSkeleton />
        </div>
      ) : !analysis ? (
        /* Empty State: ONE Centered Composition */
        <DashboardEmptyState onLoadDemo={loadDemoPatient} isLoading={isLoading} />
      ) : (
        /* Loaded State: Quiet Clinical Instrument Hierarchy */
        <div className="spatial-fade-up px-4 lg:px-8 py-6 max-w-[1600px] mx-auto space-y-6">
          {/* Patient Profile Bar */}
          <div className="instrument-surface rounded-2xl px-5 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-[#162C2A] border border-[#7C9692]/20 flex items-center justify-center text-[#F26F69] shrink-0">
                <User className="w-4 h-4" />
              </div>
              <div className="flex items-center gap-2.5 flex-wrap">
                <span className="font-semibold text-[#E8F1EE] tracking-tight">
                  {DEMO_PATIENT_METADATA.label}
                </span>
                <span className="text-[#7C9692]/40">&bull;</span>
                <span className="text-[#7C9692]">
                  {DEMO_PATIENT_METADATA.type}
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#162C2A] text-[#2dd4bf] border border-[#7C9692]/20">
                  <ShieldCheck className="w-3 h-3" />
                  <span>54 features evaluated</span>
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 self-end sm:self-auto">
              <button
                type="button"
                onClick={loadDemoPatient}
                disabled={isLoading}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-[#7C9692] hover:text-[#E8F1EE] bg-[#0A1514]/60 hover:bg-[#112321] border border-[#7C9692]/15 transition-colors cursor-pointer disabled:opacity-50"
                title="Re-analyze patient baseline"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
                <span>Re-analyze</span>
              </button>
              <button
                type="button"
                onClick={clearPatient}
                disabled={isLoading}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-[#7C9692] hover:text-rose-300 bg-[#0A1514]/60 hover:bg-rose-950/20 border border-[#7C9692]/15 transition-colors cursor-pointer disabled:opacity-50"
                title="Clear loaded patient"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear</span>
              </button>
            </div>
          </div>

          {/* 1. Hero: Overall CAD Risk Number + Threshold Bar + Verdict */}
          <DashboardHero prediction={analysis.predictions.cath} />

          {/* 2. Three Vessel Cards in a Row (LAD, LCX, RCA) */}
          <VesselRiskRow
            predictions={analysis.predictions}
            selectedTarget={selectedTarget}
            onSelectTarget={(target) => setSelectedTarget(target)}
            onHoverTarget={(target) => setHoveredTarget(target)}
          />

          {/* 3 & 4. Main Diagnostic Split: Drivers Chart (Left) + 3D Coronary Preview (Right) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left: What's driving this (Top 5 SHAP diverging bar chart) */}
            <div className="lg:col-span-5 flex flex-col space-y-4">
              <ShapDriversChart
                explanation={
                  selectedTarget !== "cath" && analysis.explanations[selectedTarget]
                    ? analysis.explanations[selectedTarget]
                    : analysis.explanations.cath
                }
                targetLabel={selectedTarget.toUpperCase()}
              />
            </div>

            {/* Right: Compact 3D Coronary Preview */}
            <div className="lg:col-span-7 flex flex-col">
              <div className="relative rounded-2xl overflow-hidden border border-slate-700/30 shadow-2xl bg-white min-h-[500px] lg:min-h-[560px]">
                <Suspense
                  fallback={
                    <ViewerLoadingFallback className="h-full w-full rounded-none border-0 bg-white" />
                  }
                >
                  <CoronaryViewer
                    predictions={analysis.predictions}
                    explanations={analysis.explanations}
                    selectedTarget={effectiveTarget}
                    onSelectTarget={(target) => setSelectedTarget(target)}
                    onOpenSimulator={() => navigate("/simulator")}
                    className="h-full w-full min-h-[500px] lg:min-h-[560px]"
                  />
                </Suspense>
              </div>
            </div>
          </div>

          {/* Single disclaimer line at bottom — not repeated elsewhere */}
          <footer className="pt-6 pb-4 text-center">
            <p className="text-[11px] text-[#7C9692]/60 font-normal">
              Research prototype, not a medical diagnosis &bull; CoroVista Machine Learning Architecture
            </p>
          </footer>
        </div>
      )}
    </div>
  )
}
