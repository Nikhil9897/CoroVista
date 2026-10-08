import React from "react"
import { AlertTriangle, Info } from "lucide-react"

interface DisclaimerBannerProps {
  compact?: boolean
  className?: string
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({ compact = false, className = "" }) => {
  if (compact) {
    return (
      <div
        className={`flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground bg-muted/40 border border-border/50 rounded-md ${className}`}
        role="note"
        aria-label="Clinical Decision Support Notice"
      >
        <Info className="w-3.5 h-3.5 text-primary shrink-0" />
        <span>
          <strong className="text-foreground/90 font-medium">Research Prototype:</strong> Predictions represent model risk estimations and do not replace clinical judgment or angiography.
        </span>
      </div>
    )
  }

  return (
    <div
      className={`border border-border/80 bg-card/60 backdrop-blur-sm rounded-lg p-3.5 text-xs text-muted-foreground shadow-sm ${className}`}
      role="region"
      aria-label="Regulatory and Clinical Disclaimer"
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="leading-relaxed">
            <strong className="text-foreground/90 font-semibold">Educational & Decision-Support Prototype Only:</strong> Model predictions are not a formal clinical diagnosis and do not replace professional medical judgment, invasive coronary catheterization, or diagnostic imaging.
          </p>
          <p className="leading-relaxed text-muted-foreground/90">
            <strong className="text-foreground/80 font-medium">Anatomical Note:</strong> Predicted vessel probabilities represent statistical stenosis risk ($\ge 50\%$ narrowing) and are not physical 3D lesion coordinates.
          </p>
        </div>
      </div>
    </div>
  )
}
