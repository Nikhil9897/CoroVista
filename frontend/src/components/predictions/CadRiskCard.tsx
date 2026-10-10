import React from "react"
import { Heart } from "lucide-react"
import type { TargetPrediction } from "@/types/prediction"
import { formatPercent } from "@/lib/utils"
import { PredictionBadge } from "@/components/common/PredictionBadge"
import { RiskBar } from "@/components/common/RiskBar"

interface CadRiskCardProps {
  prediction: TargetPrediction
  className?: string
}

export const CadRiskCard: React.FC<CadRiskCardProps> = ({
  prediction,
  className = "",
}) => {
  const isPositive = prediction.probability >= prediction.threshold
  const diffPp = ((prediction.probability - prediction.threshold) * 100).toFixed(1)

  return (
    <div
      className={`glass-panel rounded-2xl p-4 sm:p-5 border border-border/80 shadow-spatial space-y-3.5 select-none ${className}`}
      role="region"
      aria-label="Overall Coronary Artery Disease Risk Assessment"
    >
      {/* Header Row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center text-primary shrink-0 shadow-xs">
            <Heart className="w-4 h-4 fill-primary/30" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground tracking-tight leading-tight">
              Overall CAD Risk
            </h3>
            <p className="text-[11px] text-muted-foreground">Cardiac Catheterization Target (&ge;50% stenosis)</p>
          </div>
        </div>
        <PredictionBadge prediction={prediction.prediction} size="md" />
      </div>

      {/* Primary Probability & Classification Summary */}
      <div className="flex flex-wrap items-baseline justify-between gap-2 pt-0.5">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground font-mono">
            {formatPercent(prediction.probability)}
          </span>
          <span className="text-xs text-muted-foreground font-medium">
            Predicted Risk Probability
          </span>
        </div>

        <span
          className={`text-[11px] font-mono px-2 py-0.5 rounded-md border font-medium ${
            isPositive
              ? "bg-rose-500/15 text-rose-400 border-rose-500/30"
              : "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
          }`}
        >
          {Number(diffPp) >= 0 ? `+${diffPp} pp` : `${diffPp} pp`} vs threshold
        </span>
      </div>

      {/* Risk Bar with Decision Threshold Notch */}
      <RiskBar
        probability={prediction.probability}
        threshold={prediction.threshold}
      />

      {/* Structured Clinical & Model Metadata Grid */}
      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-border/40 text-[11px]">
        <div className="bg-surface-2/80 rounded-xl p-2.5 border border-border/40 text-center">
          <span className="text-[10px] font-mono text-muted-foreground uppercase block tracking-wider">Threshold</span>
          <span className="font-mono text-xs font-bold text-foreground block mt-0.5">
            {formatPercent(prediction.threshold)}
          </span>
          <span className="text-[9px] text-muted-foreground font-mono block">θ Cutoff</span>
        </div>
        <div className="bg-surface-2/80 rounded-xl p-2.5 border border-border/40 text-center">
          <span className="text-[10px] font-mono text-muted-foreground uppercase block tracking-wider">Model</span>
          <span className="font-mono text-xs font-bold text-foreground block mt-0.5">
            {prediction.model_family || "XGBoost"}
          </span>
          <span className="text-[9px] text-muted-foreground font-mono block">Classifier</span>
        </div>
        <div className="bg-surface-2/80 rounded-xl p-2.5 border border-border/40 text-center">
          <span className="text-[10px] font-mono text-muted-foreground uppercase block tracking-wider">Calibration</span>
          <span className="font-mono text-xs font-bold text-foreground block mt-0.5">
            {prediction.calibration ? "Platt / Sigmoid" : "Empirical"}
          </span>
          <span className="text-[9px] text-muted-foreground font-mono block">Decoupled</span>
        </div>
      </div>
    </div>
  )
}
