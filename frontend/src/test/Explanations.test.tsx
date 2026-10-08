import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { ExplanationPanel } from "@/components/explanations/ExplanationPanel"
import { ShapContributionList } from "@/components/explanations/ShapContributionList"
import type { ExplanationResponse } from "@/types/explanation"
import type { TargetName } from "@/types/prediction"

describe("SHAP Explanation Components", () => {
  const mockExplanation: ExplanationResponse = {
    target: "cath",
    explanation_space: "log-odds (model score)",
    calibration_disclosure:
      "SHAP values explain the underlying predictive model score (log-odds/margin); probability calibration is applied separately to determine the displayed risk probability.",
    base_value: -0.1192,
    features: [
      {
        feature: "Tinversion",
        label: "T-Wave Inversion (ECG)",
        value: 1,
        shap_value: 0.4556,
        direction: "positive",
      },
      {
        feature: "Typical Chest Pain",
        label: "Typical Anginal Chest Pain",
        value: 1,
        shap_value: -0.7724,
        direction: "negative",
      },
    ],
    positive_contributors: [
      {
        feature: "Tinversion",
        label: "T-Wave Inversion (ECG)",
        value: 1,
        shap_value: 0.4556,
        direction: "positive",
      },
    ],
    negative_contributors: [
      {
        feature: "Typical Chest Pain",
        label: "Typical Anginal Chest Pain",
        value: 1,
        shap_value: -0.7724,
        direction: "negative",
      },
    ],
  }

  const mockExplanationsMap: Record<TargetName, ExplanationResponse> = {
    cath: mockExplanation,
    lad: { ...mockExplanation, target: "lad" },
    lcx: { ...mockExplanation, target: "lcx" },
    rca: { ...mockExplanation, target: "rca" },
  }

  it("renders ShapContributionList with proper sign and log-odds score formatting", () => {
    render(
      <ShapContributionList
        title="Top Risk-Elevating Factors"
        subtitle="Variables shifting model score positive"
        items={mockExplanation.positive_contributors}
        type="positive"
      />
    )

    expect(screen.getByText("T-Wave Inversion (ECG)")).toBeInTheDocument()
    expect(screen.getByText("+0.46")).toBeInTheDocument()
    // Explicitly verify we DO NOT display false "+46% risk"
    expect(screen.queryByText("+46% risk")).not.toBeInTheDocument()
  })

  it("renders ExplanationPanel with explicit calibration disclosure and log-odds space badge", () => {
    const handleSelect = vi.fn()
    render(
      <ExplanationPanel
        explanations={mockExplanationsMap}
        selectedTarget="cath"
        onSelectTarget={handleSelect}
      />
    )

    expect(screen.getByText("Why this prediction?")).toBeInTheDocument()
    expect(screen.getByText("SHAP Log-Odds")).toBeInTheDocument()
    expect(
      screen.getByText(/probability calibration is applied separately/)
    ).toBeInTheDocument()
    expect(screen.getByText("log-odds (model score)")).toBeInTheDocument()
  })
})
