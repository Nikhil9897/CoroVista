import React, { useState, Suspense, useEffect, useMemo, useCallback } from "react"
import { Canvas } from "@react-three/fiber"
import { Info, SlidersHorizontal, RotateCcw } from "lucide-react"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import type { ExplanationResponse } from "@/types/explanation"
import type {
  CoronaryVesselId,
  HoveredVesselInfo,
  ViewerVisibilityState,
  ViewPreset,
} from "./ViewerTypes"
import { CoronaryScene } from "./CoronaryScene"
import { ViewerControls } from "./ViewerControls"
import { ViewerHoverTooltip } from "./ViewerHoverTooltip"
import { ViewerLoadingFallback } from "./ViewerLoadingFallback"
import { ViewerErrorBoundary } from "./ViewerErrorBoundary"
import { VesselFocusDetail } from "./VesselFocusDetail"
import { GuidedTourOverlay, type TourStep } from "./GuidedTourOverlay"

export interface CoronaryViewerProps {
  predictions?: PredictionResponse["predictions"]
  explanations?: Record<string, ExplanationResponse>
  selectedTarget?: TargetName | null
  onSelectTarget?: (target: TargetName) => void
  onOpenSimulator?: () => void
  className?: string
}

export const CoronaryViewer: React.FC<CoronaryViewerProps> = ({
  predictions,
  explanations,
  selectedTarget,
  onSelectTarget,
  onOpenSimulator,
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
  const [internalFocused, setInternalFocused] = useState<CoronaryVesselId | null>(null)
  const [dismissedTarget, setDismissedTarget] = useState<string | null>(null)
  const [dismissedLabels, setDismissedLabels] = useState<Set<CoronaryVesselId>>(new Set())
  const [tourActive, setTourActive] = useState<boolean>(false)
  const [tourStepIndex, setTourStepIndex] = useState<number>(0)
  const [showClinicalTooltip, setShowClinicalTooltip] = useState<boolean>(false)

  // Derive active focused vessel without cascading render effects
  const effectiveFocusedVessel: CoronaryVesselId | null = useMemo(() => {
    if (internalFocused) return internalFocused
    if (
      selectedTarget &&
      (selectedTarget === "lad" || selectedTarget === "lcx" || selectedTarget === "rca") &&
      selectedTarget !== dismissedTarget
    ) {
      return selectedTarget as CoronaryVesselId
    }
    return null
  }, [internalFocused, selectedTarget, dismissedTarget])

  // Escape key handler to exit focus or tour
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setInternalFocused(null)
        setDismissedTarget(selectedTarget ?? null)
        setTourActive(false)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [selectedTarget])

  const handleToggleVisibility = (key: keyof ViewerVisibilityState) => {
    setVisibility((prev) => {
      const next = { ...prev, [key]: !prev[key] }
      // Re-show vessel callout box if visibility is toggled back on
      if (next[key] && (key === "lad" || key === "lcx" || key === "rca")) {
        setDismissedLabels((curr) => {
          if (!curr.has(key)) return curr
          const updated = new Set(curr)
          updated.delete(key)
          return updated
        })
      }
      return next
    })
  }

  const handleSelectPreset = (preset: ViewPreset) => {
    setPresetTrigger({ preset, timestamp: Date.now() })
    if (preset === "reset") {
      setDismissedLabels(new Set())
    }
  }

  const handleDismissLabel = useCallback((id: CoronaryVesselId) => {
    setDismissedLabels((prev) => new Set(prev).add(id))
  }, [])

  const handleRestoreLabels = useCallback(() => {
    setDismissedLabels(new Set())
  }, [])

  const handleSelectVessel = (id: CoronaryVesselId | null) => {
    setInternalFocused(id)
    if (id) {
      setDismissedTarget(null)
      onSelectTarget?.(id)
      // If the selected vessel box was dismissed, restore it on user click
      setDismissedLabels((prev) => {
        if (!prev.has(id)) return prev
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    } else {
      setDismissedTarget(selectedTarget ?? null)
    }
  }

  // Define guided tour steps
  const tourSteps: TourStep[] = useMemo(() => {
    const steps: TourStep[] = [
      {
        id: "overall",
        title: "Overall CAD Risk Synthesis",
        subtitle: "Global Catheterization Stenosis Risk",
        description:
          predictions?.cath
            ? `Multivariate XGBoost models evaluate global CAD risk at ${(predictions.cath.probability * 100).toFixed(0)}%, ${
                predictions.cath.probability >= predictions.cath.threshold ? "above" : "below"
              } the ${(predictions.cath.threshold * 100).toFixed(0)}% decision threshold.`
            : "Global CAD risk evaluation derived from patient baseline biomarkers and clinical presentation.",
        camPosition: [0, -5, 215],
      },
    ]

    if (predictions?.lad) {
      steps.push({
        id: "lad",
        title: "Left Anterior Descending (LAD)",
        subtitle: "Anterior Myocardium & Septum",
        description: `LAD supplies the critical anterior myocardial wall. Model estimates a ${(predictions.lad.probability * 100).toFixed(0)}% stenosis probability vs a ${(predictions.lad.threshold * 100).toFixed(0)}% threshold.`,
        target: "lad",
        camPosition: [45, -15, 195],
      })
    }

    if (predictions?.lcx) {
      steps.push({
        id: "lcx",
        title: "Left Circumflex (LCX)",
        subtitle: "Lateral & Posterior Left Ventricle",
        description: `LCX traverses the atrioventricular groove. Model estimates a ${(predictions.lcx.probability * 100).toFixed(0)}% stenosis probability vs a ${(predictions.lcx.threshold * 100).toFixed(0)}% threshold.`,
        target: "lcx",
        camPosition: [150, -5, 145],
      })
    }

    if (predictions?.rca) {
      steps.push({
        id: "rca",
        title: "Right Coronary Artery (RCA)",
        subtitle: "Inferior Wall & Right Ventricle",
        description: `RCA perfuses the inferior myocardium and nodal conduction tissue. Model estimates a ${(predictions.rca.probability * 100).toFixed(0)}% stenosis probability vs a ${(predictions.rca.threshold * 100).toFixed(0)}% threshold.`,
        target: "rca",
        camPosition: [-130, -5, 165],
      })
    }

    return steps
  }, [predictions])

  const handleStartTour = useCallback(() => {
    setTourActive(true)
    setTourStepIndex(0)
    setInternalFocused(null)
    setPresetTrigger({ preset: "ap", timestamp: Date.now() })
  }, [])

  const handleNextTourStep = useCallback(() => {
    if (tourStepIndex < tourSteps.length - 1) {
      const nextIndex = tourStepIndex + 1
      setTourStepIndex(nextIndex)
      const nextStep = tourSteps[nextIndex]
      if (nextStep.target) {
        setInternalFocused(nextStep.target as CoronaryVesselId)
        onSelectTarget?.(nextStep.target)
      } else {
        setInternalFocused(null)
        setPresetTrigger({ preset: "ap", timestamp: Date.now() })
      }
    } else {
      setTourActive(false)
      setInternalFocused(null)
    }
  }, [tourStepIndex, tourSteps, onSelectTarget])

  const handlePrevTourStep = useCallback(() => {
    if (tourStepIndex > 0) {
      const prevIndex = tourStepIndex - 1
      setTourStepIndex(prevIndex)
      const prevStep = tourSteps[prevIndex]
      if (prevStep.target) {
        setInternalFocused(prevStep.target as CoronaryVesselId)
        onSelectTarget?.(prevStep.target)
      } else {
        setInternalFocused(null)
        setPresetTrigger({ preset: "ap", timestamp: Date.now() })
      }
    }
  }, [tourStepIndex, tourSteps, onSelectTarget])

  const activeTourStep = tourSteps[tourStepIndex]

  // Accessibility text summary
  const accessibleSummary = useMemo(() => {
    if (!predictions) return "Coronary artery 3D anatomy visualization with no patient loaded."
    return `3D Coronary Anatomy Model: Overall CAD probability is ${(predictions.cath.probability * 100).toFixed(0)}%. ` +
      `LAD predicted stenosis risk: ${(predictions.lad.probability * 100).toFixed(0)}% (threshold ${(predictions.lad.threshold * 100).toFixed(0)}%). ` +
      `LCX predicted stenosis risk: ${(predictions.lcx.probability * 100).toFixed(0)}% (threshold ${(predictions.lcx.threshold * 100).toFixed(0)}%). ` +
      `RCA predicted stenosis risk: ${(predictions.rca.probability * 100).toFixed(0)}% (threshold ${(predictions.rca.threshold * 100).toFixed(0)}%).`
  }, [predictions])

  return (
    <div
      className={`relative overflow-hidden bg-[#021315] flex flex-col justify-between select-none ${className}`}
      role="region"
      aria-label="Interactive 3D Coronary Anatomy Model"
    >
      {/* Screen-reader accessible summary and clinical note */}
      <div className="sr-only" aria-live="polite">
        <span>Interactive 3D Coronary Anatomy</span>
        <span>{accessibleSummary}</span>
      </div>
      <div role="note" className="sr-only">
        Vessel colors represent model-predicted stenosis probability, not physical lesion location.
      </div>

      {/* Subtle depth vignette overlay (ambient edges, crystal clear center) */}
      <div
        className="absolute inset-0 pointer-events-none z-10"
        style={{
          background:
            "radial-gradient(ellipse at 50% 50%, transparent 45%, rgba(2, 19, 21, 0.45) 80%, rgba(1, 10, 11, 0.85) 100%)",
        }}
        aria-hidden="true"
      />

      {/* Main 3D Canvas Area */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,#082427_0%,#031416_60%,#010a0b_100%)]">
        <ViewerErrorBoundary>
          <Suspense fallback={<ViewerLoadingFallback className="h-full w-full rounded-none border-0 bg-[#021315] text-[#E8F1EE]" />}>
            <Canvas
              camera={{ position: [0, -5, 210], fov: 45, near: 0.5, far: 800 }}
              dpr={[1, 2]}
              gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
              className="w-full h-full cursor-grab active:cursor-grabbing"
            >
              <CoronaryScene
                predictions={predictions}
                selectedTarget={selectedTarget}
                focusedVessel={effectiveFocusedVessel}
                visibility={visibility}
                presetTrigger={presetTrigger}
                dismissedLabels={dismissedLabels}
                onDismissLabel={handleDismissLabel}
                onSelectVessel={handleSelectVessel}
                onHoverVessel={setHoveredVessel}
              />
            </Canvas>
          </Suspense>
        </ViewerErrorBoundary>
      </div>

      {/* Top HUD: Quiet Anatomy Badge, Restore Boxes Button, Clinical Note Tooltip, Simulator Link */}
      <div className="absolute top-3 left-3 right-3 z-20 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Illustrative Anatomy Badge */}
          <div className="instrument-surface rounded-xl px-3 py-1.5 flex items-center gap-2 text-xs text-[#E8F1EE] shadow-lg">
            <span className="w-1.5 h-1.5 rounded-full bg-[#2dd4bf]" aria-hidden="true" />
            <span className="font-medium tracking-tight">Illustrative anatomy</span>
          </div>

          {/* Restore Closed Labels Button (visible when any text box has been closed) */}
          {dismissedLabels.size > 0 && (
            <button
              type="button"
              onClick={handleRestoreLabels}
              className="instrument-surface rounded-xl px-2.5 py-1.5 text-xs text-[#2dd4bf] hover:text-[#E8F1EE] hover:border-[#2dd4bf]/40 flex items-center gap-1.5 transition-all cursor-pointer shadow-lg"
              title="Restore closed diagnostic text boxes"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Restore boxes ({dismissedLabels.size})</span>
            </button>
          )}

          {/* Clinical Note Info Button & Tooltip */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowClinicalTooltip(!showClinicalTooltip)}
              onMouseEnter={() => setShowClinicalTooltip(true)}
              onMouseLeave={() => setShowClinicalTooltip(false)}
              className="instrument-surface rounded-xl p-1.5 text-[#7C9692] hover:text-[#E8F1EE] transition-colors cursor-pointer"
              title="Clinical Note"
              aria-label="Clinical disclaimer note"
            >
              <Info className="w-3.5 h-3.5 text-[#2dd4bf]" />
            </button>

            {showClinicalTooltip && (
              <div
                className="absolute left-0 top-full mt-2 w-72 instrument-surface rounded-xl p-3 text-[11px] text-[#7C9692] shadow-2xl z-50 animate-in fade-in duration-150 leading-relaxed border border-[#7C9692]/25"
                role="note"
              >
                <strong className="text-[#E8F1EE] block mb-1">Clinical Note:</strong>
                Vessel colors represent model-predicted stenosis probability, not physical lesion location.
              </div>
            )}
          </div>
        </div>

        {/* Simulator Link button (for Dashboard) */}
        {onOpenSimulator && (
          <button
            type="button"
            onClick={onOpenSimulator}
            className="instrument-surface rounded-xl px-3 py-1.5 flex items-center gap-2 text-xs text-[#E8F1EE] hover:border-[#F26F69]/40 hover:text-[#F26F69] transition-all cursor-pointer pointer-events-auto shadow-lg"
            title="Open interactive Patient Simulator"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Open simulator</span>
          </button>
        )}
      </div>

      {/* Focus Mode Detail Panel (Anchored Beside the Model) */}
      {effectiveFocusedVessel && !tourActive && (
        <div className="absolute top-14 right-4 z-30 pointer-events-auto max-w-[calc(100vw-32px)]">
          <VesselFocusDetail
            vesselId={effectiveFocusedVessel}
            prediction={predictions?.[effectiveFocusedVessel]}
            explanation={explanations?.[effectiveFocusedVessel] || explanations?.cath}
            isPerVesselShap={Boolean(explanations?.[effectiveFocusedVessel])}
            onClose={() => handleSelectVessel(null)}
          />
        </div>
      )}

      {/* Guided Tour Overlay Panel */}
      {tourActive && activeTourStep && (
        <div className="absolute top-14 right-4 z-30 pointer-events-auto max-w-[calc(100vw-32px)]">
          <GuidedTourOverlay
            currentStepIndex={tourStepIndex}
            totalSteps={tourSteps.length}
            activeStep={activeTourStep}
            predictions={predictions}
            onNext={handleNextTourStep}
            onPrev={handlePrevTourStep}
            onClose={() => {
              setTourActive(false)
              setInternalFocused(null)
            }}
          />
        </div>
      )}

      {/* Bottom Minimal Floating Controls Pill */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-auto">
        <ViewerControls
          visibility={visibility}
          onToggleVisibility={handleToggleVisibility}
          onSelectPreset={handleSelectPreset}
          onStartTour={predictions ? handleStartTour : undefined}
        />
      </div>

      {/* Hover Tooltip */}
      <ViewerHoverTooltip info={hoveredVessel} />
    </div>
  )
}
