import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { CoronaryViewer } from "@/components/viewer/CoronaryViewer"
import { ViewerLegend } from "@/components/viewer/ViewerLegend"
import { ViewerControls } from "@/components/viewer/ViewerControls"
import { ViewerHoverTooltip } from "@/components/viewer/ViewerHoverTooltip"
import { ViewerLoadingFallback } from "@/components/viewer/ViewerLoadingFallback"
import { ViewerErrorBoundary } from "@/components/viewer/ViewerErrorBoundary"
import type { PredictionResponse } from "@/types/prediction"

// Mock R3F and drei for JSDOM
vi.mock("@react-three/fiber", () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="mock-canvas">{children}</div>
  ),
  useThree: () => ({ camera: { position: { set: vi.fn() } } }),
}))

vi.mock("@react-three/drei", () => ({
  OrbitControls: () => <div data-testid="mock-orbit-controls" />,
  useGLTF: {
    preload: vi.fn(),
  },
}))

// Mock CoronaryScene within CoronaryViewer
vi.mock("@/components/viewer/CoronaryScene", () => ({
  CoronaryScene: ({
    onSelectVessel,
    onHoverVessel,
  }: {
    onSelectVessel: (id: string) => void
    onHoverVessel: (info: any) => void
  }) => (
    <div data-testid="mock-coronary-scene">
      <button
        data-testid="select-lad-btn"
        onClick={() => onSelectVessel("lad")}
      >
        Select LAD
      </button>
      <button
        data-testid="select-rca-btn"
        onClick={() => onSelectVessel("rca")}
      >
        Select RCA
      </button>
      <button
        data-testid="hover-lad-btn"
        onMouseEnter={() =>
          onHoverVessel({
            id: "lad",
            short: "LAD",
            full: "Left Anterior Descending",
            probability: 0.724,
            threshold: 0.46,
            isStenotic: true,
            territory: "Anterior wall, septum & apex",
          })
        }
        onMouseLeave={() => onHoverVessel(null)}
      >
        Hover LAD
      </button>
    </div>
  ),
}))

const mockPredictions: PredictionResponse["predictions"] = {
  cath: {
    probability: 0.812,
    prediction: "CAD Present",
    threshold: 0.5,
  },
  lad: {
    probability: 0.724,
    prediction: "Stenotic",
    threshold: 0.46,
  },
  lcx: {
    probability: 0.412,
    prediction: "Non-Stenotic",
    threshold: 0.5,
  },
  rca: {
    probability: 0.4005,
    prediction: "Stenotic",
    threshold: 0.38,
  },
}

describe("CoronaryViewer Component", () => {
  it("renders the mandatory clinical disclaimer note", () => {
    render(<CoronaryViewer predictions={mockPredictions} />)

    const disclaimer = screen.getByRole("note")
    expect(disclaimer).toBeInTheDocument()
    expect(disclaimer).toHaveTextContent(
      "Vessel colors represent model-predicted stenosis probability, not physical lesion location"
    )
  })

  it("renders the continuous probability legend with explicit label", () => {
    render(<ViewerLegend predictions={mockPredictions} selectedTarget="rca" />)

    expect(screen.getByText("Model-predicted stenosis probability")).toBeInTheDocument()
    expect(screen.getByText("0%")).toBeInTheDocument()
    expect(screen.getByText("50%")).toBeInTheDocument()
    expect(screen.getByText("100%")).toBeInTheDocument()
  })

  it("accurately preserves the RCA example at probability 0.4005 and threshold 0.38", () => {
    render(<ViewerLegend predictions={mockPredictions} selectedTarget="rca" />)

    // Check that RCA is shown with 40.1% and threshold 0.38
    expect(screen.getByText("RCA Threshold:")).toBeInTheDocument()
    expect(screen.getByText("38.0%")).toBeInTheDocument()
    expect(screen.getByText("40.1%")).toBeInTheDocument()
    expect(screen.getByText("(θ=0.38)")).toBeInTheDocument()
  })

  it("synchronizes vessel selection callbacks when clicking in the 3D scene", () => {
    const handleSelect = vi.fn()
    render(
      <CoronaryViewer
        predictions={mockPredictions}
        selectedTarget="cath"
        onSelectTarget={handleSelect}
      />
    )

    fireEvent.click(screen.getByTestId("select-lad-btn"))
    expect(handleSelect).toHaveBeenCalledWith("lad")

    fireEvent.click(screen.getByTestId("select-rca-btn"))
    expect(handleSelect).toHaveBeenCalledWith("rca")
  })

  it("handles visibility toggles for vessels and context", () => {
    const toggleMock = vi.fn()
    const visibility = { lad: true, lcx: true, rca: true, context: true }

    render(
      <ViewerControls
        visibility={visibility}
        onToggleVisibility={toggleMock}
        onSelectPreset={vi.fn()}
      />
    )

    const ladToggle = screen.getByRole("button", { name: /lad/i })
    fireEvent.click(ladToggle)
    expect(toggleMock).toHaveBeenCalledWith("lad")

    const contextToggle = screen.getByRole("button", { name: /context/i })
    fireEvent.click(contextToggle)
    expect(toggleMock).toHaveBeenCalledWith("context")
  })

  it("triggers camera view presets (AP, RAO, LAO, Posterior, Reset)", () => {
    const presetMock = vi.fn()
    const visibility = { lad: true, lcx: true, rca: true, context: true }

    render(
      <ViewerControls
        visibility={visibility}
        onToggleVisibility={vi.fn()}
        onSelectPreset={presetMock}
      />
    )

    fireEvent.click(screen.getByTitle(/anterior-posterior/i))
    expect(presetMock).toHaveBeenCalledWith("ap")

    fireEvent.click(screen.getByTitle(/right anterior oblique/i))
    expect(presetMock).toHaveBeenCalledWith("rao")

    fireEvent.click(screen.getByTitle(/left anterior oblique/i))
    expect(presetMock).toHaveBeenCalledWith("lao")

    fireEvent.click(screen.getByTitle(/posterior view/i))
    expect(presetMock).toHaveBeenCalledWith("posterior")

    fireEvent.click(screen.getByTitle(/reset camera/i))
    expect(presetMock).toHaveBeenCalledWith("reset")
  })

  it("renders hover tooltip with predicted probability and clinical territory", () => {
    const { rerender } = render(<ViewerHoverTooltip info={null} />)
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument()

    rerender(
      <ViewerHoverTooltip
        info={{
          id: "lad",
          short: "LAD",
          full: "Left Anterior Descending",
          probability: 0.724,
          threshold: 0.46,
          isStenotic: true,
          territory: "Anterior wall, septum & apex",
        }}
      />
    )

    const tooltip = screen.getByRole("tooltip")
    expect(tooltip).toBeInTheDocument()
    expect(tooltip).toHaveTextContent("LAD")
    expect(tooltip).toHaveTextContent("72.4%")
    expect(tooltip).toHaveTextContent("46.0%")
    expect(tooltip).toHaveTextContent("Stenotic")
    expect(tooltip).toHaveTextContent("Anterior wall, septum & apex")
  })

  it("renders loading fallback with spinner and description", () => {
    render(<ViewerLoadingFallback />)
    expect(screen.getByRole("status")).toBeInTheDocument()
    expect(screen.getByText("Loading 3D Coronary Anatomy Model...")).toBeInTheDocument()
  })

  it("catches WebGL errors in error boundary without breaking the UI", () => {
    const ProblemChild = () => {
      throw new Error("WebGL context lost test")
    }

    render(
      <ViewerErrorBoundary>
        <ProblemChild />
      </ViewerErrorBoundary>
    )

    expect(screen.getByRole("alert")).toBeInTheDocument()
    expect(screen.getByText("3D Graphics Rendering Issue")).toBeInTheDocument()
    expect(screen.getByText(/WebGL context lost test/i)).toBeInTheDocument()
  })
})
