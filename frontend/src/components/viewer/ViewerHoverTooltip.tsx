import React from "react"
import { formatPercent } from "@/lib/utils"
import type { HoveredVesselInfo } from "./ViewerTypes"
import { getVesselColor } from "@/lib/vesselColors"

interface ViewerHoverTooltipProps {
  info: HoveredVesselInfo | null
}

export const ViewerHoverTooltip: React.FC<ViewerHoverTooltipProps> = ({ info }) => {
  if (!info) return null

  const { hex } = getVesselColor(info.probability)

  return (
    <div
      className="pointer-events-none absolute top-3 left-3 z-30 bg-card/95 backdrop-blur-md border border-border/80 rounded-lg p-3 shadow-lg max-w-[240px] text-xs space-y-1.5 animate-in fade-in-50 duration-150"
      role="tooltip"
      aria-label={`${info.short} hover details`}
    >
      <div className="flex items-center justify-between gap-2 border-b border-border/60 pb-1.5">
        <div className="flex items-center gap-1.5">
          <span
            className="w-2.5 h-2.5 rounded-full inline-block shadow-sm"
            style={{ backgroundColor: hex }}
          />
          <span className="font-bold text-foreground text-sm tracking-tight">{info.short}</span>
        </div>
        <span
          className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded ${
            info.isStenotic
              ? "bg-destructive/15 text-destructive border border-destructive/20"
              : "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
          }`}
        >
          {info.isStenotic ? "Stenotic" : "Non-Stenotic"}
        </span>
      </div>

      <div className="text-[11px] text-muted-foreground leading-tight">{info.full}</div>

      <div className="pt-1 flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Predicted Risk:</span>
        <span className="font-mono font-bold text-foreground text-sm" style={{ color: hex }}>
          {formatPercent(info.probability)}
        </span>
      </div>

      <div className="flex items-center justify-between text-[10px] text-muted-foreground">
        <span>Decision Threshold:</span>
        <span className="font-mono text-foreground">{formatPercent(info.threshold)}</span>
      </div>

      <div className="text-[10px] text-muted-foreground/80 italic pt-0.5 border-t border-border/40">
        {info.territory}
      </div>
    </div>
  )
}
