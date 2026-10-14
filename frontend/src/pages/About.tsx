import React from "react"
import { Activity, Eye, ShieldAlert } from "lucide-react"

export const About: React.FC = () => {
  return (
    <div
      className="min-h-[calc(100vh-44px)] clinical-instrument px-4 sm:px-8 lg:px-12 py-10 sm:py-16 w-full"
      role="region"
      aria-label="About CoroVista"
    >
      <div className="max-w-4xl mx-auto space-y-16">
        {/* Editorial Header */}
        <header className="space-y-4">
          <span className="text-xs font-medium tracking-widest text-[#2dd4bf] uppercase">
            Clinical Overview &amp; Architecture
          </span>
          <h1 className="font-display text-4xl sm:text-5xl text-[#E8F1EE] font-normal tracking-tight">
            About CoroVista
          </h1>
          <p className="text-base sm:text-lg text-[#7C9692] font-light leading-relaxed">
            Cardiovascular Risk Visualization &amp; Multi-Target Stenosis Prediction System
          </p>
          <p className="text-sm text-[#7C9692]/80 leading-relaxed pt-2 max-w-2xl font-light">
            CoroVista translates routine clinical examinations into comprehensive, vessel-by-vessel
            coronary risk assessments — paired with interactive 3D anatomical visualization and transparent
            feature explainability.
          </p>
        </header>

        {/* Core Pillars: Minimal & Human-Readable */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-2">
          <div className="border-t border-white/10 pt-4 space-y-1">
            <span className="text-2xl sm:text-3xl font-light text-[#E8F1EE]">303</span>
            <p className="text-xs font-medium text-[#E8F1EE]">Clinical Patient Cohort</p>
            <p className="text-xs text-[#7C9692]">Validated on the authoritative Z-Alizadeh Sani clinical registry.</p>
          </div>
          <div className="border-t border-white/10 pt-4 space-y-1">
            <span className="text-2xl sm:text-3xl font-light text-[#E8F1EE]">54</span>
            <p className="text-xs font-medium text-[#E8F1EE]">Clinical Biomarkers</p>
            <p className="text-xs text-[#7C9692]">Evaluating routine demographics, ECG findings, labs, and echo data.</p>
          </div>
          <div className="border-t border-white/10 pt-4 space-y-1">
            <span className="text-2xl sm:text-3xl font-light text-[#E8F1EE]">4</span>
            <p className="text-xs font-medium text-[#E8F1EE]">Independent Vessels</p>
            <p className="text-xs text-[#7C9692]">Simultaneously predicting overall CAD and branch-specific stenosis.</p>
          </div>
        </div>

        {/* Section 1: The Four Coronary Endpoints */}
        <section className="space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-medium text-[#E8F1EE]">Multi-Target Vessel Assessment</h2>
            <p className="text-xs sm:text-sm text-[#7C9692] leading-relaxed">
              Instead of reducing heart health to a single broad score, CoroVista evaluates the patient across four individual clinical endpoints:
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Cath */}
            <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.08] space-y-2 hover:border-white/20 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-[#E8F1EE]">Overall CAD (Cath)</span>
                <span className="w-2 h-2 rounded-full bg-[#F26F69]" />
              </div>
              <p className="text-xs text-[#7C9692] leading-relaxed">
                Evaluates the overall presence of obstructive coronary artery disease (&ge;50% narrowing across major vessels).
              </p>
              <p className="text-[11px] text-[#7C9692]/60 pt-1">
                Cath (Overall CAD): XGBoost + Platt Sigmoid calibrated pipeline.
              </p>
            </div>

            {/* LAD */}
            <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.08] space-y-2 hover:border-white/20 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-[#E8F1EE]">Left Anterior Descending (LAD)</span>
                <span className="w-2 h-2 rounded-full bg-[#2dd4bf]" />
              </div>
              <p className="text-xs text-[#7C9692] leading-relaxed">
                Assesses the primary artery supplying the front wall, septum, and apex of the heart muscle.
              </p>
              <p className="text-[11px] text-[#7C9692]/60 pt-1">
                Trained with Platt calibration for reliable, well-calibrated probabilities.
              </p>
            </div>

            {/* LCX */}
            <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.08] space-y-2 hover:border-white/20 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-[#E8F1EE]">Left Circumflex (LCX)</span>
                <span className="w-2 h-2 rounded-full bg-cyan-400" />
              </div>
              <p className="text-xs text-[#7C9692] leading-relaxed">
                Monitors blood supply to the lateral and back walls of the left ventricle.
              </p>
              <p className="text-[11px] text-[#7C9692]/60 pt-1">
                Preserves uncalibrated tree margins for subtle lateral wall presentations.
              </p>
            </div>

            {/* RCA */}
            <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.08] space-y-2 hover:border-white/20 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-[#E8F1EE]">Right Coronary Artery (RCA)</span>
                <span className="w-2 h-2 rounded-full bg-amber-400" />
              </div>
              <p className="text-xs text-[#7C9692] leading-relaxed">
                Surveys perfusion to the inferior heart wall and right ventricle, calibrated with an optimized sensitivity threshold.
              </p>
              <p className="text-[11px] text-[#7C9692]/60 pt-1">
                Logistic regression calibrated with an empirical threshold (&theta; = 0.38) for ischemic sensitivity.
              </p>
            </div>
          </div>
        </section>

        {/* Section 2: Transparent Explainability */}
        <section className="space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-medium text-[#E8F1EE]">Transparent Clinical Reasoning</h2>
            <p className="text-xs sm:text-sm text-[#7C9692] leading-relaxed">
              Machine learning in cardiology must never be a black box. CoroVista computes exact mathematical explanations for every patient:
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.08] space-y-2">
              <div className="flex items-center gap-2 text-[#2dd4bf]">
                <Activity className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">Patient-Specific Drivers</span>
              </div>
              <p className="text-xs text-[#7C9692] leading-relaxed">
                Using SHAP (SHapley Additive exPlanations), the platform calculates exactly how much each individual biomarker — like age, chest pain type, ST depression, or cholesterol — pulled the patient&apos;s risk higher or lower.
              </p>
            </div>

            <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.08] space-y-2">
              <div className="flex items-center gap-2 text-[#2dd4bf]">
                <Eye className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">3D Anatomical Twin</span>
              </div>
              <p className="text-xs text-[#7C9692] leading-relaxed">
                Numerical risk probabilities map directly onto high-resolution 3D coronary geometry. Color gradients shift intuitively from healthy jade to warning coral, giving clinicians visual anatomical context for statistical findings.
              </p>
            </div>
          </div>
        </section>

        {/* Section 3: Responsible Clinical Boundary */}
        <section className="rounded-2xl p-6 bg-amber-500/[0.04] border border-amber-500/20 space-y-2">
          <div className="flex items-center gap-2 text-amber-400">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <h3 className="text-xs font-semibold uppercase tracking-wider">Clinical Decision-Support Notice</h3>
          </div>
          <p className="text-xs text-[#7C9692] leading-relaxed">
            CoroVista is an educational and investigative clinical decision-support tool. It computes statistical risk probabilities based on validated patient cohorts. It does not replace formal invasive angiography, cardiac catheterization, or the professional judgment of a licensed cardiologist.
          </p>
        </section>
      </div>
    </div>
  )
}
