import React from "react"
import { Activity, Play } from "lucide-react"

interface EmptyStateProps {
  onLoadDemo: () => void
  isLoading?: boolean
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onLoadDemo, isLoading = false }) => {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[460px] p-8 border border-dashed border-border/80 rounded-xl bg-card/30 text-center"
      role="region"
      aria-label="No patient analyzed"
    >
      <div className="w-14 h-14 rounded-2xl bg-secondary/80 border border-border flex items-center justify-center mb-4 text-muted-foreground shadow-sm">
        <Activity className="w-7 h-7 text-primary/80" />
      </div>

      <h3 className="text-lg font-semibold text-foreground mb-1">No Patient Analyzed</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-6 leading-relaxed">
        Load a synthetic demo profile or enter patient parameters to compute overall CAD risk, vessel-specific stenosis probabilities, and SHAP feature attributions.
      </p>

      <div className="flex flex-col sm:flex-row items-center gap-3">
        <button
          onClick={onLoadDemo}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{isLoading ? "Analyzing Patient..." : "Load Demo Patient (Synthetic)"}</span>
        </button>
      </div>

      <span className="mt-4 text-[11px] text-muted-foreground/70">
        Demo data conforms to the Z-Alizadeh Sani benchmark schema ($N=54$ features).
      </span>
    </div>
  )
}
