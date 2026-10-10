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
      className="pointer-events-none absolute top-16 left-4 z-30 glass-panel-strong rounded-xl p-3 shadow-spatial-lg max-w-[260px] text-xs space-y-1.5 animate-in fade-in-50 duration-150 border border-border/80"
      role="tooltip"
      aria-label={`${info.short} hover details`}
    >
      <div className="flex items-center justify-between gap-2 border-b border-border/40 pb-1.5">
        <div className="flex items-center gap-1.5">
          <span
            className="w-2.5 h-2.5 rounded-full inline-block shadow-sm"
            style={{ backgroundColor: hex }}
          />
          <span className="font-bold text-foreground text-sm tracking-tight">{info.short}</span>
        </div>
        <span
          className={`text-[10px] font-semibold uppercase font-mono px-1.5 py-0.5 rounded ${
            info.isStenotic
              ? "bg-rose-500/15 text-rose-400 border border-rose-500/25"
              : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/25"
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

      <div className="text-[10px] text-muted-foreground/80 italic pt-0.5 border-t border-border/30">
        {info.territory}
      </div>
    </div>
  )
}
