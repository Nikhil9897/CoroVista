import React from "react"
import { CheckCircle2, AlertCircle, XCircle } from "lucide-react"
import type { HealthResponse } from "@/types/patient"

interface SystemStatusBadgeProps {
  health: HealthResponse | null
  className?: string
}

export const SystemStatusBadge: React.FC<SystemStatusBadgeProps> = ({ health, className = "" }) => {
  if (!health) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-surface-2 text-muted-foreground border border-border/60 ${className}`}
        aria-label="Checking system status"
      >
        <span className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-pulse" />
        <span>Connecting...</span>
      </div>
    )
  }

  if (health.status === "ok" && health.models_loaded) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-xs ${className}`}
        aria-label="API Connected and Models Ready"
      >
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        <span>API Connected &bull; Models Ready</span>
      </div>
    )
  }

  if (health.status === "degraded" || !health.models_loaded) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-amber-500/15 text-amber-400 border border-amber-500/30 ${className}`}
        aria-label="API Connected but Models Unavailable"
      >
        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
        <span>Models Unavailable</span>
      </div>
    )
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30 ${className}`}
      aria-label="Backend Unavailable"
    >
      <XCircle className="w-3.5 h-3.5 text-rose-400" />
      <span>Backend Unavailable</span>
    </div>
  )
}
