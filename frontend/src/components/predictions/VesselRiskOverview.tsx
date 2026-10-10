import React from "react"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import { VesselRiskCard } from "./VesselRiskCard"

interface VesselRiskOverviewProps {
  predictions: PredictionResponse["predictions"]
  selectedTarget: TargetName
  onSelectTarget: (target: TargetName) => void
  className?: string
}

export const VesselRiskOverview: React.FC<VesselRiskOverviewProps> = ({
  predictions,
  selectedTarget,
  onSelectTarget,
  className = "",
}) => {
  const vessels: TargetName[] = ["lad", "lcx", "rca"]

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Vessel-Specific Stenosis Risk</h3>
          <p className="text-xs text-muted-foreground">
            Target-specific models predicting ≥ 50% luminal obstruction. Click a vessel to inspect SHAP drivers.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-2.5">
        {vessels.map((v) => (
          <VesselRiskCard
            key={v}
            target={v}
            prediction={predictions[v]}
            isSelected={selectedTarget === v}
            onSelect={() => onSelectTarget(v)}
          />
        ))}
      </div>
    </div>
  )
}
