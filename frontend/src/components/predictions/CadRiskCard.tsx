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
      className={`border border-border/80 bg-card rounded-xl p-4.5 shadow-sm space-y-3.5 ${className}`}
      role="region"
      aria-label="Overall Coronary Artery Disease Risk Assessment"
    >
      {/* Header Row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shrink-0">
            <Heart className="w-4 h-4 fill-primary/20" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground leading-tight">Overall CAD Risk</h3>
            <p className="text-[11px] text-muted-foreground">Cardiac Catheterization Target (&ge;50% stenosis)</p>
          </div>
        </div>
        <PredictionBadge prediction={prediction.prediction} size="md" />
      </div>

      {/* Primary Probability & Classification Summary */}
      <div className="flex flex-wrap items-baseline justify-between gap-2 pt-0.5">
        <div className="flex items-baseline gap-2.5">
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
              ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"
              : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
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
      <div className="grid grid-cols-3 gap-2 pt-1 border-t border-border/50 text-[11px]">
        <div className="bg-secondary/40 rounded-md p-1.5 border border-border/40">
          <span className="text-[10px] text-muted-foreground block">Decision Boundary</span>
          <span className="font-mono font-semibold text-foreground">
            Decision Threshold: {formatPercent(prediction.threshold)}
          </span>
        </div>
        <div className="bg-secondary/40 rounded-md p-1.5 border border-border/40">
          <span className="text-[10px] text-muted-foreground block">Architecture</span>
          <span className="font-mono font-medium text-foreground truncate block">
            Model: {prediction.model_family || "XGBoost"}
          </span>
        </div>
        <div className="bg-secondary/40 rounded-md p-1.5 border border-border/40">
          <span className="text-[10px] text-muted-foreground block">Calibration Method</span>
          <span className="font-mono font-medium text-foreground truncate block">
            Calibration: {prediction.calibration || "Platt/Sigmoid"}
          </span>
        </div>
      </div>
    </div>
  )
}
