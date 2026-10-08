import React from "react"
import { AlertCircle, RotateCcw } from "lucide-react"
import { ApiError } from "@/api/client"

interface ErrorAlertProps {
  error: ApiError | null
  onRetry?: () => void
  className?: string
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry, className = "" }) => {
  if (!error) return null

  let userFriendlyMessage = error.message

  if (error.code === "NETWORK_ERROR") {
    userFriendlyMessage = "Unable to connect to the CoroVista API service. Please verify that the FastAPI backend is running on http://localhost:8000."
  } else if (error.status === 422) {
    userFriendlyMessage = "Patient input validation failed. Please review the provided clinical variables."
  } else if (error.status === 503) {
    userFriendlyMessage = "The machine learning model artifacts are currently unavailable on the server."
  }

  return (
    <div
      className={`border border-rose-800/60 bg-rose-950/30 rounded-xl p-4 text-rose-200 shadow-sm ${className}`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-sm font-semibold text-rose-100">Analysis Error ({error.code})</h4>
            <p className="text-xs text-rose-300/90 leading-relaxed">{userFriendlyMessage}</p>
          </div>
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-rose-900/60 hover:bg-rose-900 text-rose-200 border border-rose-700/60 transition-colors shrink-0 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        )}
      </div>
    </div>
  )
}
