import React, { Suspense, lazy } from "react"
import type { AnalysisResponse } from "@/types/patient"
import type { TargetName } from "@/types/prediction"
import { getVesselColor } from "@/lib/vesselColors"
import { formatPercent } from "@/lib/utils"
import { ModelInfoPopover } from "@/components/dashboard/ModelInfoPopover"
import { VesselRiskRow } from "@/components/dashboard/VesselRiskRow"
import { ShapDriversChart } from "@/components/dashboard/ShapDriversChart"
import { ViewerLoadingFallback } from "@/components/viewer/ViewerLoadingFallback"
import { ProbabilityComparison } from "./ProbabilityComparison"

const CoronaryViewer = lazy(() =>
  import("@/components/viewer/CoronaryViewer").then((m) => ({ default: m.CoronaryViewer }))
)

interface SimulatorResultPanelProps {
  analysis: AnalysisResponse
  previousAnalysis?: AnalysisResponse | null
  selectedTarget: TargetName
  onSelectTarget: (target: TargetName) => void
  className?: string
}

export const SimulatorResultPanel: React.FC<SimulatorResultPanelProps> = ({
  analysis,
  previousAnalysis,
  selectedTarget,
  onSelectTarget,
  className = "",
}) => {
  const cath = analysis.predictions.cath
  const probPct = Math.round(cath.probability * 100)
  const threshPct = Math.round(cath.threshold * 100)
  const probFormatted = formatPercent(cath.probability)
  const isPositive = cath.probability >= cath.threshold
  const diffPp = (cath.probability - cath.threshold) * 100
  const { hex: barColor } = getVesselColor(cath.probability)

  const verdict = isPositive
    ? `Above the ${threshPct}% decision threshold`
    : `Below the ${threshPct}% decision threshold`

  return (
    <div className={`space-y-4 select-none ${className}`} role="region" aria-label="Simulation Diagnostics">
      {/* 1. Compact Result Summary Header */}
      <div className="instrument-surface rounded-2xl p-5 border border-[#7C9692]/20">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`w-2 h-2 rounded-full ${isPositive ? "bg-[#F26F69] animate-pulse" : "bg-[#2dd4bf]"}`}
                aria-hidden="true"
              />
              <span className="text-xs uppercase tracking-wider font-semibold text-[#7C9692]">
                Overall CAD Risk
              </span>
            </div>

            <div className="flex items-baseline gap-2">
              <span
                className="font-display text-4xl sm:text-5xl font-light tabular-nums leading-none"
                style={{ color: barColor }}
              >
                {probFormatted}
              </span>

              {/* Quiet inline text note */}
              <span className="text-xs text-[#7C9692] ml-2">
                <span className={diffPp >= 0 ? "text-[#F26F69] font-medium" : "text-[#2dd4bf] font-medium"}>
                  {diffPp >= 0 ? `+${diffPp.toFixed(1)}` : diffPp.toFixed(1)} pp
                </span>
                <span className="text-[#7C9692]/60"> vs &theta;={threshPct}%</span>
              </span>
            </div>

            <p className="text-xs text-[#7C9692] mt-1.5">
              <strong className={isPositive ? "text-[#F26F69]" : "text-[#2dd4bf]"}>
                {verdict}
              </strong>
              <span className="text-[#7C9692]/60 ml-1.5">
                &bull; Simulated patient risk
              </span>
            </p>
          </div>

          <ModelInfoPopover prediction={cath} />
        </div>

        {/* Slim risk bar */}
        <div className="space-y-1 pt-1">
          <div className="relative h-1.5 w-full rounded-full bg-[#0A1514] overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${probPct}%`, backgroundColor: barColor }}
            />
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-[#E8F1EE] z-10"
              style={{ left: `${threshPct}%` }}
              title={`Threshold: ${threshPct}%`}
            />
          </div>
          <div className="flex justify-between text-[10px] font-mono text-[#7C9692]/60">
            <span>0%</span>
            <span>Threshold: {threshPct}%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      {/* 2. Interactive 3D Coronary Anatomy Viewport */}
      <div className="relative rounded-2xl overflow-hidden border border-[#7C9692]/25 shadow-2xl bg-[#021315] min-h-[460px] lg:min-h-[500px]">
        <Suspense fallback={<ViewerLoadingFallback className="h-full w-full rounded-none border-0 bg-[#021315]" />}>
          <CoronaryViewer
            predictions={analysis.predictions}
            explanations={analysis.explanations}
            selectedTarget={selectedTarget}
            onSelectTarget={onSelectTarget}
            className="h-full w-full min-h-[460px] lg:min-h-[500px]"
          />
        </Suspense>
      </div>

      {/* 3. Three Vessel Cards Row */}
      <VesselRiskRow
        predictions={analysis.predictions}
        selectedTarget={selectedTarget}
        onSelectTarget={onSelectTarget}
      />

      {/* 4. Consecutive Simulation Sensitivity Comparison */}
      {previousAnalysis && (
        <ProbabilityComparison previous={previousAnalysis} current={analysis} />
      )}

      {/* 5. Top SHAP Drivers Diverging Bar Chart */}
      <ShapDriversChart
        explanation={
          selectedTarget !== "cath" && analysis.explanations[selectedTarget]
            ? analysis.explanations[selectedTarget]
            : analysis.explanations.cath
        }
        targetLabel={selectedTarget.toUpperCase()}
      />
    </div>
  )
}
