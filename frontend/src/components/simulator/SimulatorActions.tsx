import React from "react"
import { Play, RotateCcw, Trash2, Loader2, Sparkles, AlertCircle } from "lucide-react"

interface SimulatorActionsProps {
  onAnalyze: () => void
  onLoadDemo: () => void
  onResetDemo: () => void
  onClearForm?: () => void
  isLoading: boolean
  isDirty?: boolean
  hasResults?: boolean
  hasErrors?: boolean
}

export const SimulatorActions: React.FC<SimulatorActionsProps> = ({
  onAnalyze,
  onLoadDemo,
  onResetDemo,
  onClearForm,
  isLoading,
  isDirty = false,
  hasResults = false,
  hasErrors = false,
}) => {
  return (
    <div
      className="p-4 rounded-2xl glass-panel shadow-spatial border border-border/70 space-y-3 select-none"
      role="region"
      aria-label="Simulator Action Toolbar"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Primary Analyze Button */}
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isLoading}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-spatial-sm cursor-pointer ${
              isLoading
                ? "bg-primary/70 text-primary-foreground cursor-not-allowed"
                : "bg-primary hover:bg-primary/90 text-primary-foreground hover:shadow-primary/25 hover:shadow-lg active:scale-[0.98]"
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Evaluating Models...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Patient</span>
              </>
            )}
          </button>

          {isDirty && hasResults && !isLoading && (
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-400 bg-amber-500/15 px-2.5 py-1 rounded-md border border-amber-500/30">
              <Sparkles className="w-3 h-3" />
              <span>Unsent changes in form</span>
            </span>
          )}

          {hasErrors && (
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-400 bg-rose-500/15 px-2 py-1 rounded-md border border-rose-500/30">
              <AlertCircle className="w-3 h-3" />
              <span>Resolve validation errors before submitting</span>
            </span>
          )}
        </div>

        {/* Right: Demo / Reset Controls */}
        <div className="flex items-center gap-2">
          {!hasResults && (
            <button
              type="button"
              onClick={onLoadDemo}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-2 hover:bg-surface-3 text-foreground border border-border/60 transition-colors cursor-pointer"
              title="Load standard synthetic demo patient"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Load Demo Patient</span>
            </button>
          )}

          <button
            type="button"
            onClick={onResetDemo}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-2 hover:bg-surface-3 text-foreground border border-border/60 transition-colors cursor-pointer"
            title="Restore standard 62yo male synthetic demo profile"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to Demo Values</span>
          </button>

          {onClearForm && (
            <button
              type="button"
              onClick={onClearForm}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/30 transition-colors cursor-pointer"
              title="Clear all form fields"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear Form</span>
            </button>
          )}
        </div>
      </div>

      {/* Synthetic Disclaimer Tag */}
      <div className="pt-2 border-t border-border/40 flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted-foreground">
        <span className="font-medium text-foreground/85">
          Demo / synthetic patient — not a real patient record.
        </span>
        <span className="bg-surface-2 px-2 py-0.5 rounded-md text-[10px] font-mono border border-border/50">
          Source: Z-Alizadeh Sani Feature Specification
        </span>
      </div>
    </div>
  )
}
