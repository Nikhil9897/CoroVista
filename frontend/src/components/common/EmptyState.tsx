import React from "react"
import { Activity, Play } from "lucide-react"

interface EmptyStateProps {
  onLoadDemo: () => void
  isLoading?: boolean
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onLoadDemo, isLoading = false }) => {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[460px] p-8 sm:p-12 border border-border/70 rounded-2xl glass-panel shadow-spatial text-center select-none"
      role="region"
      aria-label="No patient analyzed"
    >
      <div className="w-16 h-16 rounded-2xl bg-surface-2 border border-border/70 flex items-center justify-center mb-5 text-muted-foreground shadow-spatial-sm">
        <Activity className="w-8 h-8 text-primary" />
      </div>

      <h3 className="text-xl font-bold tracking-tight text-foreground mb-1.5">No Patient Analyzed</h3>
      <p className="text-xs sm:text-sm text-muted-foreground max-w-md mb-6 leading-relaxed">
        Load a synthetic demo profile or enter patient parameters to compute overall CAD risk, vessel-specific stenosis probabilities, and SHAP feature attributions.
      </p>

      <div className="flex flex-col sm:flex-row items-center gap-3">
        <button
          onClick={onLoadDemo}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-spatial-sm disabled:opacity-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40 active:scale-95"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{isLoading ? "Analyzing Patient..." : "Load Demo Patient (Synthetic)"}</span>
        </button>
      </div>

      <span className="mt-5 text-[11px] font-mono text-muted-foreground/60">
        Demo data conforms to the Z-Alizadeh Sani benchmark schema ($N=54$ features).
      </span>
    </div>
  )
}
