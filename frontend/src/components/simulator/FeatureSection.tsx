import React, { useState } from "react"
import {
  Users,
  Stethoscope,
  Activity,
  FlaskConical,
  ChevronDown,
  ChevronUp,
} from "lucide-react"
import type { ClinicalCategory, SimulatorFeatureMeta } from "@/lib/simulatorRegistry"
import { CATEGORY_METADATA } from "@/lib/simulatorRegistry"
import { ClinicalInput } from "./ClinicalInput"

interface FeatureSectionProps {
  category: ClinicalCategory
  features: SimulatorFeatureMeta[]
  values: Record<string, any>
  onChange: (name: string, value: string | number) => void
  errors: Record<string, string>
  warnings: Record<string, string>
  disabled?: boolean
  defaultOpen?: boolean
}

export const FeatureSection: React.FC<FeatureSectionProps> = ({
  category,
  features,
  values,
  onChange,
  errors,
  warnings,
  disabled = false,
  defaultOpen = true,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const meta = CATEGORY_METADATA[category]

  // Section icon resolver
  const renderIcon = () => {
    switch (category) {
      case "Demographic":
        return <Users className="w-4 h-4 text-primary" />
      case "Symptoms / Examination":
        return <Stethoscope className="w-4 h-4 text-primary" />
      case "ECG":
        return <Activity className="w-4 h-4 text-primary" />
      case "Laboratory / Echo":
        return <FlaskConical className="w-4 h-4 text-primary" />
      default:
        return null
    }
  }

  // Count errors in this section
  const sectionErrors = features.filter((f) => errors[f.machine_name]).length

  return (
    <div
      className="border border-border/80 bg-card rounded-xl overflow-hidden shadow-xs transition-colors"
      role="region"
      aria-labelledby={`section-heading-${category.replace(/[\s/]+/g, "-")}`}
    >
      {/* Section Header Button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        className="w-full px-4 py-3.5 flex items-center justify-between text-left hover:bg-muted/30 transition-colors cursor-pointer border-b border-border/40"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
            {renderIcon()}
          </div>
          <div>
            <h3
              id={`section-heading-${category.replace(/[\s/]+/g, "-")}`}
              className="text-sm font-semibold text-foreground flex items-center gap-2"
            >
              <span>{meta.title}</span>
              <span className="text-[11px] font-mono font-normal text-muted-foreground bg-secondary px-2 py-0.2 rounded-full border border-border/50">
                {features.length} features
              </span>
              {sectionErrors > 0 && (
                <span className="text-[10px] font-medium text-destructive bg-destructive/10 px-1.5 py-0.5 rounded border border-destructive/30">
                  {sectionErrors} invalid
                </span>
              )}
            </h3>
            <p className="text-xs text-muted-foreground hidden sm:block mt-0.5">
              {meta.description}
            </p>
          </div>
        </div>

        <div className="text-muted-foreground">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Grid of Inputs */}
      {isOpen && (
        <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 bg-card/40">
          {features.map((feat) => (
            <ClinicalInput
              key={feat.machine_name}
              feature={feat}
              value={values[feat.machine_name]}
              onChange={(val) => onChange(feat.machine_name, val)}
              error={errors[feat.machine_name]}
              warning={warnings[feat.machine_name]}
              disabled={disabled}
            />
          ))}
        </div>
      )}
    </div>
  )
}
