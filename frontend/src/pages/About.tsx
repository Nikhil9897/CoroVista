import React from "react"
import { Cpu, Activity, AlertTriangle } from "lucide-react"

export const About: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl" role="region" aria-label="About CoroVista">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-foreground">
          About CoroVista
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Multimodal AI Hackathon 2026 &bull; Track A: Cardiovascular Risk Visualization & Prediction
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border border-border/80 bg-card rounded-xl p-4.5 space-y-2">
          <div className="flex items-center gap-2 text-primary font-semibold text-sm">
            <Cpu className="w-4 h-4" />
            <span>Target Machine Learning Models</span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            CoroVista evaluates four independent locked pipelines trained via 25-fold Repeated Stratified CV:
          </p>
          <ul className="text-xs space-y-1 text-muted-foreground/90 font-mono">
            <li>&bull; Cath (Overall CAD): XGBoost + Platt Sigmoid (Cutoff: 0.50)</li>
            <li>&bull; LAD: XGBoost + Platt Sigmoid (Cutoff: 0.50)</li>
            <li>&bull; LCX: XGBoost Uncalibrated (Cutoff: 0.50)</li>
            <li>&bull; RCA: Logistic Regression + Platt Sigmoid (Cutoff: 0.38)</li>
          </ul>
        </div>

        <div className="border border-border/80 bg-card rounded-xl p-4.5 space-y-2">
          <div className="flex items-center gap-2 text-primary font-semibold text-sm">
            <Activity className="w-4 h-4" />
            <span>SHAP Explainability Layer</span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Local feature attributions operate in model score (log-odds / margin) space using Lundberg Tree SHAP for XGBoost and LinearExplainer for Logistic Regression. Downstream probability calibration is strictly decoupled.
          </p>
        </div>
      </div>

      <div className="border border-border/80 bg-card rounded-xl p-5 space-y-3">
        <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
          <AlertTriangle className="w-4 h-4" />
          <span>Clinical & Anatomical Boundary Notice</span>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          CoroVista is an educational and research prototype developed for the Multimodal AI Hackathon 2026. Model outputs indicate statistical probability of obstructive luminal stenosis ($\ge 50\%$) based on the Z-Alizadeh Sani cohort ($N=303$). They do not establish biological causality and are not physical spatial coordinates on coronary anatomy.
        </p>
      </div>
    </div>
  )
}
