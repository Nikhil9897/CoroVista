import React from "react"
import type { ClinicalCategory } from "@/lib/simulatorRegistry"
import { SIMULATOR_FEATURES } from "@/lib/simulatorRegistry"
import { FeatureSection } from "./FeatureSection"

interface SimulatorFormProps {
  values: Record<string, any>
  onChange: (name: string, value: string | number) => void
  errors: Record<string, string>
  warnings: Record<string, string>
  disabled?: boolean
}

const CATEGORIES: ClinicalCategory[] = [
  "Demographic",
  "Symptoms / Examination",
  "ECG",
  "Laboratory / Echo",
]

export const SimulatorForm: React.FC<SimulatorFormProps> = ({
  values,
  onChange,
  errors,
  warnings,
  disabled = false,
}) => {
  return (
    <div className="space-y-4" role="form" aria-label="Clinical Feature Input Form">
      {CATEGORIES.map((cat) => {
        const catFeatures = SIMULATOR_FEATURES.filter((f) => f.category === cat)

        return (
          <FeatureSection
            key={cat}
            category={cat}
            features={catFeatures}
            values={values}
            onChange={onChange}
            errors={errors}
            warnings={warnings}
            disabled={disabled}
            defaultOpen={true}
          />
        )
      })}
    </div>
  )
}
