/**
 * DashboardHero — Full-width "instrument panel" risk summary.
 * Shows the primary CAD probability with a count-up effect,
 * decision threshold delta badge, and animated risk bar.
 * No clinical fabrication: every number comes from TargetPrediction.
 */
import React, { useEffect, useRef, useState } from "react"
import type { TargetPrediction } from "@/types/prediction"
import { getVesselColor } from "@/lib/vesselColors"

import { ModelInfoPopover } from "./ModelInfoPopover"

interface DashboardHeroProps {
  prediction: TargetPrediction
  className?: string
}

function useCountUp(target: number, duration = 900) {
  const [value, setValue] = useState(0)
  const raf = useRef<number>(0)

  useEffect(() => {
    let start: number | null = null

    const step = (ts: number) => {
      if (!start) start = ts
      const elapsed = ts - start
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(eased * target * 10) / 10)
      if (progress < 1) {
        raf.current = requestAnimationFrame(step)
      }
    }

    raf.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf.current)
  }, [target, duration])

  return value
}

export const DashboardHero: React.FC<DashboardHeroProps> = ({
  prediction,
  className = "",
}) => {
  const probabilityPct = prediction.probability * 100
  const thresholdPct = prediction.threshold * 100
  const isPositive = prediction.probability >= prediction.threshold
  const diffPp = Math.abs((prediction.probability - prediction.threshold) * 100)

  const displayPct = useCountUp(probabilityPct)
  const { hex: barColor } = getVesselColor(prediction.probability)

  // Plain-language one-line verdict derived from existing values
  const verdict = isPositive
    ? `Above the ${thresholdPct.toFixed(0)}% decision threshold (+${diffPp.toFixed(1)} pp)`
    : `Below the ${thresholdPct.toFixed(0)}% decision threshold (-${diffPp.toFixed(1)} pp)`

  return (
    <div
      className={`instrument-surface rounded-2xl p-6 sm:p-7 select-none ${className}`}
      role="region"
      aria-label="Overall Coronary Artery Disease Risk"
    >
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span
              className={`w-2 h-2 rounded-full ${isPositive ? "bg-[#F26F69] animate-pulse" : "bg-[#2dd4bf]"}`}
              aria-hidden="true"
            />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-[#7C9692]">
              Overall Coronary Artery Disease Risk
            </h2>
          </div>

          {/* Large serif risk percentage */}
          <div className="flex items-baseline gap-2 count-up-appear">
            <span
              className="font-display text-6xl sm:text-7xl font-light tabular-nums leading-none tracking-tight text-[#E8F1EE]"
              aria-label={`${probabilityPct.toFixed(1)} percent predicted coronary artery disease risk probability`}
            >
              {displayPct.toFixed(1)}
            </span>
            <span className="font-display text-3xl sm:text-4xl text-[#7C9692] font-light">%</span>
          </div>

          {/* Plain-language one-line verdict */}
          <p className="text-xs sm:text-sm text-[#7C9692] mt-2 font-normal">
            <span className={`font-medium ${isPositive ? "text-[#F26F69]" : "text-[#2dd4bf]"}`}>
              {verdict}
            </span>
            <span className="text-[#7C9692]/70 ml-1.5">
              &bull; Model-estimated risk of significant coronary stenosis
            </span>
          </p>
        </div>

        {/* Small Model Info popover */}
        <div className="sm:self-start">
          <ModelInfoPopover prediction={prediction} />
        </div>
      </div>

      {/* Slim horizontal risk bar with decision threshold marker */}
      <div className="mt-5 space-y-1.5">
        <div
          className="relative h-2 w-full rounded-full bg-[#0A1514] overflow-hidden"
          role="progressbar"
          aria-valuenow={probabilityPct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Risk bar showing ${probabilityPct.toFixed(1)}%`}
        >
          <div
            className="absolute inset-y-0 left-0 rounded-full risk-bar-fill transition-all duration-700"
            style={{ width: `${probabilityPct}%`, background: barColor }}
          />
          {/* Threshold marker tick */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-[#E8F1EE] shadow-sm z-10"
            style={{ left: `${thresholdPct}%` }}
            title={`Decision threshold: ${thresholdPct.toFixed(0)}%`}
            aria-hidden="true"
          />
        </div>

        <div className="flex justify-between text-[11px] font-mono text-[#7C9692] px-0.5">
          <span>0%</span>
          <span className="text-[#E8F1EE]/80">Decision threshold: {thresholdPct.toFixed(0)}%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  )
}
