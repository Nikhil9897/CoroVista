import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { CadRiskCard } from "@/components/predictions/CadRiskCard"
import { VesselRiskCard } from "@/components/predictions/VesselRiskCard"
import { RiskBar } from "@/components/common/RiskBar"
import { PredictionBadge } from "@/components/common/PredictionBadge"

describe("Risk & Prediction Components", () => {
  it("renders CAD risk card with continuous probability and threshold", () => {
    const mockPred = {
      probability: 0.7657,
      prediction: "CAD",
      threshold: 0.50,
      model_family: "XGBoost",
      calibration: "Platt/Sigmoid",
    }

    render(<CadRiskCard prediction={mockPred} />)

    expect(screen.getByText("Overall CAD Risk")).toBeInTheDocument()
    expect(screen.getAllByText("76.6%")[0]).toBeInTheDocument()
    expect(screen.getByText("CAD")).toBeInTheDocument()
    expect(screen.getByText("Decision Threshold: 50.0%")).toBeInTheDocument()
    expect(screen.getByText("Model: XGBoost")).toBeInTheDocument()
  })

  it("correctly handles RCA threshold 0.38 where 40.1% is Stenotic", () => {
    const mockRcaPred = {
      probability: 0.4005,
      prediction: "Stenotic",
      threshold: 0.38,
      model_family: "LogisticRegression",
      calibration: "Platt/Sigmoid",
    }

    render(<VesselRiskCard target="rca" prediction={mockRcaPred} />)

    expect(screen.getAllByText("RCA")[0]).toBeInTheDocument()
    expect(screen.getByText("Right Coronary Artery")).toBeInTheDocument()
    expect(screen.getAllByText("40.1%")[0]).toBeInTheDocument()
    expect(screen.getByText("Stenotic")).toBeInTheDocument()
    expect(screen.getByText(/Cutoff: 38.0%/)).toBeInTheDocument()
  })

  it("correctly handles LAD threshold 0.50 where 40.1% is Normal", () => {
    const mockLadPred = {
      probability: 0.4005,
      prediction: "Normal",
      threshold: 0.50,
      model_family: "XGBoost",
      calibration: "Platt/Sigmoid",
    }

    render(<VesselRiskCard target="lad" prediction={mockLadPred} />)

    expect(screen.getAllByText("LAD")[0]).toBeInTheDocument()
    expect(screen.getByText("Normal")).toBeInTheDocument()
    expect(screen.getByText(/Cutoff: 50.0%/)).toBeInTheDocument()
  })

  it("renders PredictionBadge correctly for positive and negative classes", () => {
    const { rerender } = render(<PredictionBadge prediction="CAD" />)
    expect(screen.getByText("CAD")).toBeInTheDocument()

    rerender(<PredictionBadge prediction="Normal" />)
    expect(screen.getByText("Normal")).toBeInTheDocument()
  })

  it("renders RiskBar with continuous probability and threshold notch", () => {
    render(<RiskBar probability={0.62} threshold={0.50} />)
    expect(screen.getByText("62.0%")).toBeInTheDocument()
    expect(screen.getByText(/Threshold: 50.0% \(Exceeded\)/)).toBeInTheDocument()
  })
})
