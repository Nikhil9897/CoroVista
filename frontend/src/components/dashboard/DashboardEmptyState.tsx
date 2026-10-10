import React from "react"

interface DashboardEmptyStateProps {
  onLoadDemo: () => void
  isLoading?: boolean
}

export const DashboardEmptyState: React.FC<DashboardEmptyStateProps> = ({
  onLoadDemo,
  isLoading = false,
}) => {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[70vh] px-6 text-center select-none"
      role="region"
      aria-label="No patient loaded"
    >
      {/* Ambient glow orb behind logo */}
      <div className="relative mb-8">
        <div
          className="absolute inset-0 rounded-full blur-[48px] opacity-20"
          style={{ background: "radial-gradient(circle, hsl(12 76% 62%) 0%, transparent 70%)", width: "140px", height: "140px", transform: "translate(-20%, -20%)" }}
          aria-hidden="true"
        />
        <div className="relative w-24 h-24 rounded-2xl bg-surface-1 border border-border/40 flex items-center justify-center shadow-[0_0_40px_-8px_hsl(12_76%_62%/0.15)]">
          <img
            src="/corovista-heart.png"
            alt=""
            aria-hidden="true"
            className="w-16 h-16 object-contain drop-shadow-[0_0_20px_rgba(242,111,105,0.3)]"
          />
        </div>
      </div>

      {/* Serif headline */}
      <h2 className="font-display text-3xl sm:text-4xl text-foreground mb-3 leading-tight">
        No patient analyzed yet
      </h2>
      <p className="text-sm text-muted-foreground max-w-sm leading-relaxed mb-8">
        Load a synthetic demo profile to compute coronary artery disease risk,
        vessel stenosis probabilities, and SHAP feature attributions.
      </p>

      {/* Single coral CTA */}
      <button
        type="button"
        onClick={onLoadDemo}
        disabled={isLoading}
        className="inline-flex items-center gap-2.5 px-7 py-3 rounded-full text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-[0_4px_20px_hsl(12_76%_62%/0.3)] hover:shadow-[0_6px_28px_hsl(12_76%_62%/0.4)] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
        aria-label={isLoading ? "Loading demo patient analysis" : "Load demo patient and analyze"}
      >
        {isLoading ? (
          <>
            <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" aria-hidden="true" />
            <span>Analyzing…</span>
          </>
        ) : (
          <span>Load demo patient</span>
        )}
      </button>

      {/* Single muted source note — no LaTeX */}
      <p className="mt-6 text-[11px] text-muted-foreground/50 font-mono">
        Synthetic benchmark · Z-Alizadeh Sani schema · 54 features
      </p>
    </div>
  )
}
