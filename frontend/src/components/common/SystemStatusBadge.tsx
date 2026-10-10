import React from "react"
import type { HealthResponse } from "@/types/patient"

interface SystemStatusBadgeProps {
  health: HealthResponse | null
  className?: string
}

export const SystemStatusBadge: React.FC<SystemStatusBadgeProps> = ({ health, className = "" }) => {
  if (!health) {
    return (
      <div
        className={`inline-flex items-center gap-2 text-xs text-[#7C9692] select-none ${className}`}
        aria-label="Checking system status"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[#7C9692]/50 animate-pulse" />
        <span>Connecting...</span>
      </div>
    )
  }

  const isReady = health.status === "ok" && health.models_loaded

  if (isReady) {
    return (
      <div
        className={`inline-flex items-center gap-2 text-xs text-[#7C9692] select-none ${className}`}
        aria-label="Models ready"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[#34d399]" />
        <span className="text-[#E8F1EE]/90">Models ready</span>
        <span className="sr-only">API Connected • Models Ready</span>
      </div>
    )
  }

  return (
    <div
      className={`inline-flex items-center gap-2 text-xs text-[#7C9692] select-none ${className}`}
      aria-label="Models unavailable"
    >
      <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
      <span className="text-amber-300/90">Models unavailable</span>
    </div>
  )
}
