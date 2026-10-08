import React from "react"
import { formatPercent } from "@/lib/utils"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import { RISK_COLOR_STOPS, VESSEL_NAMES } from "@/lib/vesselColors"

interface ViewerLegendProps {
  predictions?: PredictionResponse["predictions"]
  selectedTarget?: TargetName
  className?: string
}

export const ViewerLegend: React.FC<ViewerLegendProps> = ({
  predictions,
  selectedTarget,
  className = "",
}) => {
  // Gradient CSS string from stops
  const gradientCss = `linear-gradient(to right, ${RISK_COLOR_STOPS.map(
    (s) => `${s.hex} ${s.stop * 100}%`
  ).join(", ")})`

  const activeVesselKey = selectedTarget && selectedTarget in VESSEL_NAMES ? selectedTarget : null
  const activePred = activeVesselKey && predictions ? predictions[activeVesselKey] : null
  const defaultMeta = activeVesselKey ? VESSEL_NAMES[activeVesselKey] : null

  const activeThreshold = activePred?.threshold ?? defaultMeta?.defaultThreshold ?? 0.5
  const activeProb = activePred?.probability ?? null

  return (
    <div
      className={`bg-card/85 backdrop-blur-md border border-border/70 rounded-lg p-2.5 shadow-sm text-xs space-y-1.5 ${className}`}
      role="region"
      aria-label="Model-predicted stenosis probability legend"
    >
      <div className="flex items-center justify-between text-[11px]">
        <span className="font-medium text-foreground">
          Model-predicted stenosis probability
        </span>
        {activeVesselKey && (
          <span className="text-[10px] text-muted-foreground uppercase font-mono tracking-wider">
            {defaultMeta?.short} Threshold: <strong className="text-foreground">{formatPercent(activeThreshold)}</strong>
          </span>
        )}
      </div>

      {/* Gradient Bar with Threshold and Value Markers */}
      <div className="relative pt-1 pb-1">
        <div
          className="h-2.5 w-full rounded-full border border-border/40 relative shadow-inner"
          style={{ background: gradientCss }}
        >
          {/* Threshold marker for active vessel */}
          <div
            className="absolute top-[-3px] bottom-[-3px] w-0.5 bg-foreground shadow-sm z-10"
            style={{ left: `${Math.min(100, Math.max(0, activeThreshold * 100))}%` }}
            title={`Decision Threshold: ${formatPercent(activeThreshold)}`}
          >
            <div className="absolute -top-1.5 -translate-x-1/2 w-0 h-0 border-l-[3px] border-l-transparent border-r-[3px] border-r-transparent border-t-[4px] border-t-foreground" />
          </div>

          {/* Active probability point marker if available */}
          {activeProb !== null && (
            <div
              className="absolute top-[-4px] bottom-[-4px] w-3 h-3 -translate-x-1/2 rounded-full border-2 border-white bg-foreground shadow-md z-20 pointer-events-none"
              style={{ left: `${Math.min(100, Math.max(0, activeProb * 100))}%` }}
              title={`Current probability: ${formatPercent(activeProb)}`}
            />
          )}
        </div>

        {/* Labels below gradient */}
        <div className="flex justify-between text-[10px] font-mono text-muted-foreground mt-1 px-0.5">
          <span>0%</span>
          <span>25%</span>
          <span>50%</span>
          <span>75%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Vessel summary chips */}
      {predictions && (
        <div className="flex items-center gap-2 pt-0.5 text-[10px] text-muted-foreground border-t border-border/50">
          {(["lad", "lcx", "rca"] as const).map((vKey) => {
            const p = predictions[vKey]
            const meta = VESSEL_NAMES[vKey]
            const isSelected = selectedTarget === vKey
            return (
              <span
                key={vKey}
                className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded ${
                  isSelected ? "bg-primary/15 text-primary font-semibold border border-primary/30" : "bg-muted/40"
                }`}
              >
                <span className="font-mono">{meta.short}:</span>
                <span className="text-foreground">{formatPercent(p.probability)}</span>
                <span className="text-[9px] text-muted-foreground">(&theta;={p.threshold.toFixed(2)})</span>
              </span>
            )
          })}
        </div>
      )}
    </div>
  )
}
