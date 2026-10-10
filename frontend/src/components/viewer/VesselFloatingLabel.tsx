import React, { useMemo } from "react"
import { Html } from "@react-three/drei"
import * as THREE from "three"
import type { CoronaryVesselId } from "./ViewerTypes"
import { getVesselColor, VESSEL_NAMES } from "@/lib/vesselColors"

interface VesselFloatingLabelProps {
  id: CoronaryVesselId
  geometry?: THREE.BufferGeometry
  probability: number
  threshold: number
  isSelected: boolean
  isAnyFocused: boolean
  onClick: (id: CoronaryVesselId) => void
}

function getVesselSentence(short: string, probability: number, threshold: number): {
  status: "Below" | "Near" | "Above"
  sentence: string
} {
  const probPct = Math.round(probability * 100)
  const threshPct = Math.round(threshold * 100)
  const diff = probPct - threshPct

  if (diff > 5) {
    return {
      status: "Above",
      sentence: `${short}: estimated ${probPct}% stenosis risk, above the ${threshPct}% threshold.`,
    }
  }
  if (diff < -5) {
    return {
      status: "Below",
      sentence: `${short}: estimated ${probPct}% stenosis risk, below the ${threshPct}% threshold.`,
    }
  }
  return {
    status: "Near",
    sentence: `${short}: estimated ${probPct}% stenosis risk, near the ${threshPct}% threshold.`,
  }
}

// Offsets in local coordinates so labels diverge from heart center and avoid overlap
const LABEL_OFFSETS: Record<CoronaryVesselId, [number, number, number]> = {
  lad: [15, -15, 12],
  lcx: [25, 15, -8],
  rca: [-25, -10, 10],
}

export const VesselFloatingLabel: React.FC<VesselFloatingLabelProps> = ({
  id,
  geometry,
  probability,
  threshold,
  isSelected,
  isAnyFocused,
  onClick,
}) => {
  const meta = VESSEL_NAMES[id]
  const { hex: colorHex } = useMemo(() => getVesselColor(probability), [probability])
  const { status, sentence } = useMemo(
    () => getVesselSentence(meta.short, probability, threshold),
    [meta.short, probability, threshold]
  )

  const anchorPos = useMemo(() => {
    if (!geometry) return null
    if (!geometry.boundingBox) geometry.computeBoundingBox()
    const box = geometry.boundingBox
    if (!box) return null
    const c = new THREE.Vector3()
    box.getCenter(c)
    const offset = LABEL_OFFSETS[id] || [0, 0, 0]
    return [c.x + offset[0], c.y + offset[1], c.z + offset[2]] as [number, number, number]
  }, [geometry, id])

  if (!anchorPos) return null

  // If another vessel is in focus mode, hide this label to avoid distraction
  if (isAnyFocused && !isSelected) return null

  const probPct = Math.round(probability * 100)

  return (
    <Html
      position={anchorPos}
      center
      distanceFactor={90}
      zIndexRange={[100, 0]}
      style={{ pointerEvents: "auto", transition: "all 0.3s ease" }}
    >
      <div
        onClick={(e) => {
          e.stopPropagation()
          onClick(id)
        }}
        className={`vessel-label-in group relative cursor-pointer select-none rounded-xl p-2.5 text-left border transition-all duration-200 backdrop-blur-md shadow-2xl ${
          isSelected
            ? "bg-[#102422]/95 border-[#F26F69] ring-2 ring-[#F26F69]/40 scale-105"
            : "bg-[#0A1615]/90 border-[#7C9692]/25 hover:border-[#7C9692]/50 hover:bg-[#112624]/95"
        }`}
        style={{ minWidth: "190px", maxWidth: "230px" }}
        role="button"
        tabIndex={0}
        aria-label={`${meta.short} annotation: ${sentence}`}
      >
        {/* Top header row */}
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full shrink-0 shadow-xs"
              style={{ backgroundColor: colorHex }}
              aria-hidden="true"
            />
            <span className="font-semibold text-xs tracking-tight text-[#E8F1EE]">
              {meta.short}
            </span>
          </div>

          <div className="flex items-center gap-1">
            <span
              className="font-display text-sm font-normal tabular-nums leading-none"
              style={{ color: colorHex }}
            >
              {probPct}%
            </span>
            <span
              className={`text-[9px] font-mono px-1.5 py-0.2 rounded ${
                status === "Above"
                  ? "bg-rose-500/20 text-rose-300"
                  : status === "Below"
                  ? "bg-emerald-500/20 text-emerald-300"
                  : "bg-amber-500/20 text-amber-300"
              }`}
            >
              {status}
            </span>
          </div>
        </div>

        {/* Clinical sentence derived honestly from data */}
        <p className="text-[10px] text-[#7C9692] leading-snug font-normal line-clamp-2">
          {sentence}
        </p>

        {/* Interactive hint */}
        <div className="mt-1.5 pt-1 border-t border-[#7C9692]/15 flex items-center justify-between text-[9px] text-[#7C9692]/70 group-hover:text-[#E8F1EE] transition-colors">
          <span>Click to focus</span>
          <span className="font-mono text-[#F26F69]">&rarr;</span>
        </div>

        {/* Stem leader line indicator */}
        <div
          className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-2 h-2 rotate-45 border-r border-b border-[#7C9692]/25 bg-[#0A1615]"
          aria-hidden="true"
        />
      </div>
    </Html>
  )
}
