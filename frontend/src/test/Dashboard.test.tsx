import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { EmptyState } from "@/components/common/EmptyState"
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner"
import { SystemStatusBadge } from "@/components/common/SystemStatusBadge"
import { ApiError } from "@/api/client"

describe("Dashboard States & Shared Components", () => {
  it("renders EmptyState with load demo CTA button", () => {
    const handleLoad = vi.fn()
    render(<EmptyState onLoadDemo={handleLoad} />)

    expect(screen.getByText("No Patient Analyzed")).toBeInTheDocument()
    const btn = screen.getByRole("button", { name: /Load Demo Patient/i })
    expect(btn).toBeInTheDocument()

    fireEvent.click(btn)
    expect(handleLoad).toHaveBeenCalledTimes(1)
  })

  it("renders LoadingSkeleton with pulse animation and screen-reader status", () => {
    render(<LoadingSkeleton />)
    expect(screen.getByRole("status")).toBeInTheDocument()
    expect(
      screen.getByText(/Computing multi-target predictions and SHAP attributions/i)
    ).toBeInTheDocument()
  })

  it("renders ErrorAlert with user-friendly message and retry callback", () => {
    const handleRetry = vi.fn()
    const error = new ApiError("Validation failed", "INVALID_INPUT", 422)

    render(<ErrorAlert error={error} onRetry={handleRetry} />)

    expect(screen.getByRole("alert")).toBeInTheDocument()
    expect(screen.getByText(/Patient input validation failed/i)).toBeInTheDocument()

    const retryBtn = screen.getByRole("button", { name: /Retry/i })
    fireEvent.click(retryBtn)
    expect(handleRetry).toHaveBeenCalledTimes(1)
  })

  it("renders DisclaimerBanner with mandatory clinical and 3D limitations", () => {
    render(<DisclaimerBanner />)

    expect(
      screen.getByText(/Educational & Decision-Support Prototype Only/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/are not physical 3D lesion coordinates/i)
    ).toBeInTheDocument()
  })

  it("renders SystemStatusBadge for healthy and degraded states", () => {
    const { rerender } = render(
      <SystemStatusBadge
        health={{
          status: "ok",
          service: "corovista-api",
          version: "1.0.0",
          models_loaded: true,
        }}
      />
    )
    expect(screen.getByText(/API Connected • Models Ready/i)).toBeInTheDocument()

    rerender(
      <SystemStatusBadge
        health={{
          status: "degraded",
          service: "corovista-api",
          version: "1.0.0",
          models_loaded: false,
        }}
      />
    )
    expect(screen.getByText(/Models Unavailable/i)).toBeInTheDocument()

    rerender(<SystemStatusBadge health={null} />)
    expect(screen.getByText(/Connecting\.\.\./i)).toBeInTheDocument()
  })
})
