import React from "react"
import { Cpu, Activity, AlertTriangle, Layers, CheckCircle } from "lucide-react"

export const About: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-10" role="region" aria-label="About CoroVista">
      {/* Editorial Header */}
      <div className="border-b border-border/40 pb-6 space-y-2">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-wider bg-primary/15 text-primary border border-primary/30">
          <span>System Architecture & Scientific Methodology</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          About CoroVista
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed max-w-3xl">
          Cardiovascular Risk Visualization & Multi-Target Stenosis Prediction System
        </p>
      </div>

      {/* Primary Model Architecture Section */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-foreground font-semibold text-base">
          <Cpu className="w-5 h-5 text-primary" />
          <h2>Multi-Target Machine Learning Architecture</h2>
        </div>
        <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
          CoroVista evaluates four independent locked pipelines trained via 25-fold Repeated Stratified Cross-Validation on the authoritative Z-Alizadeh Sani clinical cohort ($N=303$ patients, 54 features):
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          <div className="glass-panel rounded-2xl p-5 border border-border/70 shadow-spatial-sm space-y-3">
            <div className="flex items-center justify-between border-b border-border/40 pb-2">
              <span className="font-semibold text-sm text-foreground">Target Pipelines</span>
              <span className="text-[10px] font-mono text-muted-foreground">Locked Artifacts</span>
            </div>
            <ul className="text-xs space-y-2.5 text-muted-foreground font-mono">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Cath (Overall CAD): XGBoost + Platt Sigmoid (Cutoff: 0.50)</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>LAD: XGBoost + Platt Sigmoid (Cutoff: 0.50)</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>LCX: XGBoost Uncalibrated (Cutoff: 0.50)</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>RCA: Logistic Regression + Platt Sigmoid (Cutoff: 0.38)</span>
              </li>
            </ul>
          </div>

          <div className="glass-panel rounded-2xl p-5 border border-border/70 shadow-spatial-sm space-y-3">
            <div className="flex items-center justify-between border-b border-border/40 pb-2">
              <span className="font-semibold text-sm text-foreground">Decision Threshold Strategy</span>
              <span className="text-[10px] font-mono text-muted-foreground">ROC / F1 Optimization</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              While Cath, LAD, and LCX utilize a standard decision boundary (&theta; = 0.50), the Right Coronary Artery model utilizes an empirical threshold of <strong>&theta; = 0.38</strong> derived from validation ROC curves to maximize clinical sensitivity against subtle inferior-wall ischemic patterns.
            </p>
          </div>
        </div>
      </section>

      {/* SHAP Explainability & Calibration Section */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-foreground font-semibold text-base">
          <Activity className="w-5 h-5 text-primary" />
          <h2>Explainability Layer & Decoupled Calibration</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="glass-panel rounded-2xl p-5 border border-border/70 shadow-spatial-sm space-y-2.5">
            <span className="font-semibold text-sm text-foreground block">SHAP Explainability Layer</span>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Local feature attributions operate in model score (log-odds / margin) space using Lundberg Tree SHAP for XGBoost and LinearExplainer for Logistic Regression. Downstream probability calibration is strictly decoupled.
            </p>
          </div>

          <div className="glass-panel rounded-2xl p-5 border border-border/70 shadow-spatial-sm space-y-2.5">
            <span className="font-semibold text-sm text-foreground block">Mathematical Additivity</span>
            <p className="text-xs text-muted-foreground leading-relaxed">
              In margin space, local attributions satisfy exact efficiency: the sum of base value and all individual feature SHAP contributions equals the raw uncalibrated model margin score $f(x) = \phi_0 + \sum \phi_i$.
            </p>
          </div>
        </div>
      </section>

      {/* Anatomical 3D Coordinate Mapping Section */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-foreground font-semibold text-base">
          <Layers className="w-5 h-5 text-primary" />
          <h2>Anatomical 3D Mesh Registration</h2>
        </div>

        <div className="glass-panel rounded-2xl p-5 border border-border/70 shadow-spatial-sm space-y-3">
          <p className="text-xs text-muted-foreground leading-relaxed">
            Coronary arterial geometry is derived from high-resolution BodyParts3D anatomical polygon sets. Geometries are centered at the clinical heart centroid (X = 20.10 mm, Y = -124.14 mm, Z = 1236.43 mm) and mapped to continuous vertex risk shaders. Vessel hues represent model-predicted stenosis risk probabilities, giving clinicians spatial context for statistical risk predictions.
          </p>
        </div>
      </section>

      {/* Mandatory Clinical & Ethical Boundary Notice */}
      <section className="glass-panel-strong rounded-2xl p-5 sm:p-6 border border-amber-500/30 shadow-spatial space-y-3 bg-amber-500/5">
        <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
          <AlertTriangle className="w-4 h-4" />
          <h3>Clinical & Anatomical Boundary Notice</h3>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          CoroVista is an educational and clinical decision-support research prototype. Model outputs indicate statistical probability of obstructive luminal stenosis (≥ 50%) based on the Z-Alizadeh Sani cohort ($N=303$). They do not establish biological causality and are not physical spatial coordinates on coronary anatomy.
        </p>
      </section>
    </div>
  )
}
