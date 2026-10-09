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
      className={`border rounded-xl p-4 bg-card transition-all duration-200 cursor-pointer shadow-xs flex flex-col justify-between ${
        isSelected
          ? "border-primary ring-2 ring-primary/60 bg-primary/5 shadow-md scale-[1.01]"
          : "border-border/80 hover:border-border hover:bg-card/80"
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
        <div className="flex items-start justify-between gap-1.5 mb-2.5">
          <div className="flex items-center gap-2">
            <div
              className={`w-7 h-7 rounded-md flex items-center justify-center text-xs font-mono font-bold shrink-0 ${
                isPositive
                  ? "bg-rose-950/60 text-rose-300 border border-rose-800/70"
                  : "bg-secondary text-foreground border border-border"
              }`}
            >
              {meta.short}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <h4 className="text-sm font-semibold text-foreground leading-tight">{meta.short}</h4>
                {isSelected && (
                  <span className="text-[9px] font-mono font-medium px-1.5 py-0.2 rounded bg-primary/20 text-primary border border-primary/30">
                    Selected
                  </span>
                )}
              </div>
              <p className="text-[11px] text-muted-foreground truncate">{meta.full}</p>
            </div>
          </div>
          <PredictionBadge prediction={prediction.prediction} size="sm" />
        </div>

        <div className="my-2.5 flex items-baseline justify-between gap-2">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono tracking-tight text-foreground">
              {formatPercent(prediction.probability)}
            </span>
            <span className="text-xs text-muted-foreground">probability</span>
          </div>

          <span
            className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
              isPositive
                ? "bg-rose-500/10 text-rose-500 border-rose-500/20"
                : "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
            }`}
          >
            {isPositive ? "&ge; cutoff" : "< cutoff"}
          </span>
        </div>
      </div>

      <div className="space-y-2 pt-2 border-t border-border/50">
        <RiskBar
          probability={prediction.probability}
          threshold={prediction.threshold}
        />

        <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-0.5 gap-1">
          <span className="truncate leading-tight" title={meta.territory}>
            {meta.territory}
          </span>
          <span className="font-mono text-foreground/80 font-medium shrink-0 bg-secondary/70 px-1.5 py-0.5 rounded border border-border/40">
            Cutoff: {formatPercent(prediction.threshold)}
          </span>
        </div>
      </div>
    </div>
  )
}
