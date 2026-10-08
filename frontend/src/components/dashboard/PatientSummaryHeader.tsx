import React from "react"
import { User, Activity, RefreshCw, Trash2 } from "lucide-react"
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
      className={`border border-border/80 bg-card rounded-xl p-4 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${className}`}
      role="region"
      aria-label="Patient Analysis Status"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-secondary border border-border flex items-center justify-center text-muted-foreground">
          <User className="w-5 h-5 text-primary/80" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-foreground">
              {patient ? DEMO_PATIENT_METADATA.label : "No Patient Loaded"}
            </h3>
            {patient && (
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-950/50 text-amber-300 border border-amber-800/60">
                Synthetic / Benchmark
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            {patient
              ? "All 54 predictive clinical variables evaluated via Stage 4 API."
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
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-secondary hover:bg-secondary/80 text-foreground border border-border transition-colors cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
              <span>Re-analyze</span>
            </button>
            <button
              onClick={onClear}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-secondary/50 hover:bg-rose-950/30 text-muted-foreground hover:text-rose-300 border border-border transition-colors cursor-pointer disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          </>
        ) : (
          <button
            onClick={onLoadDemo}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm cursor-pointer disabled:opacity-50"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{isLoading ? "Analyzing..." : "Load Demo Patient"}</span>
          </button>
        )}
      </div>
    </div>
  )
}
