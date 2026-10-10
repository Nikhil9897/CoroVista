import React from "react"
import { ArrowRight, TrendingUp, TrendingDown, Minus, Info } from "lucide-react"
import type { AnalysisResponse } from "@/types/patient"
import type { TargetName } from "@/types/prediction"
import { formatPercent } from "@/lib/utils"

interface ProbabilityComparisonProps {
  previous: AnalysisResponse
  current: AnalysisResponse
  className?: string
}

const TARGETS: Array<{ key: TargetName; label: string; territory: string }> = [
  { key: "cath", label: "Overall CAD (Cath)", territory: "Overall Multivessel Disease" },
  { key: "lad", label: "LAD Stenosis", territory: "Anterior wall, septum & apex" },
  { key: "lcx", label: "LCX Stenosis", territory: "Lateral & posterior LV myocardium" },
  { key: "rca", label: "RCA Stenosis", territory: "Inferior wall, RV & conduction system" },
]

export const ProbabilityComparison: React.FC<ProbabilityComparisonProps> = ({
  previous,
  current,
  className = "",
}) => {
  return (
    <div
      className={`glass-panel rounded-2xl p-5 shadow-spatial border border-border/70 space-y-4 select-none ${className}`}
      role="region"
      aria-label="Before and After Risk Probability Comparison"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/40 pb-3">
        <div>
          <h4 className="text-sm font-semibold text-foreground flex items-center gap-2 tracking-tight">
            <span>Model Sensitivity Comparison</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-primary/15 text-primary border border-primary/30">
              Consecutive Simulation Runs
            </span>
          </h4>
          <p className="text-xs text-muted-foreground mt-0.5">
            Compares model-predicted probabilities between your previous and latest simulation inputs.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {TARGETS.map(({ key, label }) => {
          const prevProb = previous.predictions[key].probability
          const currProb = current.predictions[key].probability
          const delta = (currProb - prevProb) * 100
          const deltaAbs = Math.abs(delta)
          const isIncrease = delta > 0.05
          const isDecrease = delta < -0.05
          const isNeutral = !isIncrease && !isDecrease

          return (
            <div
              key={key}
              className="p-3.5 rounded-xl bg-surface-2/70 border border-border/60 flex flex-col justify-between space-y-2.5 shadow-xs"
            >
              <div>
                <span className="text-xs font-semibold text-foreground block truncate tracking-tight">
                  {label}
                </span>
                <span className="text-[10px] text-muted-foreground block font-mono">
                  θ = {previous.predictions[key].threshold.toFixed(2)}
                </span>
              </div>

              {/* Trajectory: Previous -> Current */}
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-muted-foreground" title="Previous evaluation">
                  {formatPercent(prevProb)}
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-muted-foreground/60 shrink-0 mx-1" />
                <span className="text-foreground font-bold" title="Current evaluation">
                  {formatPercent(currProb)}
                </span>
              </div>

              {/* Delta Badge */}
              <div className="pt-2 border-t border-border/40 flex items-center justify-between">
                <span className="text-[10px] text-muted-foreground">Delta:</span>
                <span
                  className={`inline-flex items-center gap-1 text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md ${
                    isIncrease
                      ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                      : isDecrease
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-surface-3 text-muted-foreground border border-border/50"
                  }`}
                >
                  {isIncrease && <TrendingUp className="w-3 h-3" />}
                  {isDecrease && <TrendingDown className="w-3 h-3" />}
                  {isNeutral && <Minus className="w-3 h-3" />}
                  <span>
                    {isIncrease ? "+" : isDecrease ? "-" : ""}
                    {deltaAbs.toFixed(1)} pp
                  </span>
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Strict Clinical Non-Causality Caveat */}
      <div
        className="flex items-start gap-2 text-[11px] text-muted-foreground bg-surface-2/60 border border-border/50 p-2.5 rounded-xl leading-relaxed"
        role="note"
      >
        <Info className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
        <p>
          <strong className="text-foreground/90 font-medium">Non-Causal Note:</strong> The comparison above reflects mathematical differences across two discrete model evaluations with different input vectors. It does not demonstrate biological causality, therapeutic response, or clinical prognosis.
        </p>
      </div>
    </div>
  )
}
