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
    <div className={`space-y-6 ${className}`} role="region" aria-label="Simulated Risk Results">
      {/* Top Section: CAD Risk Card + 3D Heart Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <CadRiskCard prediction={analysis.predictions.cath} className="h-full" />
        </div>
        <div className="lg:col-span-2">
          <Suspense fallback={<ViewerLoadingFallback className="h-full min-h-[440px]" />}>
            <CoronaryViewer
              predictions={analysis.predictions}
              selectedTarget={selectedTarget}
              onSelectTarget={onSelectTarget}
              className="h-full min-h-[440px]"
            />
          </Suspense>
        </div>
      </div>

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
