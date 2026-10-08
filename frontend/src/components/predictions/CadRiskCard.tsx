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

export const CadRiskCard: React.FC<CadRiskCardProps> = ({ prediction, className = "" }) => {
  return (
    <div
      className={`border border-border/80 bg-card rounded-xl p-5 shadow-sm space-y-4 flex flex-col justify-between ${className}`}
      role="region"
      aria-label="Overall Coronary Artery Disease Risk Assessment"
    >
      <div>
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <Heart className="w-4 h-4 fill-primary/20" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-foreground">Overall CAD Risk</h3>
              <p className="text-[11px] text-muted-foreground">Cardiac Catheterization Target</p>
            </div>
          </div>
          <PredictionBadge prediction={prediction.prediction} size="md" />
        </div>

        <div className="mt-4 flex items-baseline gap-3">
          <span className="text-4xl font-bold tracking-tight text-foreground font-mono">
            {formatPercent(prediction.probability)}
          </span>
          <span className="text-xs text-muted-foreground">
            Predicted Risk Probability
          </span>
        </div>
      </div>

      <div className="space-y-3 pt-2 border-t border-border/50">
        <RiskBar
          probability={prediction.probability}
          threshold={prediction.threshold}
        />

        <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
          <span>Model: {prediction.model_family || "XGBoost"}</span>
          <span>Calibration: {prediction.calibration || "Platt/Sigmoid"}</span>
          <span>Decision Threshold: {formatPercent(prediction.threshold)}</span>
        </div>
      </div>
    </div>
  )
}
