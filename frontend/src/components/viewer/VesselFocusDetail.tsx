import React from "react"
import { X, ArrowUpRight, ArrowDownRight, Compass } from "lucide-react"
import type { CoronaryVesselId } from "./ViewerTypes"
import type { TargetPrediction } from "@/types/prediction"
import type { ExplanationResponse, FeatureContributionItem } from "@/types/explanation"
import { VESSEL_NAMES, getVesselColor } from "@/lib/vesselColors"

interface VesselFocusDetailProps {
  vesselId: CoronaryVesselId
  prediction?: TargetPrediction
  explanation?: ExplanationResponse | null
  isPerVesselShap?: boolean
  onClose: () => void
  className?: string
}

export const VesselFocusDetail: React.FC<VesselFocusDetailProps> = ({
  vesselId,
  prediction,
  explanation,
  isPerVesselShap = true,
  onClose,
  className = "",
}) => {
  const meta = VESSEL_NAMES[vesselId]
  const prob = prediction?.probability ?? 0.0
  const thresh = prediction?.threshold ?? 0.5
  const probPct = Math.round(prob * 100)
  const threshPct = Math.round(thresh * 100)
  const isStenotic = prob >= thresh
  const { hex: colorHex } = getVesselColor(prob)

  // Top 3 drivers for this vessel
  const topDrivers: FeatureContributionItem[] = explanation?.features
    ? [...explanation.features]
        .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
        .slice(0, 3)
    : []

  return (
    <div
      className={`guided-tour-in instrument-surface rounded-2xl p-4 sm:p-5 w-80 sm:w-88 shadow-2xl border border-[#7C9692]/25 select-none text-left z-30 ${className}`}
      role="dialog"
      aria-label={`Detailed analysis for ${meta.full}`}
    >
      {/* Header with vessel identity and close button */}
      <div className="flex items-start justify-between gap-2 pb-2.5 border-b border-[#7C9692]/15">
        <div>
          <div className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs"
              style={{ backgroundColor: colorHex }}
              aria-hidden="true"
            />
            <h3 className="font-semibold text-sm text-[#E8F1EE] tracking-tight">
              {meta.full}
            </h3>
            <span className="font-mono text-xs text-[#F26F69] font-medium">
              ({meta.short})
            </span>
          </div>
          <p className="text-[11px] text-[#7C9692] mt-0.5">
            {meta.territory}
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-lg text-[#7C9692] hover:text-[#E8F1EE] hover:bg-[#112321] transition-colors cursor-pointer"
          title="Exit focus mode (Esc)"
          aria-label="Exit focus mode"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Probability and status verdict */}
      <div className="py-3 space-y-2">
        <div className="flex items-baseline justify-between">
          <span className="text-xs text-[#7C9692]">Predicted stenosis probability:</span>
          <div className="flex items-baseline gap-1">
            <span
              className="font-display text-2xl font-light tabular-nums leading-none"
              style={{ color: colorHex }}
            >
              {probPct}%
            </span>
            <span className="text-[10px] text-[#7C9692] font-mono">
              vs &theta;={threshPct}%
            </span>
          </div>
        </div>

        {/* Mini probability vs threshold bar */}
        <div className="relative h-1.5 w-full rounded-full bg-[#0A1514] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${probPct}%`, backgroundColor: colorHex }}
          />
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-[#E8F1EE] z-10"
            style={{ left: `${threshPct}%` }}
            title={`Threshold: ${threshPct}%`}
          />
        </div>

        {/* One-line clinical verdict */}
        <p className="text-xs leading-relaxed text-[#E8F1EE]/90">
          {isStenotic ? (
            <span>
              <strong className="text-[#F26F69] font-semibold">Above threshold.</strong> Model predicts high likelihood of significant lumen narrowing.
            </span>
          ) : (
            <span>
              <strong className="text-[#2dd4bf] font-semibold">Below threshold.</strong> Model predicts lower likelihood of hemodynamically significant stenosis.
            </span>
          )}
        </p>
      </div>

      {/* Top 3 SHAP Drivers */}
      <div className="pt-2.5 border-t border-[#7C9692]/15 space-y-2">
        <div className="flex items-center justify-between text-[11px]">
          <span className="font-semibold text-[#E8F1EE] uppercase tracking-wider text-[10px]">
            {isPerVesselShap ? "Top Influencing Factors" : "Overall Influencing Factors"}
          </span>
          <span className="text-[10px] text-[#7C9692] font-mono">
            TreeSHAP
          </span>
        </div>

        {topDrivers.length > 0 ? (
          <div className="space-y-1.5">
            {topDrivers.map((driver) => {
              const isHigher = driver.direction === "positive" || driver.shap_value > 0
              return (
                <div
                  key={driver.feature}
                  className="flex items-center justify-between text-xs px-2 py-1 rounded-lg bg-[#0A1514]/60 border border-[#7C9692]/10"
                >
                  <div className="flex items-center gap-1.5 truncate pr-2">
                    {isHigher ? (
                      <ArrowUpRight className="w-3.5 h-3.5 text-[#F26F69] shrink-0" />
                    ) : (
                      <ArrowDownRight className="w-3.5 h-3.5 text-[#2dd4bf] shrink-0" />
                    )}
                    <span className="text-[#E8F1EE] truncate text-[11px]">
                      {driver.label || driver.feature}
                    </span>
                    <span className="text-[10px] text-[#7C9692] font-mono">
                      ({typeof driver.value === "number" ? (Number.isInteger(driver.value) ? driver.value : driver.value.toFixed(1)) : driver.value})
                    </span>
                  </div>

                  <span
                    className={`text-[10px] font-mono font-medium shrink-0 ${
                      isHigher ? "text-[#F26F69]" : "text-[#2dd4bf]"
                    }`}
                  >
                    {isHigher ? "↑ raises risk" : "↓ lowers risk"}
                  </span>
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-[11px] text-[#7C9692]">No local attribution factors available.</p>
        )}
      </div>

      {/* Footer hint */}
      <div className="mt-3 pt-2 border-t border-[#7C9692]/10 flex items-center justify-between text-[10px] text-[#7C9692]/60">
        <span className="flex items-center gap-1">
          <Compass className="w-3 h-3 text-[#F26F69]" />
          <span>Click empty space or Esc to exit</span>
        </span>
        <button
          onClick={onClose}
          className="text-[#E8F1EE] hover:underline cursor-pointer"
        >
          Exit focus
        </button>
      </div>
    </div>
  )
}
