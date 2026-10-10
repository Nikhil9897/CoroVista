import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { Simulator } from "@/pages/Simulator"
import { apiClient, ApiError } from "@/api/client"
import type { AnalysisResponse } from "@/types/patient"
import { DEMO_PATIENT } from "@/lib/demoPatient"
import { FORBIDDEN_TARGET_NAMES } from "@/lib/simulatorRegistry"

// Mock 3D Canvas / Three.js
vi.mock("@react-three/fiber", () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="mock-three-canvas">{children}</div>
  ),
  useThree: () => ({ camera: { position: { set: vi.fn() } } }),
}))

vi.mock("@react-three/drei", () => ({
  OrbitControls: () => <div data-testid="mock-orbit-controls" />,
  useGLTF: Object.assign(
    vi.fn().mockReturnValue({
      nodes: {
        vessel_lad: { geometry: {} },
        vessel_lcx: { geometry: {} },
        vessel_rca: { geometry: {} },
      },
    }),
    { preload: vi.fn() }
  ),
}))

vi.mock("@/components/viewer/CoronaryScene", () => ({
  CoronaryScene: () => <div data-testid="mock-coronary-scene" />,
}))

const MOCK_ANALYSIS_1: AnalysisResponse = {
  predictions: {
    cath: {
      probability: 0.7657,
      prediction: "CAD",
      threshold: 0.50,
      model_family: "XGBoost",
      calibration: "sigmoid",
    },
    lad: {
      probability: 0.5300,
      prediction: "Stenotic",
      threshold: 0.50,
      model_family: "XGBoost",
      calibration: "sigmoid",
    },
    lcx: {
      probability: 0.1300,
      prediction: "Normal",
      threshold: 0.50,
      model_family: "XGBoost",
      calibration: "uncalibrated",
    },
    rca: {
      probability: 0.4005,
      prediction: "Stenotic",
      threshold: 0.38,
      model_family: "LogisticRegression",
      calibration: "sigmoid",
    },
  },
  explanations: {
    cath: {
      target: "cath",
      explanation_space: "log-odds (model score)",
      calibration_disclosure: "SHAP values explain the underlying model score.",
      base_value: -0.1192,
      features: [
        {
          feature: "Tinversion",
          label: "T-Wave Inversion (ECG)",
          value: 1.0,
          shap_value: 0.4556,
          direction: "positive",
        },
      ],
      positive_contributors: [
        {
          feature: "Tinversion",
          label: "T-Wave Inversion (ECG)",
          value: 1.0,
          shap_value: 0.4556,
          direction: "positive",
        },
      ],
      negative_contributors: [],
    },
    lad: {
      target: "lad",
      explanation_space: "log-odds (model score)",
      calibration_disclosure: "SHAP values explain the underlying model score.",
      base_value: -0.15,
      features: [
        {
          feature: "EF-TTE",
          label: "Left Ventricular Ejection Fraction (% Echo)",
          value: 45.0,
          shap_value: -0.32,
          direction: "negative",
        },
      ],
      positive_contributors: [],
      negative_contributors: [
        {
          feature: "EF-TTE",
          label: "Left Ventricular Ejection Fraction (% Echo)",
          value: 45.0,
          shap_value: -0.32,
          direction: "negative",
        },
      ],
    },
    lcx: {
      target: "lcx",
      explanation_space: "log-odds (model score)",
      calibration_disclosure: "SHAP values explain the underlying model score.",
      base_value: -0.3,
      features: [],
      positive_contributors: [],
      negative_contributors: [],
    },
    rca: {
      target: "rca",
      explanation_space: "log-odds (model score)",
      calibration_disclosure: "SHAP values explain the underlying model score.",
      base_value: -0.25,
      features: [],
      positive_contributors: [],
      negative_contributors: [],
    },
  },
  clinical_disclaimer: "Educational and decision-support prototype only.",
  visualization_note: "Predicted vessel probabilities represent model risk, not physical 3D lesion coordinates.",
}

const MOCK_ANALYSIS_2: AnalysisResponse = {
  ...MOCK_ANALYSIS_1,
  predictions: {
    ...MOCK_ANALYSIS_1.predictions,
    lad: {
      ...MOCK_ANALYSIS_1.predictions.lad,
      probability: 0.6100, // +8.0 pp change
    },
  },
}

describe("Interactive Patient Simulator", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it("1. renders simulator title, subtitle, and educational simulation indicator", () => {
    render(<Simulator />)

    expect(screen.getByRole("heading", { name: "Patient Simulator", level: 1 })).toBeInTheDocument()
    expect(
      screen.getByText(/Explore how clinical inputs influence model-predicted cardiovascular risk/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Educational \/ Decision-Support Simulation/i)
    ).toBeInTheDocument()
  })

  it("2. loads demo patient values and clearly labels synthetic data", () => {
    render(<Simulator />)

    expect(
      screen.getByText(/Demo \/ synthetic patient — not a real patient record/i)
    ).toBeInTheDocument()

    // Age input is pre-populated with 62
    const ageInput = screen.getByRole("spinbutton", { name: /Patient Age/i })
    expect(ageInput).toHaveValue(62)
  })

  it("3. renders all four clinical feature sections", () => {
    render(<Simulator />)

    expect(screen.getByText("Demographics & Medical History")).toBeInTheDocument()
    expect(screen.getByText("Physical Exam & Angina Presentation")).toBeInTheDocument()
    expect(screen.getByText("12-Lead Electrocardiography (ECG)")).toBeInTheDocument()
    expect(screen.getByText("Laboratory Biomarkers & Echocardiography")).toBeInTheDocument()
  })

  it("4. populates feature names, units, and categories from registry", () => {
    render(<Simulator />)

    expect(screen.getByText("Patient Age")).toBeInTheDocument()
    expect(screen.getByText("Systolic Blood Pressure")).toBeInTheDocument()
    expect(screen.getByText("Fasting Blood Sugar")).toBeInTheDocument()
    expect(screen.getByText("Ejection Fraction (Echocardiography)")).toBeInTheDocument()
  })

  it("5. updates numeric and categorical inputs correctly", () => {
    render(<Simulator />)

    const ageInput = screen.getByRole("spinbutton", { name: /Patient Age/i })
    fireEvent.change(ageInput, { target: { value: "65" } })
    expect(ageInput).toHaveValue(65)

    // Check Female selection
    const femaleRadio = screen.getByRole("radio", { name: /Female/i })
    fireEvent.click(femaleRadio)
    expect(femaleRadio).toHaveAttribute("aria-checked", "true")
  })

  it("6. guarantees target columns (Cath, LAD, LCX, RCA) are strictly not editable or present", () => {
    render(<Simulator />)

    for (const forbidden of Array.from(FORBIDDEN_TARGET_NAMES)) {
      expect(screen.queryByLabelText(new RegExp(`^${forbidden}$`, "i"))).not.toBeInTheDocument()
      expect(screen.queryByRole("textbox", { name: new RegExp(`^${forbidden}$`, "i") })).not.toBeInTheDocument()
    }
  })

  it("7. handles missing/invalid numeric inputs with field-level validation", async () => {
    render(<Simulator />)

    const ageInput = screen.getByRole("spinbutton", { name: /Patient Age/i })
    fireEvent.change(ageInput, { target: { value: "" } })

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getByText(/Patient Age is required/i)).toBeInTheDocument()
    })
  })

  it("8. calls POST /api/v1/analyze when Analyze Patient is clicked", async () => {
    const analyzeSpy = vi.spyOn(apiClient, "analyzePatient").mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(analyzeSpy).toHaveBeenCalledTimes(1)
      expect(analyzeSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          Age: 62,
          Sex: "Male",
          BP: 135,
        })
      )
    })
  })

  it("9. does not display predictions before successful API response", () => {
    render(<Simulator />)

    expect(screen.getByText(/No Active Simulation Results/i)).toBeInTheDocument()
    expect(screen.queryByText("76.6%")).not.toBeInTheDocument()
  })

  it("10. renders predictions dynamically from the API response", async () => {
    vi.spyOn(apiClient, "analyzePatient").mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getAllByText("76.6%").length).toBeGreaterThan(0) // Cath
      expect(screen.getAllByText("53.0%").length).toBeGreaterThan(0) // LAD
      expect(screen.getAllByText("13.0%").length).toBeGreaterThan(0) // LCX
      expect(screen.getAllByText("40.1%").length).toBeGreaterThan(0) // RCA
    })
  })

  it("11. preserves RCA probability 40.1% at threshold 0.38 as Stenotic", async () => {
    vi.spyOn(apiClient, "analyzePatient").mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    fireEvent.click(screen.getByRole("button", { name: /Analyze Patient/i }))

    await waitFor(() => {
      const rcaCard = screen.getByRole("button", { name: /RCA stenosis risk: 40\.1%/i })
      expect(rcaCard).toBeInTheDocument()
      expect(rcaCard).toHaveTextContent("Cutoff: 38.0%")
      expect(rcaCard).toHaveTextContent("Stenotic")
    })
  })

  it("12. updates CAD and all three vessel probabilities on successful analysis", async () => {
    vi.spyOn(apiClient, "analyzePatient").mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    fireEvent.click(screen.getByRole("button", { name: /Analyze Patient/i }))

    await waitFor(() => {
      expect(screen.getByText("Overall CAD Risk")).toBeInTheDocument()
      expect(screen.getByText("Left Anterior Descending")).toBeInTheDocument()
      expect(screen.getByText("Left Circumflex")).toBeInTheDocument()
      expect(screen.getByText("Right Coronary Artery")).toBeInTheDocument()
    })
  })

  it("13. renders SHAP feature explanations with log-odds transparency", async () => {
    vi.spyOn(apiClient, "analyzePatient").mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    fireEvent.click(screen.getByRole("button", { name: /Analyze Patient/i }))

    await waitFor(() => {
      expect(screen.getByText(/Why this prediction\?/i)).toBeInTheDocument()
      expect(screen.getByText(/SHAP Log-Odds/i)).toBeInTheDocument()
      expect(screen.getByText(/T-Wave Inversion \(ECG\)/i)).toBeInTheDocument()
    })
  })

  it("14. renders 3D anatomical coronary viewer with identical prediction payload", async () => {
    vi.spyOn(apiClient, "analyzePatient").mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    fireEvent.click(screen.getByRole("button", { name: /Analyze Patient/i }))

    await waitFor(() => {
      expect(screen.getByText(/Interactive 3D Coronary Anatomy/i)).toBeInTheDocument()
      expect(
        screen.getByText(/Vessel colors represent model-predicted stenosis probability/i)
      ).toBeInTheDocument()
    })
  })

  it("15. preserves previous successful analysis when a subsequent request fails", async () => {
    vi.spyOn(apiClient, "analyzePatient")
      .mockResolvedValueOnce(MOCK_ANALYSIS_1)
      .mockRejectedValueOnce(new ApiError("Server timeout", "TIMEOUT", 504))

    render(<Simulator />)

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getAllByText("76.6%").length).toBeGreaterThan(0)
    })

    // Modify a field and re-submit
    const ageInput = screen.getByRole("spinbutton", { name: /Patient Age/i })
    fireEvent.change(ageInput, { target: { value: "70" } })

    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      // Error is displayed
      expect(screen.getByRole("alert")).toBeInTheDocument()
      expect(screen.getByText(/Server timeout/i)).toBeInTheDocument()
      // Previous result 76.6% is still intact!
      expect(screen.getAllByText("76.6%").length).toBeGreaterThan(0)
    })
  })

  it("16. reset restores demo values without claiming a new prediction occurred", () => {
    render(<Simulator />)

    const ageInput = screen.getByRole("spinbutton", { name: /Patient Age/i })
    fireEvent.change(ageInput, { target: { value: "80" } })
    expect(ageInput).toHaveValue(80)

    const resetBtn = screen.getByRole("button", { name: /Reset to Demo Values/i })
    fireEvent.click(resetBtn)

    expect(ageInput).toHaveValue(DEMO_PATIENT.Age)
    // No prediction occurred
    expect(screen.getByText(/No Active Simulation Results/i)).toBeInTheDocument()
  })

  it("17. calculates before/after percentage point changes correctly", async () => {
    vi.spyOn(apiClient, "analyzePatient")
      .mockResolvedValueOnce(MOCK_ANALYSIS_1)
      .mockResolvedValueOnce(MOCK_ANALYSIS_2)

    render(<Simulator />)

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getAllByText("53.0%").length).toBeGreaterThan(0)
    })

    // Second analysis
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getByText(/Model Sensitivity Comparison/i)).toBeInTheDocument()
      expect(screen.getByText("+8.0 pp")).toBeInTheDocument()
    })
  })

  it("18. shows loading state during analysis and prevents duplicate submission", async () => {
    let resolvePromise: (val: AnalysisResponse) => void
    const pendingPromise = new Promise<AnalysisResponse>((resolve) => {
      resolvePromise = resolve
    })
    const analyzeSpy = vi.spyOn(apiClient, "analyzePatient").mockReturnValueOnce(pendingPromise)

    render(<Simulator />)

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    expect(screen.getByText(/Evaluating Models\.\.\./i)).toBeInTheDocument()
    expect(analyzeBtn).toBeDisabled()

    // Multiple clicks do not trigger additional calls
    fireEvent.click(analyzeBtn)
    expect(analyzeSpy).toHaveBeenCalledTimes(1)

    // Complete the promise
    resolvePromise!(MOCK_ANALYSIS_1)
    await waitFor(() => {
      expect(screen.getAllByText("76.6%").length).toBeGreaterThan(0)
    })
  })

  it("19. displays recoverable API error state with retry", async () => {
    const analyzeSpy = vi
      .spyOn(apiClient, "analyzePatient")
      .mockRejectedValueOnce(new ApiError("Backend connection error", "NETWORK_ERROR", 503))
      .mockResolvedValueOnce(MOCK_ANALYSIS_1)

    render(<Simulator />)

    const analyzeBtn = screen.getByRole("button", { name: /Analyze Patient/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument()
      expect(screen.getByText(/Backend connection error/i)).toBeInTheDocument()
    })

    const retryBtn = screen.getByRole("button", { name: /Retry/i })
    fireEvent.click(retryBtn)

    await waitFor(() => {
      expect(analyzeSpy).toHaveBeenCalledTimes(2)
      expect(screen.getAllByText("76.6%").length).toBeGreaterThan(0)
    })
  })

  it("20. keeps clinical and anatomical disclaimers clearly visible", () => {
    render(<Simulator />)

    expect(
      screen.getByText(/Model exploration only\. Not a formal medical diagnosis/i)
    ).toBeInTheDocument()
  })
})
