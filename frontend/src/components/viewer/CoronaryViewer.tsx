import React, { useState, Suspense } from "react"
import { Canvas } from "@react-three/fiber"
import { Info, Sparkles } from "lucide-react"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import type {
  CoronaryVesselId,
  HoveredVesselInfo,
  ViewerVisibilityState,
  ViewPreset,
} from "./ViewerTypes"
import { CoronaryScene } from "./CoronaryScene"
import { ViewerControls } from "./ViewerControls"
import { ViewerLegend } from "./ViewerLegend"
import { ViewerHoverTooltip } from "./ViewerHoverTooltip"
import { ViewerLoadingFallback } from "./ViewerLoadingFallback"
import { ViewerErrorBoundary } from "./ViewerErrorBoundary"
import { VESSEL_NAMES } from "@/lib/vesselColors"

export interface CoronaryViewerProps {
  predictions?: PredictionResponse["predictions"]
  selectedTarget?: TargetName
  onSelectTarget?: (target: TargetName) => void
  className?: string
}

export const CoronaryViewer: React.FC<CoronaryViewerProps> = ({
  predictions,
  selectedTarget,
  onSelectTarget,
  className = "",
}) => {
  const [visibility, setVisibility] = useState<ViewerVisibilityState>({
    lad: true,
    lcx: true,
    rca: true,
    context: true,
  })

  const [hoveredVessel, setHoveredVessel] = useState<HoveredVesselInfo | null>(null)
  const [presetTrigger, setPresetTrigger] = useState<{ preset: ViewPreset; timestamp: number } | null>(null)

  const handleToggleVisibility = (key: keyof ViewerVisibilityState) => {
    setVisibility((prev) => ({ ...prev, [key]: !prev [key] }))
  }

  const handleSelectPreset = (preset: ViewPreset) => {
    setPresetTrigger({ preset, timestamp: Date.now() })
  }

  const handleSelectVessel = (id: CoronaryVesselId) => {
    onSelectTarget?.(id)
  }

  const selectedMeta = selectedTarget && selectedTarget in VESSEL_NAMES ? VESSEL_NAMES[selectedTarget] : null

  return (
    <div
      className={`border border-border/80 bg-gradient-to-br from-card/95 via-card/75 to-card/50 rounded-xl p-4 shadow-sm flex flex-col justify-between relative overflow-hidden min-h-[480px] ${className}`}
      role="region"
      aria-label="Interactive 3D Coronary Anatomy Model"
    >
      {/* Top Header: Title, Selected Pill, and Clinical Note */}
      <div className="space-y-2 z-10">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
              <span>Interactive 3D Coronary Anatomy</span>
            </h3>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="w-2.5 h-2.5" />
              <span>Continuous Risk Shaders</span>
            </span>
          </div>

          {selectedMeta && (
            <div className="text-[11px] font-mono text-muted-foreground flex items-center gap-1 bg-secondary/80 px-2 py-0.5 rounded border border-border/60">
              <span>Focus:</span>
              <strong className="text-foreground">{selectedMeta.short}</strong>
              <span className="text-[10px] text-muted-foreground/80">({selectedMeta.territory})</span>
            </div>
          )}
        </div>

        {/* Clinical Disclaimer Note */}
        <div
          className="flex items-center gap-1.5 text-[11px] text-amber-700 dark:text-amber-400/90 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1.5 rounded-lg"
          role="note"
        >
          <Info className="w-3.5 h-3.5 shrink-0" />
          <p className="leading-tight">
            <strong>Clinical Note:</strong> Vessel colors represent model-predicted stenosis probability, not physical lesion location.
          </p>
        </div>

        {/* View Controls Toolbar */}
        <ViewerControls
          visibility={visibility}
          onToggleVisibility={handleToggleVisibility}
          onSelectPreset={handleSelectPreset}
        />
      </div>

      {/* Main 3D Canvas Area */}
      <div className="relative flex-1 min-h-[340px] sm:min-h-[400px] lg:min-h-[420px] w-full my-2 rounded-lg overflow-hidden border border-border/40 bg-radial from-slate-900/10 to-slate-950/30">
        <ViewerErrorBoundary>
          <Suspense fallback={<ViewerLoadingFallback className="h-full min-h-[340px]" />}>
            <Canvas
              camera={{ position: [0, -6, 138], fov: 40, near: 1, far: 1000 }}
              dpr={[1, 2]}
              gl={{ antialias: true, alpha: true }}
              className="w-full h-full cursor-grab active:cursor-grabbing"
            >
              <CoronaryScene
                predictions={predictions}
                selectedTarget={selectedTarget}
                visibility={visibility}
                presetTrigger={presetTrigger}
                onSelectVessel={handleSelectVessel}
                onHoverVessel={setHoveredVessel}
              />
            </Canvas>
          </Suspense>
        </ViewerErrorBoundary>

        {/* Hover Information Tooltip */}
        <ViewerHoverTooltip info={hoveredVessel} />
      </div>

      {/* Bottom Footer: Continuous Probability Legend */}
      <div className="z-10 pt-1">
        <ViewerLegend
          predictions={predictions}
          selectedTarget={selectedTarget}
        />
      </div>
    </div>
  )
}
