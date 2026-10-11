import React, { useMemo } from "react"
import { Html } from "@react-three/drei"
import * as THREE from "three"
import { X } from "lucide-react"
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
  onDismiss?: (id: CoronaryVesselId) => void
}

function getVesselSentence(short: string, probability: number, threshold: number): {
  status: "Below" | "Near" | "Above"
  sentence: string
  diff: number
} {
  const probPct = Math.round(probability * 100)
  const threshPct = Math.round(threshold * 100)
  const diff = probPct - threshPct

  if (diff > 5) {
    return {
      status: "Above",
      sentence: `${short}: estimated ${probPct}% stenosis risk, above the ${threshPct}% threshold.`,
      diff,
    }
  }
  if (diff < -5) {
    return {
      status: "Below",
      sentence: `${short}: estimated ${probPct}% stenosis risk, below the ${threshPct}% threshold.`,
      diff,
    }
  }
  return {
    status: "Near",
    sentence: `${short}: estimated ${probPct}% stenosis risk, near the ${threshPct}% threshold.`,
    diff,
  }
}

// Calibrated 3D offsets so diagnostic callouts diverge cleanly away from the heart center:
// - RCA: Screen Left corridor (X_world ≈ -58, Y_world ≈ +6)
// - LCX: Screen Upper-Right corridor (X_world ≈ +58, Y_world ≈ +30)
// - LAD: Screen Lower-Right corridor (X_world ≈ +58, Y_world ≈ -30)
// Math reference with group rotation [-PI/2, 0, 0]:
// World X = c.x + offset.x
// World Y = c.z + offset.z
// World Z = -(c.y + offset.y)
const LABEL_OFFSETS: Record<CoronaryVesselId, [number, number, number]> = {
  rca: [-38, 0, 25],
  lcx: [50, -25, 45],
  lad: [32, 3, -13],
}

export const VesselFloatingLabel: React.FC<VesselFloatingLabelProps> = ({
  id,
  geometry,
  probability,
  threshold,
  isSelected,
  isAnyFocused,
  onClick,
  onDismiss,
}) => {
  const meta = VESSEL_NAMES[id]
  const { hex: colorHex } = useMemo(() => getVesselColor(probability), [probability])
  const { status, sentence, diff } = useMemo(
    () => getVesselSentence(meta.short, probability, threshold),
    [meta.short, probability, threshold]
  )

  const positions = useMemo(() => {
    if (!geometry) return null
    if (!geometry.boundingBox) geometry.computeBoundingBox()
    const box = geometry.boundingBox
    if (!box) return null
    const c = new THREE.Vector3()
    box.getCenter(c)
    const offset = LABEL_OFFSETS[id] || [0, 0, 0]
    const centerPos = [c.x, c.y, c.z] as [number, number, number]
    const anchorPos = [c.x + offset[0], c.y + offset[1], c.z + offset[2]] as [number, number, number]
    return { centerPos, anchorPos }
  }, [geometry, id])

  // Create subtle connecting leader line from vessel center to callout card
  const lineObject = useMemo(() => {
    if (!positions) return null
    const geom = new THREE.BufferGeometry()
    const pts = new Float32Array([
      positions.centerPos[0],
      positions.centerPos[1],
      positions.centerPos[2],
      positions.anchorPos[0],
      positions.anchorPos[1],
      positions.anchorPos[2],
    ])
    geom.setAttribute("position", new THREE.BufferAttribute(pts, 3))
    const mat = new THREE.LineBasicMaterial({
      color: colorHex,
      transparent: true,
      opacity: isSelected ? 0.8 : 0.4,
      depthTest: false,
    })
    return new THREE.Line(geom, mat)
  }, [positions, colorHex, isSelected])

  if (!positions) return null

  // If another vessel is in focus mode, hide this label to prevent distraction
  if (isAnyFocused && !isSelected) return null

  const probPct = Math.round(probability * 100)
  const threshPct = Math.round(threshold * 100)
  const isRightSide = id === "lad" || id === "lcx"

  return (
    <group>
      {/* 3D Anatomical Beacon Dot directly anchored on the vessel arterial branch */}
      <mesh position={positions.centerPos}>
        <sphereGeometry args={[1.5, 16, 16]} />
        <meshBasicMaterial color={colorHex} transparent opacity={0.9} depthTest={false} />
      </mesh>

      {/* Subtle leader line tracing from arterial branch outward to diagnostic card */}
      {lineObject && <primitive object={lineObject} />}

      {/* High-Clarity Floating Diagnostic Callout Card */}
      <Html
        position={positions.anchorPos}
        center
        distanceFactor={155}
        zIndexRange={[100, 0]}
        style={{ pointerEvents: "auto", transition: "all 0.3s ease" }}
      >
        <div
          onClick={(e) => {
            e.stopPropagation()
            onClick(id)
          }}
          className={`vessel-label-in group relative cursor-pointer select-none rounded-2xl p-2.5 text-left border transition-all duration-200 backdrop-blur-xl shadow-2xl ${
            isSelected
              ? "bg-[#062024]/95 border-[#2dd4bf] ring-2 ring-[#2dd4bf]/40 scale-105 shadow-[0_0_24px_rgba(45,212,191,0.3)]"
              : "bg-[#031417]/92 border-white/15 hover:border-white/35 hover:bg-[#072428]/95 shadow-[0_12px_32px_rgba(0,0,0,0.65)]"
          }`}
          style={{ width: "202px" }}
          role="button"
          tabIndex={0}
          aria-label={`${meta.short} annotation: ${sentence}`}
        >
          {/* Header Row: Vessel Tag, Clinical Stenosis Status Pill & Close Cross Button */}
          <div className="flex items-center justify-between gap-1.5 mb-1.5">
            <div className="flex items-center gap-1.5 min-w-0">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0 shadow-sm"
                style={{ backgroundColor: colorHex }}
                aria-hidden="true"
              />
              <span className="font-bold text-xs tracking-tight text-[#E8F1EE] uppercase font-mono">
                {meta.short}
              </span>
              <span className="text-[10px] text-[#7C9692] truncate hidden sm:inline">
                {id === "lad" ? "Anterior" : id === "lcx" ? "Circumflex" : "Right"}
              </span>
            </div>

            <div className="flex items-center gap-1 shrink-0">
              <span
                className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-semibold shrink-0 uppercase tracking-wide ${
                  status === "Above"
                    ? "bg-rose-500/25 text-rose-300 border border-rose-500/35"
                    : status === "Below"
                    ? "bg-emerald-500/25 text-emerald-300 border border-emerald-500/35"
                    : "bg-amber-500/25 text-amber-300 border border-amber-500/35"
                }`}
              >
                {status === "Above" ? "Stenotic" : status === "Below" ? "Normal" : "Borderline"}
              </span>

              {/* Cross button to close text box only if necessary */}
              {onDismiss && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDismiss(id)
                  }}
                  className="w-4 h-4 rounded-md text-[#7C9692] hover:text-[#E8F1EE] hover:bg-white/10 flex items-center justify-center transition-colors cursor-pointer"
                  title={`Close ${meta.short} annotation box`}
                  aria-label={`Close ${meta.short} annotation`}
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>

          {/* Metric Row: Large High-Contrast Probability & Cut-off Comparison */}
          <div className="flex items-baseline justify-between gap-2 py-0.5">
            <div className="flex items-baseline gap-1">
              <span
                className="font-display text-xl font-bold tabular-nums leading-none"
                style={{ color: colorHex }}
              >
                {probPct}%
              </span>
              <span className="text-[10px] text-[#7C9692] font-mono">risk</span>
            </div>

            <div className="text-[10px] font-mono text-right leading-tight">
              <span className="text-[#7C9692]/80 block">Cutoff {threshPct}%</span>
              <span
                className={`font-semibold block ${
                  status === "Above"
                    ? "text-rose-400"
                    : status === "Below"
                    ? "text-emerald-400"
                    : "text-amber-400"
                }`}
              >
                {diff > 0 ? `+${diff}%` : `${diff}%`}
              </span>
            </div>
          </div>

          {/* Interactive Footer */}
          <div className="mt-1.5 pt-1.5 border-t border-white/10 flex items-center justify-between text-[10px] text-[#7C9692] group-hover:text-[#E8F1EE] transition-colors">
            <span>{isSelected ? "● 3D Focused" : "Click to focus"}</span>
            <span
              className="font-mono text-xs font-bold transition-transform group-hover:translate-x-0.5"
              style={{ color: colorHex }}
            >
              &rarr;
            </span>
          </div>

          {/* Directional Pointer Notch pointing back toward the heart */}
          {isRightSide ? (
            /* For LAD & LCX on the right: notch points left toward heart */
            <div
              className="absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-2 rotate-45 border-b border-l border-white/20 bg-[#031417]"
              aria-hidden="true"
            />
          ) : (
            /* For RCA on the left: notch points right toward heart */
            <div
              className="absolute -right-1 top-1/2 -translate-y-1/2 w-2 h-2 rotate-45 border-t border-r border-white/20 bg-[#031417]"
              aria-hidden="true"
            />
          )}
        </div>
      </Html>
    </group>
  )
}
