import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { App } from "@/App"

// Mock apiClient to prevent real network calls during route testing
vi.mock("@/api/client", () => ({
  apiClient: {
    getHealth: vi.fn().mockResolvedValue({
      status: "ok",
      service: "corovista-api",
      version: "1.0.0",
      models_loaded: true,
    }),
    getModels: vi.fn().mockResolvedValue({ models: [] }),
    analyzePatient: vi.fn().mockResolvedValue({
      predictions: {
        cath: { probability: 0.76, prediction: "CAD", threshold: 0.5 },
        lad: { probability: 0.53, prediction: "Stenotic", threshold: 0.5 },
        lcx: { probability: 0.13, prediction: "Normal", threshold: 0.5 },
        rca: { probability: 0.40, prediction: "Stenotic", threshold: 0.38 },
      },
      explanations: {
        cath: {
          target: "cath",
          explanation_space: "log-odds (model score)",
          calibration_disclosure: "calibration note",
          base_value: -0.1,
          features: [],
          positive_contributors: [],
          negative_contributors: [],
        },
        lad: {
          target: "lad",
          explanation_space: "log-odds (model score)",
          calibration_disclosure: "calibration note",
          base_value: -0.1,
          features: [],
          positive_contributors: [],
          negative_contributors: [],
        },
        lcx: {
          target: "lcx",
          explanation_space: "log-odds (model score)",
          calibration_disclosure: "calibration note",
          base_value: -0.1,
          features: [],
          positive_contributors: [],
          negative_contributors: [],
        },
        rca: {
          target: "rca",
          explanation_space: "log-odds (model score)",
          calibration_disclosure: "calibration note",
          base_value: -0.1,
          features: [],
          positive_contributors: [],
          negative_contributors: [],
        },
      },
      clinical_disclaimer: "test disclaimer",
      visualization_note: "test note",
    }),
  },
  ApiError: class ApiError extends Error {
    constructor(msg: string) {
      super(msg)
    }
  },
}))

describe("Application Shell & Navigation", () => {
  it("renders CoroVista application brand and sidebar navigation", async () => {
    render(<App />)

    expect(screen.getAllByText("CoroVista")[0]).toBeInTheDocument()
    expect(screen.getByText("Clinical Dashboard")).toBeInTheDocument()
    expect(screen.getByText("Patient Simulator")).toBeInTheDocument()
    expect(screen.getByText("About & Methodology")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText(/API Connected • Models Ready/i)).toBeInTheDocument()
    })
  })

  it("navigates to Patient Simulator placeholder route", async () => {
    render(<App />)

    const simLink = screen.getByText("Patient Simulator")
    fireEvent.click(simLink)

    expect(
      screen.getByText(/Modify clinical parameters and observe how model predictions change/i)
    ).toBeInTheDocument()
    expect(screen.getByText("Stage 5C Feature Roadmap")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText(/API Connected • Models Ready/i)).toBeInTheDocument()
    })
  })

  it("navigates to About & Methodology page", async () => {
    render(<App />)

    const aboutLink = screen.getByText("About & Methodology")
    fireEvent.click(aboutLink)

    expect(
      screen.getByText(/Multimodal AI Hackathon 2026 • Track A/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Cath \(Overall CAD\): XGBoost \+ Platt Sigmoid/i)
    ).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText(/API Connected • Models Ready/i)).toBeInTheDocument()
    })
  })
})
