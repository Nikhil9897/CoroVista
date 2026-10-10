import React from "react"
import { Eye, EyeOff, RotateCcw, Compass } from "lucide-react"
import type { ViewerVisibilityState, ViewPreset } from "./ViewerTypes"

interface ViewerControlsProps {
  visibility: ViewerVisibilityState
  onToggleVisibility: (key: keyof ViewerVisibilityState) => void
  onSelectPreset: (preset: ViewPreset) => void
  className?: string
}

export const ViewerControls: React.FC<ViewerControlsProps> = ({
  visibility,
  onToggleVisibility,
  onSelectPreset,
  className = "",
}) => {
  return (
    <div
      className={`flex flex-wrap items-center justify-between gap-2.5 rounded-xl px-3 py-2 text-xs select-none ${className}`}
      role="toolbar"
      aria-label="3D Viewer Controls"
    >
      {/* Vessel visibility toggles */}
      <div className="flex items-center gap-1.5">
        <span className="text-[10px] font-mono tracking-wider text-muted-foreground uppercase mr-0.5">
          Layers:
        </span>
        {(["lad", "lcx", "rca"] as const).map((vKey) => {
          const isVisible = visibility[vKey]
          return (
            <button
              key={vKey}
              type="button"
              onClick={() => onToggleVisibility(vKey)}
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium transition-all duration-150 cursor-pointer ${
                isVisible
                  ? "bg-primary/20 text-primary border border-primary/40 shadow-xs hover:bg-primary/30"
                  : "bg-surface-2 text-muted-foreground/60 line-through border border-border/30 hover:bg-surface-3 hover:text-muted-foreground"
              }`}
              title={`Toggle ${vKey.toUpperCase()} visibility`}
              aria-pressed={isVisible}
            >
              {isVisible ? <Eye className="w-3 h-3 text-primary" /> : <EyeOff className="w-3 h-3 opacity-50" />}
              <span>{vKey.toUpperCase()}</span>
            </button>
          )
        })}

        {/* Context toggle */}
        <button
          type="button"
          onClick={() => onToggleVisibility("context")}
          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all duration-150 ml-0.5 cursor-pointer ${
            visibility.context
              ? "bg-surface-3 text-foreground border border-border/70 hover:bg-surface-4 shadow-xs"
              : "bg-surface-2 text-muted-foreground/60 line-through border border-border/30 hover:bg-surface-3 hover:text-muted-foreground"
          }`}
          title="Toggle Heart Anatomy Context (Aorta & Myocardium)"
          aria-pressed={visibility.context}
        >
          {visibility.context ? <Eye className="w-3 h-3 text-foreground/80" /> : <EyeOff className="w-3 h-3 opacity-50" />}
          <span>Context</span>
        </button>
      </div>

      {/* Preset Camera Views */}
      <div className="flex items-center gap-1 border-l border-border/40 pl-2">
        <span className="text-[10px] font-mono tracking-wider text-muted-foreground uppercase mr-1 flex items-center gap-1">
          <Compass className="w-3 h-3 text-primary/70" />
          <span>Views:</span>
        </span>
        <button
          type="button"
          onClick={() => onSelectPreset("ap")}
          className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-surface-2 hover:bg-surface-3 text-foreground/90 border border-border/40 transition-colors cursor-pointer"
          title="Anterior-Posterior (Front) view"
        >
          AP
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("rao")}
          className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-surface-2 hover:bg-surface-3 text-foreground/90 border border-border/40 transition-colors cursor-pointer"
          title="Right Anterior Oblique view (Optimal for RCA & LAD)"
        >
          RAO
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("lao")}
          className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-surface-2 hover:bg-surface-3 text-foreground/90 border border-border/40 transition-colors cursor-pointer"
          title="Left Anterior Oblique view (Optimal for LAD bifurcation)"
        >
          LAO
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("posterior")}
          className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-surface-2 hover:bg-surface-3 text-foreground/90 border border-border/40 transition-colors cursor-pointer"
          title="Posterior view (Optimal for LCX & AV groove)"
        >
          Post
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("reset")}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] bg-surface-3 hover:bg-surface-4 text-foreground border border-border/60 transition-colors ml-1 cursor-pointer"
          title="Reset camera to default view"
        >
          <RotateCcw className="w-2.5 h-2.5 text-primary" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  )
}
