import React from "react"
import { Box, Sparkles } from "lucide-react"

interface AnatomyPlaceholderProps {
  className?: string
}

export const AnatomyPlaceholder: React.FC<AnatomyPlaceholderProps> = ({ className = "" }) => {
  return (
    <div
      className={`border border-border/80 bg-gradient-to-br from-card/80 to-card/40 rounded-xl p-6 shadow-sm flex flex-col items-center justify-center text-center relative overflow-hidden min-h-[220px] ${className}`}
      role="region"
      aria-label="3D Coronary Anatomy Visualization Placeholder"
    >
      {/* Subtle grid background pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f29370f_1px,transparent_1px),linear-gradient(to_bottom,#1f29370f_1px,transparent_1px)] bg-[size:16px_16px] pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center max-w-sm">
        <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-3 shadow-inner">
          <Box className="w-6 h-6 animate-pulse-subtle" />
        </div>

        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-secondary text-muted-foreground border border-border/60 mb-2">
          <Sparkles className="w-3 h-3 text-primary" />
          <span>Stage 5B Module Interface</span>
        </div>

        <h4 className="text-base font-semibold text-foreground mb-1">
          3D Coronary Anatomy
        </h4>

        <p className="text-xs text-muted-foreground leading-relaxed">
          Interactive anatomical visualization will appear here. Vessel mesh segments will map continuous model probabilities to 3D surface shaders.
        </p>
      </div>
    </div>
  )
}
