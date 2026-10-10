import React, { useState, Suspense, useEffect, useMemo, useCallback } from "react"
import { Canvas } from "@react-three/fiber"
import { Info, SlidersHorizontal } from "lucide-react"
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
    setVisibility((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleSelectPreset = (preset: ViewPreset) => {
    setPresetTrigger({ preset, timestamp: Date.now() })
  }

  const handleSelectVessel = (id: CoronaryVesselId | null) => {
    setInternalFocused(id)
    if (id) {
      setDismissedTarget(null)
      onSelectTarget?.(id)
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
        camPosition: [0, -6, 96],
      },
    ]

    if (predictions?.lad) {
      steps.push({
        id: "lad",
        title: "Left Anterior Descending (LAD)",
        subtitle: "Anterior Myocardium & Septum",
        description: `LAD supplies the critical anterior myocardial wall. Model estimates a ${(predictions.lad.probability * 100).toFixed(0)}% stenosis probability vs a ${(predictions.lad.threshold * 100).toFixed(0)}% threshold.`,
        target: "lad",
        camPosition: [14, -8, 64],
      })
    }

    if (predictions?.lcx) {
      steps.push({
        id: "lcx",
        title: "Left Circumflex (LCX)",
        subtitle: "Lateral & Posterior Left Ventricle",
        description: `LCX traverses the atrioventricular groove. Model estimates a ${(predictions.lcx.probability * 100).toFixed(0)}% stenosis probability vs a ${(predictions.lcx.threshold * 100).toFixed(0)}% threshold.`,
        target: "lcx",
        camPosition: [52, -4, 54],
      })
    }

    if (predictions?.rca) {
      steps.push({
        id: "rca",
        title: "Right Coronary Artery (RCA)",
        subtitle: "Inferior Wall & Right Ventricle",
        description: `RCA perfuses the inferior myocardium and nodal conduction tissue. Model estimates a ${(predictions.rca.probability * 100).toFixed(0)}% stenosis probability vs a ${(predictions.rca.threshold * 100).toFixed(0)}% threshold.`,
        target: "rca",
        camPosition: [-44, -8, 62],
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
      className={`relative overflow-hidden bg-white flex flex-col justify-between select-none ${className}`}
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

      {/* Subtle crisp clinical vignette overlay */}
      <div
        className="absolute inset-0 pointer-events-none z-[1]"
        style={{
          background:
            "radial-gradient(ellipse at 50% 45%, #ffffff 55%, #f1f5f9 100%)",
        }}
        aria-hidden="true"
      />

      {/* Main 3D Canvas Area */}
      <div className="absolute inset-0">
        <ViewerErrorBoundary>
          <Suspense fallback={<ViewerLoadingFallback className="h-full w-full rounded-none border-0 bg-white text-slate-800" />}>
            <Canvas
              camera={{ position: [0, -6, 96], fov: 36, near: 0.5, far: 500 }}
              dpr={[1, 2]}
              gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
              className="w-full h-full cursor-grab active:cursor-grabbing"
            >
              <color attach="background" args={["#ffffff"]} />
              <CoronaryScene
                predictions={predictions}
                selectedTarget={selectedTarget}
                focusedVessel={effectiveFocusedVessel}
                visibility={visibility}
                presetTrigger={presetTrigger}
                onSelectVessel={handleSelectVessel}
                onHoverVessel={setHoveredVessel}
              />
            </Canvas>
          </Suspense>
        </ViewerErrorBoundary>
      </div>

      {/* Top HUD: Quiet Anatomy Badge, Clinical Note Tooltip, Simulator Link */}
      <div className="absolute top-3 left-3 right-3 z-20 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Illustrative Anatomy Badge */}
          <div className="instrument-surface rounded-xl px-3 py-1.5 flex items-center gap-2 text-xs text-[#E8F1EE] shadow-lg">
            <span className="w-1.5 h-1.5 rounded-full bg-[#2dd4bf]" aria-hidden="true" />
            <span className="font-medium tracking-tight">Illustrative anatomy</span>
          </div>

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
