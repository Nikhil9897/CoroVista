/**
 * CoroVista — Continuous Vessel Risk Color Mapping
 *
 * Maps continuous model prediction probability [0, 1] to smooth visual colors.
 * Requirement:
 * - Continuous color/intensity mapping from 0 to 1
 * - Clear legend labelled: "Model-predicted stenosis probability"
 * - Never use binary prediction to force a vessel to 100% intensity
 * - RCA probability of 0.4005 with a 0.38 threshold remains ~40.1% intensity
 */

export interface ColorStop {
  stop: number
  color: [number, number, number] // RGB [0-255]
  hex: string
}

// Continuous clinical color ramp:
// 0.00: Normal healthy blue/teal (low probability)
// 0.35: Mild/intermediate gold-amber
// 0.60: Moderate risk orange
// 1.00: High risk crimson/red
export const RISK_COLOR_STOPS: ColorStop[] = [
  { stop: 0.0, color: [14, 165, 233], hex: "#0ea5e9" }, // Sky-500
  { stop: 0.25, color: [34, 197, 94], hex: "#22c55e" }, // Green-500
  { stop: 0.45, color: [234, 179, 8], hex: "#eab308" }, // Yellow-500
  { stop: 0.70, color: [249, 115, 22], hex: "#f97316" }, // Orange-500
  { stop: 1.0, color: [239, 68, 68], hex: "#ef4444" }, // Red-500
]

function interpolateChannel(c1: number, c2: number, t: number): number {
  return Math.round(c1 + (c2 - c1) * t)
}

/**
 * Computes continuous RGB and HEX color for any probability in [0, 1].
 * Guaranteed strictly continuous and monotonic across the scale.
 */
export function getVesselColor(prob: number): {
  hex: string
  rgb: [number, number, number]
  rgbCss: string
  normalized: [number, number, number] // [0-1] for Three.js Color
} {
  const clamped = Math.max(0, Math.min(1, prob))

  // Find surrounding color stops
  let lower = RISK_COLOR_STOPS[0]
  let upper = RISK_COLOR_STOPS[RISK_COLOR_STOPS.length - 1]

  for (let i = 0; i < RISK_COLOR_STOPS.length - 1; i++) {
    if (clamped >= RISK_COLOR_STOPS[i].stop && clamped <= RISK_COLOR_STOPS[i + 1].stop) {
      lower = RISK_COLOR_STOPS[i]
      upper = RISK_COLOR_STOPS[i + 1]
      break
    }
  }

  const span = upper.stop - lower.stop
  const t = span > 0 ? (clamped - lower.stop) / span : 0

  const r = interpolateChannel(lower.color[0], upper.color[0], t)
  const g = interpolateChannel(lower.color[1], upper.color[1], t)
  const b = interpolateChannel(lower.color[2], upper.color[2], t)

  const hex = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`

  return {
    hex,
    rgb: [r, g, b],
    rgbCss: `rgb(${r}, ${g}, ${b})`,
    normalized: [r / 255, g / 255, b / 255],
  }
}

export const VESSEL_NAMES: Record<string, { short: string; full: string; territory: string; defaultThreshold: number }> = {
  lad: {
    short: "LAD",
    full: "Left Anterior Descending",
    territory: "Anterior wall, septum & apex",
    defaultThreshold: 0.50,
  },
  lcx: {
    short: "LCX",
    full: "Left Circumflex",
    territory: "Lateral & posterior LV myocardium",
    defaultThreshold: 0.50,
  },
  rca: {
    short: "RCA",
    full: "Right Coronary Artery",
    territory: "Inferior wall, RV & conduction system",
    defaultThreshold: 0.38,
  },
}
