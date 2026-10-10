import React, { useState, useRef, useEffect } from "react"
import { RotateCcw, HelpCircle, Eye, EyeOff, Sparkles, X } from "lucide-react"
import type { ViewerVisibilityState, ViewPreset } from "./ViewerTypes"
import { RISK_COLOR_STOPS } from "@/lib/vesselColors"

interface ViewerControlsProps {
  visibility: ViewerVisibilityState
  onToggleVisibility: (key: keyof ViewerVisibilityState) => void
  onSelectPreset: (preset: ViewPreset) => void
  onStartTour?: () => void
  className?: string
}

const GRADIENT_CSS = `linear-gradient(to right, ${RISK_COLOR_STOPS.map(
  (s) => `${s.hex} ${s.stop * 100}%`
).join(", ")})`

export const ViewerControls: React.FC<ViewerControlsProps> = ({
  visibility,
  onToggleVisibility,
  onSelectPreset,
  onStartTour,
  className = "",
}) => {
  const [activePreset, setActivePreset] = useState<ViewPreset>("ap")
  const [showLegendPopover, setShowLegendPopover] = useState(false)
  const legendRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (legendRef.current && !legendRef.current.contains(e.target as Node)) {
        setShowLegendPopover(false)
      }
    }
    if (showLegendPopover) {
      document.addEventListener("mousedown", handleClickOutside)
    }
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [showLegendPopover])

  const handlePreset = (preset: ViewPreset) => {
    setActivePreset(preset)
    onSelectPreset(preset)
  }

  return (
    <div
      className={`relative inline-flex items-center gap-2 rounded-2xl px-3 py-2 text-xs select-none backdrop-blur-xl border border-slate-700/60 bg-[#0f1719]/90 shadow-2xl ${className}`}
      role="toolbar"
      aria-label="3D Anatomical Controls"
    >
      {/* 1. Guided Tour Button */}
      {onStartTour && (
        <>
          <button
            type="button"
            onClick={onStartTour}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-[#F26F69]/15 text-[#F26F69] hover:bg-[#F26F69]/25 border border-[#F26F69]/30 transition-all cursor-pointer shadow-xs active:scale-95"
            title="Start guided anatomical explanation tour"
            aria-label="Explain this model"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="font-semibold">Explain this model</span>
          </button>
          <div className="w-px h-5 bg-[#7C9692]/20 mx-0.5" aria-hidden="true" />
        </>
      )}

      {/* 2. Layer Toggles (LAD / LCX / RCA / Context) */}
      <div className="flex items-center gap-1">
        {(["lad", "lcx", "rca"] as const).map((key) => {
          const isVis = visibility[key]
          return (
            <button
              key={key}
              type="button"
              onClick={() => onToggleVisibility(key)}
              className={`px-2 py-1 rounded-lg text-[11px] font-mono transition-all cursor-pointer flex items-center gap-1 ${
                isVis
                  ? "bg-[#162C2A] text-[#E8F1EE] border border-[#7C9692]/30"
                  : "bg-transparent text-[#7C9692]/50 line-through border border-transparent hover:text-[#7C9692]"
              }`}
              title={`Toggle ${key.toUpperCase()} visibility`}
              aria-pressed={isVis}
            >
              {isVis ? <Eye className="w-3 h-3 text-[#2dd4bf]" /> : <EyeOff className="w-3 h-3" />}
              <span>{key.toUpperCase()}</span>
            </button>
          )
        })}

        {/* Context mesh toggle */}
        <button
          type="button"
          onClick={() => onToggleVisibility("context")}
          className={`px-2 py-1 rounded-lg text-[11px] transition-all cursor-pointer flex items-center gap-1 ${
            visibility.context
              ? "bg-[#162C2A] text-[#E8F1EE] border border-[#7C9692]/30"
              : "bg-transparent text-[#7C9692]/50 line-through border border-transparent hover:text-[#7C9692]"
          }`}
          title="Toggle Context Myocardium & Aorta"
          aria-label="Toggle Context Myocardium & Aorta"
          aria-pressed={visibility.context}
        >
          {visibility.context ? <Eye className="w-3 h-3 text-[#7C9692]" /> : <EyeOff className="w-3 h-3" />}
          <span className="hidden sm:inline">Context</span>
        </button>
      </div>

      <div className="w-px h-5 bg-[#7C9692]/20 mx-0.5" aria-hidden="true" />

      {/* 3. View Selector Segmented Control */}
      <div className="flex items-center gap-0.5 bg-[#071110] p-0.5 rounded-xl border border-[#7C9692]/15">
        {(
          [
            { id: "ap", label: "AP", title: "Anterior-Posterior (AP) view" },
            { id: "rao", label: "RAO", title: "Right Anterior Oblique (RAO) view" },
            { id: "lao", label: "LAO", title: "Left Anterior Oblique (LAO) view" },
            { id: "posterior", label: "Post", title: "Posterior view (Post)" },
          ] as const
        ).map((v) => (
          <button
            key={v.id}
            type="button"
            onClick={() => handlePreset(v.id)}
            className={`px-2 py-0.5 rounded-lg text-[11px] font-mono transition-colors cursor-pointer ${
              activePreset === v.id
                ? "bg-[#162C2A] text-[#E8F1EE] font-medium shadow-xs"
                : "text-[#7C9692] hover:text-[#E8F1EE]"
            }`}
            title={v.title}
          >
            {v.label}
          </button>
        ))}

        <button
          type="button"
          onClick={() => handlePreset("reset")}
          className="p-1 rounded-lg text-[#7C9692] hover:text-[#E8F1EE] hover:bg-[#162C2A] transition-colors cursor-pointer"
          title="Reset camera view"
          aria-label="Reset camera"
        >
          <RotateCcw className="w-3 h-3" />
        </button>
      </div>

      {/* 4. Tiny "?" Legend Popover */}
      <div className="relative" ref={legendRef}>
        <button
          type="button"
          onClick={() => setShowLegendPopover(!showLegendPopover)}
          className={`p-1.5 rounded-xl border transition-colors cursor-pointer ${
            showLegendPopover
              ? "bg-[#F26F69]/20 text-[#F26F69] border-[#F26F69]/40"
              : "text-[#7C9692] hover:text-[#E8F1EE] bg-[#071110] border-[#7C9692]/15"
          }`}
          title="Color spectrum legend"
          aria-label="Show color spectrum scale"
        >
          <HelpCircle className="w-3.5 h-3.5" />
        </button>

        {showLegendPopover && (
          <div
            className="absolute bottom-full right-0 mb-2 w-64 instrument-surface rounded-xl p-3 shadow-2xl border border-[#7C9692]/25 text-left z-50 animate-in fade-in duration-150"
            role="dialog"
            aria-label="Color scale legend"
          >
            <div className="flex items-center justify-between pb-1.5 mb-2 border-b border-[#7C9692]/15">
              <span className="text-[11px] font-semibold text-[#E8F1EE]">
                Predicted Stenosis Scale
              </span>
              <button
                onClick={() => setShowLegendPopover(false)}
                className="text-[#7C9692] hover:text-[#E8F1EE] p-0.5"
                aria-label="Close legend"
              >
                <X className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-1.5">
              <div
                className="h-2 w-full rounded-full border border-[#7C9692]/20"
                style={{ background: GRADIENT_CSS }}
              />
              <div className="flex justify-between text-[10px] font-mono text-[#7C9692]">
                <span>0% Low</span>
                <span>50%</span>
                <span>100% High</span>
              </div>
            </div>

            <p className="mt-2 pt-2 border-t border-[#7C9692]/10 text-[10px] text-[#7C9692] leading-tight">
              Colors represent continuous model-predicted stenosis probability (&theta; approx 0.38 - 0.50).
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
