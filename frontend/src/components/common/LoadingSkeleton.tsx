import React from "react"

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="space-y-6 animate-pulse" role="status" aria-label="Analyzing patient data">
      {/* Top Patient Summary Skeleton */}
      <div className="h-14 rounded-lg bg-card/60 border border-border" />

      {/* Main Grid: CAD Risk + Anatomy placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 h-64 rounded-xl bg-card/60 border border-border" />
        <div className="lg:col-span-2 h-64 rounded-xl bg-card/60 border border-border" />
      </div>

      {/* Three Vessel Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="h-44 rounded-xl bg-card/60 border border-border" />
        <div className="h-44 rounded-xl bg-card/60 border border-border" />
        <div className="h-44 rounded-xl bg-card/60 border border-border" />
      </div>

      {/* SHAP Explanation Section */}
      <div className="h-80 rounded-xl bg-card/60 border border-border" />

      <span className="sr-only">Computing multi-target predictions and SHAP attributions...</span>
    </div>
  )
}
