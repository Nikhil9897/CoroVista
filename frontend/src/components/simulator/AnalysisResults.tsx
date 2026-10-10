import React, { Suspense, lazy } from "react"
import type { AnalysisResponse } from "@/types/patient"
import type { TargetName } from "@/types/prediction"
import { CadRiskCard } from "@/components/predictions/CadRiskCard"
import { VesselRiskOverview } from "@/components/predictions/VesselRiskOverview"
import { ExplanationPanel } from "@/components/explanations/ExplanationPanel"
import { ViewerLoadingFallback } from "@/components/viewer/ViewerLoadingFallback"
import { ProbabilityComparison } from "./ProbabilityComparison"

const CoronaryViewer = lazy(() =>
  import("@/components/viewer/CoronaryViewer").then((m) => ({ default: m.CoronaryViewer }))
)

interface AnalysisResultsProps {
  analysis: AnalysisResponse
  previousAnalysis: AnalysisResponse | null
  selectedTarget: TargetName
  onSelectTarget: (target: TargetName) => void
  className?: string
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  analysis,
  previousAnalysis,
  selectedTarget,
  onSelectTarget,
  className = "",
}) => {
  return (
    <div className={`space-y-6 ${className}`} role="region" aria-label="Simulated Risk Results">
      {/* 1. Compact Primary CAD Risk Summary */}
      <div className="spatial-fade-up">
        <CadRiskCard prediction={analysis.predictions.cath} />
      </div>

      {/* 2. Interactive 3D Coronary Anatomy Viewer */}
      <div className="rounded-2xl overflow-hidden border border-border/70 shadow-spatial-lg bg-surface-0 spatial-fade-up" style={{ animationDelay: "0.1s" }}>
        <Suspense fallback={<ViewerLoadingFallback className="w-full min-h-[480px] lg:min-h-[520px]" />}>
          <CoronaryViewer
            predictions={analysis.predictions}
            selectedTarget={selectedTarget}
            onSelectTarget={onSelectTarget}
            className="w-full min-h-[480px] lg:min-h-[520px]"
          />
        </Suspense>
      </div>

      {/* Middle Section: Vessel-Specific Stenosis (LAD, LCX, RCA) */}
      <div className="spatial-fade-up" style={{ animationDelay: "0.15s" }}>
        <VesselRiskOverview
          predictions={analysis.predictions}
          selectedTarget={selectedTarget}
          onSelectTarget={onSelectTarget}
        />
      </div>

      {/* Optional Before / After Comparison View (if >= 2 analyses run) */}
      {previousAnalysis && (
        <div className="spatial-fade-up" style={{ animationDelay: "0.2s" }}>
          <ProbabilityComparison previous={previousAnalysis} current={analysis} />
        </div>
      )}

      {/* Bottom Section: Local SHAP Feature Explanations */}
      <div className="spatial-fade-up" style={{ animationDelay: "0.25s" }}>
        <ExplanationPanel
          explanations={analysis.explanations}
          selectedTarget={selectedTarget}
          onSelectTarget={onSelectTarget}
        />
      </div>
    </div>
  )
}
