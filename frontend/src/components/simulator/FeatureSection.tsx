import React from "react"
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
import { DEMO_PATIENT } from "@/lib/demoPatient"
import { ClinicalInput } from "./ClinicalInput"

interface FeatureSectionProps {
  category: ClinicalCategory
  features: SimulatorFeatureMeta[]
  values: Record<string, any>
  onChange: (name: string, value: string | number) => void
  errors: Record<string, string>
  warnings: Record<string, string>
  disabled?: boolean
  isOpen?: boolean
  onToggle?: () => void
}

export const FeatureSection: React.FC<FeatureSectionProps> = ({
  category,
  features,
  values,
  onChange,
  errors,
  warnings,
  disabled = false,
  isOpen = false,
  onToggle,
}) => {
  const meta = CATEGORY_METADATA[category]

  const renderIcon = () => {
    switch (category) {
      case "Demographic":
        return <Users className="w-4 h-4 text-[#2dd4bf]" />
      case "Symptoms / Examination":
        return <Stethoscope className="w-4 h-4 text-[#2dd4bf]" />
      case "ECG":
        return <Activity className="w-4 h-4 text-[#2dd4bf]" />
      case "Laboratory / Echo":
        return <FlaskConical className="w-4 h-4 text-[#2dd4bf]" />
      default:
        return null
    }
  }

  // Count errors
  const sectionErrors = features.filter((f) => errors[f.machine_name]).length

  // Count edited features vs demo baseline
  const editedCount = features.filter((f) => {
    const currentVal = values[f.machine_name]
    const baselineVal = DEMO_PATIENT[f.machine_name]
    return currentVal !== undefined && currentVal !== "" && String(currentVal) !== String(baselineVal)
  }).length

  return (
    <div
      className="instrument-surface rounded-2xl overflow-hidden transition-all border border-[#7C9692]/15"
      role="region"
      aria-labelledby={`section-heading-${category.replace(/[\s/]+/g, "-")}`}
    >
      {/* Accordion Header Button */}
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-[#112321]/60 transition-colors cursor-pointer select-none"
      >
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-[#0A1514] border border-[#7C9692]/20 flex items-center justify-center shrink-0">
            {renderIcon()}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span
                id={`section-heading-${category.replace(/[\s/]+/g, "-")}`}
                className="text-xs font-semibold text-[#E8F1EE] tracking-tight"
              >
                {meta.title}
              </span>
              <span className="text-[10px] font-mono text-[#7C9692] bg-[#0A1514] px-1.5 py-0.2 rounded-md border border-[#7C9692]/15">
                {features.length} features
              </span>
              {editedCount > 0 && (
                <span className="text-[10px] font-mono text-[#F26F69] bg-[#F26F69]/10 px-1.5 py-0.2 rounded-md border border-[#F26F69]/25">
                  {editedCount} of {features.length} edited
                </span>
              )}
              {sectionErrors > 0 && (
                <span className="text-[10px] font-medium text-rose-300 bg-rose-500/15 px-1.5 py-0.2 rounded-md border border-rose-500/30">
                  {sectionErrors} invalid
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="text-[#7C9692] p-1">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Grid of Inputs (visible when accordion is open, hidden when collapsed) */}
      <div
        className={`p-3.5 pt-2 grid grid-cols-1 sm:grid-cols-2 gap-2.5 border-t border-[#7C9692]/10 bg-[#071110]/50 animate-in fade-in duration-200 ${
          isOpen ? "" : "hidden"
        }`}
      >
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
    </div>
  )
}
