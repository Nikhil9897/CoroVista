import React, { useState } from "react"
import { usePatientAnalysis } from "@/hooks/usePatientAnalysis"
import type { TargetName } from "@/types/prediction"
import { PatientSummaryHeader } from "@/components/dashboard/PatientSummaryHeader"
import { CadRiskCard } from "@/components/predictions/CadRiskCard"
import { VesselRiskOverview } from "@/components/predictions/VesselRiskOverview"
import { AnatomyPlaceholder } from "@/components/predictions/AnatomyPlaceholder"
import { ExplanationPanel } from "@/components/explanations/ExplanationPanel"
import { EmptyState } from "@/components/common/EmptyState"
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton"
import { ErrorAlert } from "@/components/common/ErrorAlert"

export const Dashboard: React.FC = () => {
  const {
    patient,
    analysis,
    isLoading,
    error,
    loadDemoPatient,
    clearPatient,
    analyze,
  } = usePatientAnalysis()

  const [selectedTarget, setSelectedTarget] = useState<TargetName>("cath")

  return (
    <div className="space-y-6" role="region" aria-label="Clinical Risk Dashboard">
      {/* Patient Summary & Controls */}
      <PatientSummaryHeader
        patient={patient}
        isLoading={isLoading}
        onLoadDemo={loadDemoPatient}
        onClear={clearPatient}
      />

      {/* Error Banner */}
      {error && (
        <ErrorAlert
          error={error}
          onRetry={patient ? () => analyze(patient) : loadDemoPatient}
        />
      )}

      {/* Main Content Area: Loading vs Empty vs Results */}
      {isLoading ? (
        <LoadingSkeleton />
      ) : !analysis ? (
        <EmptyState onLoadDemo={loadDemoPatient} isLoading={isLoading} />
      ) : (
        <div className="space-y-6 animate-in fade-in-50 duration-500">
          {/* Top Row: Overall CAD Primary Risk + 3D Anatomy Placeholder */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <CadRiskCard prediction={analysis.predictions.cath} className="h-full" />
            </div>
            <div className="lg:col-span-2">
              <AnatomyPlaceholder className="h-full" />
            </div>
          </div>

          {/* Middle Row: Vessel-Specific Stenosis (LAD, LCX, RCA) */}
          <VesselRiskOverview
            predictions={analysis.predictions}
            selectedTarget={selectedTarget}
            onSelectTarget={(target) => setSelectedTarget(target)}
          />

          {/* Bottom Row: Local SHAP Feature Explanations */}
          <ExplanationPanel
            explanations={analysis.explanations}
            selectedTarget={selectedTarget}
            onSelectTarget={(target) => setSelectedTarget(target)}
          />
        </div>
      )}
    </div>
  )
}
