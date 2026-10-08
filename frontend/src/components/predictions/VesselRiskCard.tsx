import React from "react"
import type { TargetName, TargetPrediction } from "@/types/prediction"
import { formatPercent } from "@/lib/utils"
import { PredictionBadge } from "@/components/common/PredictionBadge"
import { RiskBar } from "@/components/common/RiskBar"

interface VesselRiskCardProps {
  target: TargetName
  prediction: TargetPrediction
  isSelected?: boolean
  onSelect?: () => void
  className?: string
}

const VESSEL_TITLES: Record<string, { short: string; full: string; territory: string }> = {
  lad: {
    short: "LAD",
    full: "Left Anterior Descending",
    territory: "Anterior wall, septum & apex",
  },
  lcx: {
    short: "LCX",
    full: "Left Circumflex",
    territory: "Lateral & posterior LV myocardium",
  },
  rca: {
    short: "RCA",
    full: "Right Coronary Artery",
    territory: "Inferior wall, RV & conduction system",
  },
}

export const VesselRiskCard: React.FC<VesselRiskCardProps> = ({
  target,
  prediction,
  isSelected = false,
  onSelect,
  className = "",
}) => {
  const meta = VESSEL_TITLES[target] || { short: target.toUpperCase(), full: target, territory: "" }
  const isPositive = prediction.probability >= prediction.threshold

  return (
    <div
      onClick={onSelect}
      className={`border rounded-xl p-4.5 bg-card transition-all duration-200 cursor-pointer shadow-sm flex flex-col justify-between ${
        isSelected
          ? "border-primary ring-1 ring-primary/40 bg-card/90"
          : "border-border hover:border-border/80 hover:bg-card/70"
      } ${className}`}
      role="button"
      tabIndex={0}
      aria-pressed={isSelected}
      aria-label={`${meta.short} stenosis risk: ${formatPercent(prediction.probability)}, status: ${prediction.prediction}`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onSelect?.()
        }
      }}
    >
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <div
              className={`w-7 h-7 rounded-md flex items-center justify-center text-xs font-mono font-bold ${
                isPositive
                  ? "bg-rose-950/50 text-rose-300 border border-rose-800/60"
                  : "bg-secondary text-foreground border border-border"
              }`}
            >
              {meta.short}
            </div>
            <div>
              <h4 className="text-sm font-semibold text-foreground leading-tight">{meta.short}</h4>
              <p className="text-[11px] text-muted-foreground truncate">{meta.full}</p>
            </div>
          </div>
          <PredictionBadge prediction={prediction.prediction} size="sm" />
        </div>

        <div className="my-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono tracking-tight text-foreground">
            {formatPercent(prediction.probability)}
          </span>
          <span className="text-xs text-muted-foreground">probability</span>
        </div>
      </div>

      <div className="space-y-2 pt-2 border-t border-border/50">
        <RiskBar
          probability={prediction.probability}
          threshold={prediction.threshold}
        />

        <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
          <span className="truncate">{meta.territory}</span>
          <span className="font-mono text-muted-foreground/80 shrink-0">
            Cutoff: {formatPercent(prediction.threshold)}
          </span>
        </div>
      </div>
    </div>
  )
}
