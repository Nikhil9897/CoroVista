import React from "react"
import { Box, Loader2 } from "lucide-react"

interface ViewerLoadingFallbackProps {
  className?: string
  message?: string
}

export const ViewerLoadingFallback: React.FC<ViewerLoadingFallbackProps> = ({
  className = "",
  message = "Loading 3D Coronary Anatomy Model...",
}) => {
  return (
    <div
      className={`border border-border/80 bg-gradient-to-br from-card/90 to-card/50 rounded-xl p-6 shadow-sm flex flex-col items-center justify-center text-center relative overflow-hidden min-h-[360px] ${className}`}
      role="status"
      aria-label="Loading 3D Anatomy Model"
    >
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f29370f_1px,transparent_1px),linear-gradient(to_bottom,#1f29370f_1px,transparent_1px)] bg-[size:16px_16px] pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center max-w-sm">
        <div className="relative w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-3 shadow-inner">
          <Box className="w-7 h-7 text-primary/80" />
          <Loader2 className="w-8 h-8 text-primary absolute animate-spin opacity-80" />
        </div>

        <h4 className="text-sm font-semibold text-foreground mb-1">
          {message}
        </h4>

        <p className="text-xs text-muted-foreground leading-relaxed">
          Parsing verified BodyParts3D vascular geometries and compiling risk shaders.
        </p>
      </div>
    </div>
  )
}
