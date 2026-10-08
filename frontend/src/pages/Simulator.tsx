import React from "react"
import { Sliders, Sparkles } from "lucide-react"

export const Simulator: React.FC = () => {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[500px] p-8 border border-border/80 rounded-xl bg-card/60 text-center relative overflow-hidden"
      role="region"
      aria-label="Patient Simulator Placeholder"
    >
      <div className="w-16 h-16 rounded-2xl bg-secondary border border-border flex items-center justify-center mb-4 text-primary shadow-sm">
        <Sliders className="w-8 h-8" />
      </div>

      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20 mb-3">
        <Sparkles className="w-3.5 h-3.5" />
        <span>Stage 5C Feature Roadmap</span>
      </div>

      <h2 className="text-xl font-bold tracking-tight text-foreground mb-2">
        Patient Simulator
      </h2>

      <p className="text-sm text-muted-foreground max-w-md leading-relaxed mb-6">
        Modify clinical parameters and observe how model predictions change in real time. Full parameter sliders across Demographics, ECG, and Biomarkers will be enabled in Stage 5C.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-lg text-left">
        <div className="p-3 rounded-lg bg-secondary/40 border border-border/50 text-xs">
          <span className="font-semibold text-foreground block mb-0.5">Demographics</span>
          <span className="text-muted-foreground">Age, BMI, Sex, Blood Pressure</span>
        </div>
        <div className="p-3 rounded-lg bg-secondary/40 border border-border/50 text-xs">
          <span className="font-semibold text-foreground block mb-0.5">ECG Findings</span>
          <span className="text-muted-foreground">ST Elevation, T-Wave Inversion, Q Wave</span>
        </div>
        <div className="p-3 rounded-lg bg-secondary/40 border border-border/50 text-xs">
          <span className="font-semibold text-foreground block mb-0.5">Biomarkers & Echo</span>
          <span className="text-muted-foreground">EF-TTE, RWMA, Lipid Panel</span>
        </div>
      </div>
    </div>
  )
}
