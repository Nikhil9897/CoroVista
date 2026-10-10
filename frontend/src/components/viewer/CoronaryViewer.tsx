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
    setVisibility((prev) => ({ ...prev, [key]: !prev[key] }))
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
      className={`relative overflow-hidden bg-surface-0 flex flex-col justify-between ${className}`}
      role="region"
      aria-label="Interactive 3D Coronary Anatomy Model"
    >
      {/* Radial vignette overlay */}
      <div className="absolute inset-0 pointer-events-none viewer-vignette z-[1]" />

      {/* Main 3D Canvas Area — full space */}
      <div className="absolute inset-0">
        <ViewerErrorBoundary>
          <Suspense fallback={<ViewerLoadingFallback className="h-full w-full rounded-none border-0 bg-surface-0" />}>
            <Canvas
              camera={{ position: [0, -6, 96], fov: 36, near: 0.5, far: 500 }}
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
      </div>

      {/* Top HUD Bar — floating spatial controls */}
      <div className="absolute top-3 left-3 right-3 z-20 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        <div className="flex flex-wrap items-center gap-2 pointer-events-auto">
          {/* Anatomical Title Pill */}
          <div className="glass-panel rounded-lg px-3 py-1 flex items-center gap-2 text-xs font-medium text-foreground shadow-spatial-sm">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <span>Interactive 3D Coronary Anatomy</span>
          </div>

          {/* Mandatory Clinical Disclaimer Note */}
          <div
            className="glass-panel rounded-lg px-2.5 py-1 flex items-center gap-1.5 text-[10px] text-amber-300/90 shadow-spatial-sm max-w-[440px]"
            role="note"
          >
            <Info className="w-3 h-3 text-amber-400 shrink-0" />
            <span className="leading-tight">
              <strong>Clinical Note:</strong> Vessel colors represent model-predicted stenosis probability, not physical lesion location.
            </span>
          </div>
        </div>

        {/* Selected vessel indicator */}
        {selectedMeta && (
          <div className="glass-panel rounded-lg px-3 py-1 text-[11px] font-mono text-muted-foreground flex items-center gap-2 shadow-spatial-sm pointer-events-auto">
            <span className="text-foreground/60">Focus:</span>
            <strong className="text-foreground">{selectedMeta.short}</strong>
            <span className="text-muted-foreground/60 text-[10px]">({selectedMeta.territory})</span>
          </div>
        )}
      </div>

      {/* Floating Controls — bottom-left */}
      <div className="absolute bottom-4 left-4 z-20 spatial-fade-up pointer-events-auto" style={{ animationDelay: "0.15s" }}>
        <ViewerControls
          visibility={visibility}
          onToggleVisibility={handleToggleVisibility}
          onSelectPreset={handleSelectPreset}
          className="glass-panel shadow-spatial"
        />
      </div>

      {/* Floating Legend — bottom-right */}
      <div className="absolute bottom-4 right-4 z-20 max-w-[340px] spatial-fade-up pointer-events-auto" style={{ animationDelay: "0.2s" }}>
        <ViewerLegend
          predictions={predictions}
          selectedTarget={selectedTarget}
          className="glass-panel shadow-spatial"
        />
      </div>

      {/* Hover Information Tooltip */}
      <ViewerHoverTooltip info={hoveredVessel} />
    </div>
  )
}
