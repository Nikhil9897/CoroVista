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
      className={`flex flex-wrap items-center justify-between gap-2 bg-card/85 backdrop-blur-md border border-border/70 rounded-lg p-2 shadow-sm text-xs ${className}`}
      role="toolbar"
      aria-label="3D Viewer Controls"
    >
      {/* Vessel visibility toggles */}
      <div className="flex items-center gap-1.5">
        <span className="text-[11px] font-medium text-muted-foreground mr-1">Vessels:</span>
        {(["lad", "lcx", "rca"] as const).map((vKey) => {
          const isVisible = visibility[vKey]
          return (
            <button
              key={vKey}
              type="button"
              onClick={() => onToggleVisibility(vKey)}
              className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-mono transition-colors ${
                isVisible
                  ? "bg-primary/10 text-primary border border-primary/30 hover:bg-primary/20"
                  : "bg-muted/50 text-muted-foreground line-through border border-transparent hover:bg-muted"
              }`}
              title={`Toggle ${vKey.toUpperCase()} visibility`}
              aria-pressed={isVisible}
            >
              {isVisible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
              <span>{vKey.toUpperCase()}</span>
            </button>
          )
        })}

        {/* Context toggle */}
        <button
          type="button"
          onClick={() => onToggleVisibility("context")}
          className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ml-1 ${
            visibility.context
              ? "bg-secondary text-foreground border border-border/60 hover:bg-secondary/80"
              : "bg-muted/50 text-muted-foreground line-through border border-transparent hover:bg-muted"
          }`}
          title="Toggle Heart Anatomy Context (Aorta & Myocardium)"
          aria-pressed={visibility.context}
        >
          {visibility.context ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
          <span>Context</span>
        </button>
      </div>

      {/* Preset Camera Views */}
      <div className="flex items-center gap-1">
        <span className="text-[11px] font-medium text-muted-foreground mr-1 flex items-center gap-0.5">
          <Compass className="w-3 h-3" />
          <span>Views:</span>
        </span>
        <button
          type="button"
          onClick={() => onSelectPreset("ap")}
          className="px-2 py-0.5 rounded text-[11px] font-mono bg-muted/60 hover:bg-muted text-foreground transition-colors"
          title="Anterior-Posterior (Front) view"
        >
          AP
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("rao")}
          className="px-2 py-0.5 rounded text-[11px] font-mono bg-muted/60 hover:bg-muted text-foreground transition-colors"
          title="Right Anterior Oblique view (Optimal for RCA & LAD)"
        >
          RAO
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("lao")}
          className="px-2 py-0.5 rounded text-[11px] font-mono bg-muted/60 hover:bg-muted text-foreground transition-colors"
          title="Left Anterior Oblique view (Optimal for LAD bifurcation)"
        >
          LAO
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("posterior")}
          className="px-2 py-0.5 rounded text-[11px] font-mono bg-muted/60 hover:bg-muted text-foreground transition-colors"
          title="Posterior view (Optimal for LCX & AV groove)"
        >
          Post
        </button>
        <button
          type="button"
          onClick={() => onSelectPreset("reset")}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-secondary hover:bg-secondary/80 text-foreground transition-colors ml-1"
          title="Reset camera to default view"
        >
          <RotateCcw className="w-2.5 h-2.5" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  )
}
