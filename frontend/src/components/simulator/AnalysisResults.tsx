import React, { Suspense } from "react"
import type { AnalysisResponse } from "@/types/patient"
import type { TargetName } from "@/types/prediction"
import { CadRiskCard } from "@/components/predictions/CadRiskCard"
import { VesselRiskOverview } from "@/components/predictions/VesselRiskOverview"
import { ExplanationPanel } from "@/components/explanations/ExplanationPanel"
import { ViewerLoadingFallback } from "@/components/viewer/ViewerLoadingFallback"
import { ProbabilityComparison } from "./ProbabilityComparison"

import { CoronaryViewer } from "@/components/viewer/CoronaryViewer"

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
    <div className={`space-y-5 ${className}`} role="region" aria-label="Simulated Risk Results">
      {/* 1. Compact Primary CAD Risk Summary */}
      <CadRiskCard prediction={analysis.predictions.cath} />

      {/* 2. Interactive 3D Coronary Anatomy Viewer (Enlarged) */}
      <Suspense fallback={<ViewerLoadingFallback className="w-full min-h-[480px] lg:min-h-[520px]" />}>
        <CoronaryViewer
          predictions={analysis.predictions}
          selectedTarget={selectedTarget}
          onSelectTarget={onSelectTarget}
          className="w-full min-h-[480px] lg:min-h-[520px]"
        />
      </Suspense>

      {/* Middle Section: Vessel-Specific Stenosis (LAD, LCX, RCA) */}
      <VesselRiskOverview
        predictions={analysis.predictions}
        selectedTarget={selectedTarget}
        onSelectTarget={onSelectTarget}
      />

      {/* Optional Before / After Comparison View (if >= 2 analyses run) */}
      {previousAnalysis && (
        <ProbabilityComparison previous={previousAnalysis} current={analysis} />
      )}

      {/* Bottom Section: Local SHAP Feature Explanations */}
      <ExplanationPanel
        explanations={analysis.explanations}
        selectedTarget={selectedTarget}
        onSelectTarget={onSelectTarget}
      />
    </div>
  )
}
