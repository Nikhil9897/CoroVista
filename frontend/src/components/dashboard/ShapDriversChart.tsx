import React from "react"
import type { ExplanationResponse, FeatureContributionItem } from "@/types/explanation"

interface ShapDriversChartProps {
  explanation?: ExplanationResponse | null
  targetLabel?: string
  className?: string
}

export const ShapDriversChart: React.FC<ShapDriversChartProps> = ({
  explanation,
  targetLabel = "Overall CAD",
  className = "",
}) => {
  if (!explanation || !explanation.features || explanation.features.length === 0) {
    return (
      <div className={`instrument-surface rounded-2xl p-5 ${className}`}>
        <h4 className="text-xs font-semibold text-[#E8F1EE] uppercase tracking-wider mb-2">
          What&apos;s driving this &bull; {targetLabel}
        </h4>
        <p className="text-xs text-[#7C9692]">
          No local feature attributions available for this target.
        </p>
      </div>
    )
  }

  // Pick top 5 absolute drivers
  const topDrivers: FeatureContributionItem[] = [...explanation.features]
    .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
    .slice(0, 5)

  const maxAbs = Math.max(...topDrivers.map((d) => Math.abs(d.shap_value)), 0.01)

  return (
    <div
      className={`instrument-surface rounded-2xl p-5 select-none ${className}`}
      role="region"
      aria-label={`Top clinical factors driving ${targetLabel} risk`}
    >
      <div className="flex items-center justify-between gap-3 mb-4">
        <div>
          <h4 className="text-sm font-semibold text-[#E8F1EE] tracking-tight">
            What&apos;s driving this risk <span className="text-[#7C9692] font-normal text-xs">(Why this prediction?)</span>
          </h4>
          <p className="text-xs text-[#7C9692] mt-0.5">
            Top 5 TreeSHAP Log-Odds feature contributions for {targetLabel}
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px] text-[#7C9692] font-mono">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#F26F69]" aria-hidden="true" />
            <span>Increases risk</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#2dd4bf]" aria-hidden="true" />
            <span>Lowers risk</span>
          </span>
        </div>
      </div>

      {/* Diverging bar list */}
      <div className="space-y-3 pt-1">
        {topDrivers.map((item) => {
          const isHigher = item.direction === "positive" || item.shap_value > 0
          const magnitudePct = Math.min(100, (Math.abs(item.shap_value) / maxAbs) * 100)
          const barColor = isHigher ? "#F26F69" : "#2dd4bf"
          const prefix = item.shap_value > 0 ? "+" : ""

          return (
            <div key={item.feature} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 truncate pr-2">
                  <span className="text-[#E8F1EE] font-medium truncate">
                    {item.label || item.feature}
                  </span>
                  <span className="text-[11px] text-[#7C9692] font-mono bg-[#0A1514]/60 px-1.5 py-0.2 rounded border border-[#7C9692]/15">
                    {typeof item.value === "number" ? (Number.isInteger(item.value) ? item.value : item.value.toFixed(1)) : item.value}
                  </span>
                </div>
                <span
                  className="text-xs font-mono font-medium shrink-0 tabular-nums"
                  style={{ color: barColor }}
                >
                  {prefix}{item.shap_value.toFixed(2)}
                </span>
              </div>

              {/* Center-aligned diverging track */}
              <div className="relative h-2 w-full rounded-full bg-[#0A1514]/80 overflow-hidden flex">
                {/* Left side (negative / protective) */}
                <div className="w-1/2 h-full flex justify-end">
                  {!isHigher && (
                    <div
                      className="h-full rounded-l-full transition-all duration-500"
                      style={{
                        width: `${magnitudePct}%`,
                        backgroundColor: barColor,
                      }}
                      role="progressbar"
                      aria-valuenow={Math.abs(item.shap_value)}
                      aria-label={`${item.label} lowers risk by ${Math.abs(item.shap_value).toFixed(2)}`}
                    />
                  )}
                </div>

                {/* Center tick divider */}
                <div className="w-0.5 h-full bg-[#7C9692]/40 shrink-0" aria-hidden="true" />

                {/* Right side (positive / risk-increasing) */}
                <div className="w-1/2 h-full flex justify-start">
                  {isHigher && (
                    <div
                      className="h-full rounded-r-full transition-all duration-500"
                      style={{
                        width: `${magnitudePct}%`,
                        backgroundColor: barColor,
                      }}
                      role="progressbar"
                      aria-valuenow={item.shap_value}
                      aria-label={`${item.label} increases risk by ${item.shap_value.toFixed(2)}`}
                    />
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
