import { describe, it, expect } from "vitest"
import { getVesselColor, VESSEL_NAMES } from "@/lib/vesselColors"

describe("Continuous Vessel Risk Color Mapping", () => {
  it("provides continuous color mapping from 0 to 1 without crashing", () => {
    const p0 = getVesselColor(0.0)
    const p25 = getVesselColor(0.25)
    const p50 = getVesselColor(0.5)
    const p75 = getVesselColor(0.75)
    const p100 = getVesselColor(1.0)

    expect(p0.hex).toBeDefined()
    expect(p25.hex).toBeDefined()
    expect(p50.hex).toBeDefined()
    expect(p75.hex).toBeDefined()
    expect(p100.hex).toBeDefined()

    // 0.0 is low risk (sky/green), 1.0 is high risk (red)
    expect(p0.rgb[0]).toBeLessThan(p100.rgb[0]) // Red channel increases
    expect(p0.rgb[2]).toBeGreaterThan(p100.rgb[2]) // Blue channel decreases
  })

  it("strictly preserves the RCA example at probability 0.4005 and threshold 0.38", () => {
    const rcaProb = 0.4005
    const rcaThreshold = 0.38
    const isStenotic = rcaProb >= rcaThreshold

    expect(isStenotic).toBe(true)

    const color = getVesselColor(rcaProb)
    const red100 = getVesselColor(1.0)

    // Crucial requirement: Must NOT force binary prediction to 100% intensity
    expect(color.hex).not.toBe(red100.hex)
    expect(color.rgb[0]).toBeLessThan(red100.rgb[0]) // Not at full red intensity
    // Red channel at 40.1% should reflect intermediate gold/yellow (~220-240), not full crimson
    expect(color.rgb[0]).toBeGreaterThan(150)
    expect(color.rgb[1]).toBeGreaterThan(150) // Green channel still significant in gold/amber
  })

  it("clamps probabilities strictly to [0, 1]", () => {
    const below = getVesselColor(-0.5)
    const zero = getVesselColor(0.0)
    expect(below.hex).toBe(zero.hex)

    const above = getVesselColor(1.5)
    const one = getVesselColor(1.0)
    expect(above.hex).toBe(one.hex)
  })

  it("defines correct metadata and default thresholds for all 3 clinical targets", () => {
    expect(VESSEL_NAMES.lad.short).toBe("LAD")
    expect(VESSEL_NAMES.lad.defaultThreshold).toBe(0.46)

    expect(VESSEL_NAMES.lcx.short).toBe("LCX")
    expect(VESSEL_NAMES.lcx.defaultThreshold).toBe(0.50)

    expect(VESSEL_NAMES.rca.short).toBe("RCA")
    expect(VESSEL_NAMES.rca.defaultThreshold).toBe(0.38)
  })
})
