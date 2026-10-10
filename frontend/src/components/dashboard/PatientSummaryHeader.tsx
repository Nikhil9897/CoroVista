import React from "react"
import { User, Activity, RefreshCw, Trash2, ShieldCheck } from "lucide-react"
import type { PatientRecord } from "@/types/patient"
import { DEMO_PATIENT_METADATA } from "@/lib/demoPatient"

interface PatientSummaryHeaderProps {
  patient: PatientRecord | null
  isLoading: boolean
  onLoadDemo: () => void
  onClear: () => void
  className?: string
}

export const PatientSummaryHeader: React.FC<PatientSummaryHeaderProps> = ({
  patient,
  isLoading,
  onLoadDemo,
  onClear,
  className = "",
}) => {
  return (
    <div
      className={`glass-panel rounded-2xl p-4 shadow-spatial flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-border/70 select-none ${className}`}
      role="region"
      aria-label="Patient Analysis Status"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border/60 flex items-center justify-center text-primary shrink-0 shadow-xs">
          <User className="w-5 h-5 text-primary" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-foreground tracking-tight">
              {patient ? DEMO_PATIENT_METADATA.label : "No Patient Loaded"}
            </h3>
            {patient && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-amber-400" />
                <span>Synthetic / Benchmark</span>
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            {patient
              ? "All 54 predictive clinical variables evaluated via CoroVista API."
              : "Load benchmark profile to trigger multi-target prediction and SHAP analysis."}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 self-end sm:self-center">
        {patient ? (
          <>
            <button
              onClick={onLoadDemo}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-2 hover:bg-surface-3 text-foreground border border-border/60 transition-all cursor-pointer disabled:opacity-50 shadow-xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-primary ${isLoading ? "animate-spin" : ""}`} />
              <span>Re-analyze</span>
            </button>
            <button
              onClick={onClear}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-2/60 hover:bg-rose-950/30 text-muted-foreground hover:text-rose-300 border border-border/40 transition-all cursor-pointer disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          </>
        ) : (
          <button
            onClick={onLoadDemo}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-spatial-sm cursor-pointer disabled:opacity-50 active:scale-95"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{isLoading ? "Analyzing..." : "Load Demo Patient"}</span>
          </button>
        )}
      </div>
    </div>
  )
}
