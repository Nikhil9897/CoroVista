import React from "react"
import { AlertCircle, Clock, RefreshCw, Sparkles } from "lucide-react"
import type { ApiError } from "@/api/client"

interface SimulatorStatusProps {
  isLoading: boolean
  isStale: boolean
  error: ApiError | null
  onRetry?: () => void
}

export const SimulatorStatus: React.FC<SimulatorStatusProps> = ({
  isLoading,
  isStale,
  error,
  onRetry,
}) => {
  if (error) {
    return (
      <div
        className="p-3.5 rounded-xl border border-destructive/40 bg-destructive/10 text-destructive flex items-center justify-between gap-3 shadow-sm animate-in fade-in-50"
        role="alert"
      >
        <div className="flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <div className="text-xs">
            <strong className="font-semibold">Analysis Failed:</strong> {error.message}
            {error.code && <span className="font-mono ml-1.5 opacity-80">({error.code})</span>}
          </div>
        </div>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-destructive/20 hover:bg-destructive/30 text-destructive-foreground transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        )}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div
        className="p-3 rounded-xl border border-primary/30 bg-primary/5 text-primary flex items-center gap-2.5 shadow-sm text-xs animate-pulse"
        role="status"
      >
        <Sparkles className="w-4 h-4 shrink-0 animate-spin" />
        <span>Evaluating multi-target machine learning models and SHAP feature attributions...</span>
      </div>
    )
  }

  if (isStale) {
    return (
      <div
        className="p-2.5 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center gap-2 text-xs"
        role="note"
      >
        <Clock className="w-3.5 h-3.5 shrink-0" />
        <span>
          <strong>Showing previous successful analysis:</strong> Input parameters have been modified. Click &ldquo;Analyze Patient&rdquo; to re-evaluate.
        </span>
      </div>
    )
  }

  return null
}
