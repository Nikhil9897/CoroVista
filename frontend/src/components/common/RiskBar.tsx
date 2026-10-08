import React from "react"
import { formatPercent } from "@/lib/utils"

interface RiskBarProps {
  probability: number
  threshold: number
  showThresholdMarker?: boolean
  className?: string
}

export const RiskBar: React.FC<RiskBarProps> = ({
  probability,
  threshold,
  showThresholdMarker = true,
  className = "",
}) => {
  // Continuous percent clamped to 0-100 for width
  const percent = Math.min(Math.max(probability * 100, 0), 100)
  const thresholdPercent = Math.min(Math.max(threshold * 100, 0), 100)

  // Determine semantic color based on continuous probability relative to threshold
  const isPositive = probability >= threshold

  let barColor = "bg-emerald-500"
  if (percent > 65) {
    barColor = "bg-rose-500"
  } else if (percent > 35) {
    barColor = "bg-amber-500"
  }

  // Model probability category label
  let tierLabel = "Low model score"
  if (percent >= 65) {
    tierLabel = "Elevated model score"
  } else if (percent >= 40) {
    tierLabel = "Moderate model score"
  }

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="font-medium text-foreground/80">{tierLabel}</span>
        <span className="font-mono">{formatPercent(probability)}</span>
      </div>

      <div className="relative w-full h-2.5 bg-secondary/80 rounded-full overflow-hidden border border-border/60">
        {/* Animated fill bar */}
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${barColor}`}
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={Math.round(percent)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Probability ${formatPercent(probability)}`}
        />

        {/* Decision threshold indicator notch */}
        {showThresholdMarker && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-foreground/90 z-10 shadow-sm"
            style={{ left: `${thresholdPercent}%` }}
            title={`Decision threshold: ${formatPercent(threshold)}`}
          />
        )}
      </div>

      <div className="flex items-center justify-between text-[11px] text-muted-foreground/70">
        <span>0%</span>
        {showThresholdMarker && (
          <span className="font-mono text-muted-foreground">
            Threshold: {formatPercent(threshold)} {isPositive ? "(Exceeded)" : "(Below)"}
          </span>
        )}
        <span>100%</span>
      </div>
    </div>
  )
}
