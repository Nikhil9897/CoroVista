import React from "react"
import { ChevronLeft, ChevronRight, X, Sparkles, CheckCircle2 } from "lucide-react"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import type { ExplanationResponse } from "@/types/explanation"
import { VESSEL_NAMES, getVesselColor } from "@/lib/vesselColors"

export interface TourStep {
  id: "overall" | "lad" | "lcx" | "rca"
  title: string
  subtitle: string
  description: string
  target?: TargetName
  camPosition: [number, number, number]
}

interface GuidedTourOverlayProps {
  currentStepIndex: number
  totalSteps: number
  activeStep: TourStep
  predictions?: PredictionResponse["predictions"]
  explanations?: Record<string, ExplanationResponse>
  onNext: () => void
  onPrev: () => void
  onClose: () => void
  className?: string
}

export const GuidedTourOverlay: React.FC<GuidedTourOverlayProps> = ({
  currentStepIndex,
  totalSteps,
  activeStep,
  predictions,
  onNext,
  onPrev,
  onClose,
  className = "",
}) => {
  const isOverall = activeStep.id === "overall"
  const vesselKey = !isOverall ? (activeStep.id as "lad" | "lcx" | "rca") : null
  const vesselMeta = vesselKey ? VESSEL_NAMES[vesselKey] : null
  const vesselPred = vesselKey && predictions ? predictions[vesselKey] : null
  const cathPred = predictions?.cath

  const currentProb = vesselPred ? vesselPred.probability : isOverall && cathPred ? cathPred.probability : 0
  const currentThresh = vesselPred ? vesselPred.threshold : isOverall && cathPred ? cathPred.threshold : 0.5
  const { hex: colorHex } = getVesselColor(currentProb)

  const isLastStep = currentStepIndex === totalSteps - 1

  return (
    <div
      className={`guided-tour-in instrument-surface rounded-2xl p-4 sm:p-5 w-80 sm:w-96 shadow-2xl border border-[#7C9692]/30 select-none text-left z-30 ${className}`}
      role="region"
      aria-label={`Guided explanation step ${currentStepIndex + 1} of ${totalSteps}: ${activeStep.title}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2 pb-2.5 border-b border-[#7C9692]/15">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-full bg-[#F26F69]/20 flex items-center justify-center text-[#F26F69]">
            <Sparkles className="w-3 h-3" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-[#7C9692] uppercase tracking-wider block leading-tight">
              Guided Tour &bull; Step {currentStepIndex + 1} of {totalSteps}
            </span>
            <h4 className="font-semibold text-xs text-[#E8F1EE] leading-tight">
              {activeStep.title}
            </h4>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-lg text-[#7C9692] hover:text-[#E8F1EE] hover:bg-[#112321] transition-colors cursor-pointer"
          title="Close Tour (Esc)"
          aria-label="Close guided tour"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body content */}
      <div className="py-3 space-y-2.5 text-xs">
        {/* Metric banner */}
        <div className="flex items-baseline justify-between p-2.5 rounded-xl bg-[#0A1514]/70 border border-[#7C9692]/15">
          <span className="text-[11px] text-[#7C9692]">
            {isOverall ? "CAD Probability:" : `${vesselMeta?.short} Stenosis Risk:`}
          </span>
          <div className="flex items-baseline gap-1.5">
            <span
              className="font-display text-2xl font-light tabular-nums leading-none"
              style={{ color: colorHex }}
            >
              {(currentProb * 100).toFixed(0)}%
            </span>
            <span className="text-[10px] font-mono text-[#7C9692]">
              (threshold: {(currentThresh * 100).toFixed(0)}%)
            </span>
          </div>
        </div>

        {/* Narrative explanation */}
        <p className="text-xs text-[#E8F1EE]/90 leading-relaxed font-normal">
          {activeStep.description}
        </p>

        {/* Territory or driver note */}
        {vesselMeta && (
          <div className="text-[11px] text-[#7C9692] flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3 text-[#2dd4bf] shrink-0" />
            <span>Perfusion Territory: {vesselMeta.territory}</span>
          </div>
        )}
      </div>

      {/* Stepper Footer Controls */}
      <div className="pt-2.5 border-t border-[#7C9692]/15 flex items-center justify-between gap-2">
        <button
          onClick={onPrev}
          disabled={currentStepIndex === 0}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#7C9692] hover:text-[#E8F1EE] hover:bg-[#112321] transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label="Previous step"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          <span>Back</span>
        </button>

        {/* Step dots */}
        <div className="flex items-center gap-1.5">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <span
              key={i}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                i === currentStepIndex
                  ? "bg-[#F26F69] w-4"
                  : "bg-[#7C9692]/30"
              }`}
              aria-hidden="true"
            />
          ))}
        </div>

        <button
          onClick={isLastStep ? onClose : onNext}
          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#F26F69] text-[#0A1514] hover:bg-[#F26F69]/90 transition-all cursor-pointer shadow-sm"
          aria-label={isLastStep ? "Finish tour" : "Next step"}
        >
          <span>{isLastStep ? "Finish" : "Next"}</span>
          {!isLastStep && <ChevronRight className="w-3.5 h-3.5" />}
        </button>
      </div>
    </div>
  )
}
