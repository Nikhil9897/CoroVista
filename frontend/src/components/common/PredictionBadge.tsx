import React from "react"
import { AlertCircle, CheckCircle2 } from "lucide-react"

interface PredictionBadgeProps {
  prediction: string
  className?: string
  size?: "sm" | "md" | "lg"
}

export const PredictionBadge: React.FC<PredictionBadgeProps> = ({
  prediction,
  className = "",
  size = "md",
}) => {
  const isPositive = prediction.toLowerCase() === "cad" || prediction.toLowerCase() === "stenotic"

  const sizeStyles = {
    sm: "px-2 py-0.5 text-xs gap-1",
    md: "px-2.5 py-1 text-xs gap-1.5",
    lg: "px-3.5 py-1.5 text-sm font-semibold gap-2",
  }[size]

  if (isPositive) {
    return (
      <span
        className={`inline-flex items-center rounded-md font-medium bg-rose-950/40 text-rose-300 border border-rose-800/60 shadow-sm ${sizeStyles} ${className}`}
        role="status"
        aria-label={`Prediction: ${prediction}`}
      >
        <AlertCircle className={size === "lg" ? "w-4 h-4" : "w-3.5 h-3.5"} />
        <span>{prediction}</span>
      </span>
    )
  }

  return (
    <span
      className={`inline-flex items-center rounded-md font-medium bg-emerald-950/40 text-emerald-300 border border-emerald-800/60 shadow-sm ${sizeStyles} ${className}`}
      role="status"
      aria-label={`Prediction: ${prediction}`}
    >
      <CheckCircle2 className={size === "lg" ? "w-4 h-4" : "w-3.5 h-3.5"} />
      <span>{prediction}</span>
    </span>
  )
}
