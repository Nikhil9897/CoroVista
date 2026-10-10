import React from "react"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import { VESSEL_NAMES, RISK_COLOR_STOPS, getVesselColor } from "@/lib/vesselColors"
import { formatPercent } from "@/lib/utils"

interface VesselRiskRowProps {
  predictions: PredictionResponse["predictions"]
  selectedTarget?: TargetName
  onSelectTarget: (target: TargetName) => void
  onHoverTarget?: (target: TargetName | null) => void
  className?: string
}

const GRADIENT_CSS = `linear-gradient(to right, ${RISK_COLOR_STOPS.map(
  (s) => `${s.hex} ${s.stop * 100}%`
).join(", ")})`

function getVesselStatus(probability: number, threshold: number): {
  label: "Below threshold" | "Near threshold" | "Above threshold"
  dotColor: string
} {
  const diff = probability - threshold
  if (diff > 0.05) {
    return { label: "Above threshold", dotColor: "bg-rose-400" }
  }
  if (diff < -0.05) {
    return { label: "Below threshold", dotColor: "bg-emerald-400" }
  }
  return { label: "Near threshold", dotColor: "bg-amber-400" }
}

export const VesselRiskRow: React.FC<VesselRiskRowProps> = ({
  predictions,
  selectedTarget,
  onSelectTarget,
  onHoverTarget,
  className = "",
}) => {
  const vessels: Array<"lad" | "lcx" | "rca"> = ["lad", "lcx", "rca"]

  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-3 gap-3.5 ${className}`}
      role="region"
      aria-label="Coronary Vessel Stenosis Risks"
    >
      {vessels.map((key) => {
        const pred = predictions[key]
        const meta = VESSEL_NAMES[key]
        const isSelected = selectedTarget === key
        const probPct = pred.probability * 100
        const threshPct = pred.threshold * 100
        const probFormatted = formatPercent(pred.probability)
        const threshFormatted = formatPercent(pred.threshold)
        const status = getVesselStatus(pred.probability, pred.threshold)
        const { hex: colorHex } = getVesselColor(pred.probability)

        return (
          <div
            key={key}
            onClick={() => onSelectTarget(key)}
            onMouseEnter={() => onHoverTarget?.(key)}
            onMouseLeave={() => onHoverTarget?.(null)}
            className={`instrument-surface rounded-2xl p-4 transition-all duration-200 cursor-pointer select-none text-left relative overflow-hidden group ${
              isSelected
                ? "ring-1 ring-[#F26F69] bg-[#142A27]"
                : "hover:border-[#7C9692]/30 hover:bg-[#132825]"
            }`}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault()
                onSelectTarget(key)
              }
            }}
            aria-pressed={isSelected}
            aria-label={`${meta.short} stenosis risk: ${probFormatted}, status: ${pred.prediction}`}
          >
            {/* Top row: Vessel name and status dot */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm tracking-tight text-[#E8F1EE]">
                    {meta.short}
                  </span>
                  <span className="text-[11px] text-[#7C9692] font-normal truncate">
                    {meta.full}
                  </span>
                </div>
                <p className="text-[10px] text-[#7C9692]/70 mt-0.5">
                  {meta.territory}
                </p>
              </div>

              {/* Status word + dot */}
              <div className="flex items-center gap-1.5 shrink-0 px-2 py-0.5 rounded-full bg-[#0A1514]/60 border border-[#7C9692]/15 text-[10px]">
                <span className={`w-1.5 h-1.5 rounded-full ${status.dotColor}`} aria-hidden="true" />
                <span className="text-[#E8F1EE]/80 font-medium">
                  {pred.prediction ? `${pred.prediction} • ` : ""}{status.label}
                </span>
              </div>
            </div>

            {/* Probability number */}
            <div className="flex items-baseline gap-1.5 my-2">
              <span
                className="font-display text-3xl font-light tabular-nums leading-none"
                style={{ color: colorHex }}
              >
                {probFormatted}
              </span>
              <span className="text-[11px] text-[#7C9692] ml-auto font-mono">
                Cutoff: {threshFormatted}
              </span>
            </div>

            {/* Thin spectrum bar */}
            <div className="relative pt-1 pb-1">
              <div
                className="h-1.5 w-full rounded-full relative overflow-hidden"
                style={{ background: GRADIENT_CSS }}
              >
                {/* Active value indicator line */}
                <div
                  className="absolute top-0 bottom-0 w-1 bg-white rounded-full shadow-sm"
                  style={{ left: `calc(${Math.min(100, Math.max(0, probPct))}% - 2px)` }}
                  aria-hidden="true"
                />
              </div>

              {/* Threshold tick notch below bar */}
              <div
                className="absolute top-1 bottom-1 w-0.5 bg-[#E8F1EE]/90 shadow-sm pointer-events-none"
                style={{ left: `${Math.min(100, Math.max(0, threshPct))}%` }}
                title={`Decision threshold: ${threshPct.toFixed(0)}%`}
                aria-hidden="true"
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
