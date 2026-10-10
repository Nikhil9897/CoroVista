import React from "react"
import { Info } from "lucide-react"
import type { ExplanationResponse } from "@/types/explanation"
import type { TargetName } from "@/types/prediction"
import { ShapContributionList } from "./ShapContributionList"

interface ExplanationPanelProps {
  explanations: Record<TargetName, ExplanationResponse>
  selectedTarget: TargetName
  onSelectTarget: (target: TargetName) => void
  className?: string
}

const TARGET_DISPLAY_NAMES: Record<TargetName, string> = {
  cath: "Overall CAD (Cath)",
  lad: "LAD Stenosis",
  lcx: "LCX Stenosis",
  rca: "RCA Stenosis",
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  explanations,
  selectedTarget,
  onSelectTarget,
  className = "",
}) => {
  const currentExp = explanations[selectedTarget]
  const targets: TargetName[] = ["cath", "lad", "lcx", "rca"]

  return (
    <div
      className={`glass-panel rounded-2xl p-5 sm:p-6 shadow-spatial border border-border/70 space-y-5 select-none ${className}`}
      role="region"
      aria-label="SHAP Explainability Section"
    >
      {/* Header and target selector tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/40 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-foreground tracking-tight">
              Why this prediction?
            </h3>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-medium bg-primary/15 text-primary border border-primary/30">
              SHAP Log-Odds
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Model contribution in log-odds margin space. Ranked by absolute impact.
          </p>
        </div>

        {/* Target Tabs */}
        <div className="flex items-center gap-1 p-1 bg-surface-2 rounded-xl border border-border/60 self-start sm:self-auto">
          {targets.map((t) => (
            <button
              key={t}
              onClick={() => onSelectTarget(t)}
              className={`px-3 py-1 text-xs font-mono font-medium rounded-lg transition-all cursor-pointer ${
                selectedTarget === t
                  ? "bg-surface-3 text-foreground shadow-xs border border-border/80 font-semibold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Calibration Disclosure Notice */}
      <div className="flex items-start gap-2.5 p-3 rounded-xl bg-surface-2/60 border border-border/50 text-xs text-muted-foreground">
        <Info className="w-4 h-4 text-primary shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-foreground/90 font-medium">Model Attribution Boundary:</strong>{" "}
          {currentExp?.calibration_disclosure ||
            "SHAP values explain the underlying predictive model score (log-odds/margin); probability calibration is applied separately to determine the displayed risk probability."}
        </p>
      </div>

      {/* Target Metadata Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground px-1">
        <span>Target: <strong className="text-foreground font-medium">{TARGET_DISPLAY_NAMES[selectedTarget]}</strong></span>
        <span>Base Score ($\phi_0$): <strong className="font-mono text-foreground">{currentExp?.base_value?.toFixed(3)}</strong></span>
        <span>Explanation Space: <strong className="font-mono text-foreground">{currentExp?.explanation_space}</strong></span>
      </div>

      {/* Grid of Positive & Negative Contributors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-1">
        <ShapContributionList
          title="Top Risk-Elevating Factors"
          subtitle="Variables shifting model score positive (+) towards stenosis"
          items={currentExp?.positive_contributors || []}
          type="positive"
        />

        <ShapContributionList
          title="Top Protective / Lowering Factors"
          subtitle="Variables shifting model score negative (-) towards normal"
          items={currentExp?.negative_contributors || []}
          type="negative"
        />
      </div>
    </div>
  )
}
