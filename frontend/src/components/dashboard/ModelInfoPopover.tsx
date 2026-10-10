import React, { useState, useRef, useEffect } from "react"
import { Info, X, ShieldCheck } from "lucide-react"
import type { TargetPrediction } from "@/types/prediction"

interface ModelInfoPopoverProps {
  prediction?: TargetPrediction
  className?: string
}

export const ModelInfoPopover: React.FC<ModelInfoPopoverProps> = ({
  prediction,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const popoverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside)
    }
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [isOpen])

  return (
    <div className={`relative inline-block ${className}`} ref={popoverRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs text-[#7C9692] hover:text-[#E8F1EE] bg-[#0A1514]/60 hover:bg-[#112321] border border-[#7C9692]/15 transition-colors cursor-pointer"
        aria-expanded={isOpen}
        aria-label="Model specification and calibration details"
      >
        <Info className="w-3.5 h-3.5 text-[#F26F69]" />
        <span>Model info</span>
      </button>

      {isOpen && (
        <div
          className="absolute right-0 bottom-full mb-2 w-72 instrument-surface rounded-xl p-3.5 shadow-2xl z-50 text-left border border-[#7C9692]/25 animate-in fade-in zoom-in-95 duration-150"
          role="dialog"
          aria-label="Model Specifications"
        >
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#7C9692]/15">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#E8F1EE]">
              <ShieldCheck className="w-3.5 h-3.5 text-[#2dd4bf]" />
              <span>Model Specifications</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-[#7C9692] hover:text-[#E8F1EE] p-0.5"
              aria-label="Close"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-[#7C9692]">Architecture:</span>
              <span className="text-[#E8F1EE] font-mono font-medium">
                {prediction?.model_family ?? "XGBoost (54 feats)"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#7C9692]">Probability Calibration:</span>
              <span className="text-[#E8F1EE] font-mono font-medium">
                {prediction?.calibration ?? "Platt Sigmoid"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#7C9692]">Decision Boundary:</span>
              <span className="text-[#E8F1EE] font-mono font-medium">
                &theta; = {prediction ? (prediction.threshold * 100).toFixed(0) : "50"}%
              </span>
            </div>
            <div className="pt-2 border-t border-[#7C9692]/10 text-[10px] text-[#7C9692] leading-relaxed">
              Derived from Z-Alizadeh Sani coronary angiography cohort with stratified cross-validation.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
