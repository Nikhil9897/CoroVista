import React, { useState } from "react"
import { ChevronsUpDown } from "lucide-react"
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
  // Demographic open by default so initial view is compact
  const [openSections, setOpenSections] = useState<Record<ClinicalCategory, boolean>>({
    Demographic: true,
    "Symptoms / Examination": false,
    ECG: false,
    "Laboratory / Echo": false,
  })

  const toggleSection = (cat: ClinicalCategory) => {
    setOpenSections((prev) => ({ ...prev, [cat]: !prev[cat] }))
  }

  const allOpen = Object.values(openSections).every(Boolean)

  const toggleAll = () => {
    const nextState = !allOpen
    setOpenSections({
      Demographic: nextState,
      "Symptoms / Examination": nextState,
      ECG: nextState,
      "Laboratory / Echo": nextState,
    })
  }

  return (
    <div className="space-y-3.5" role="form" aria-label="Clinical Feature Input Form">
      {/* Category Accordion Header Toolbar */}
      <div className="flex items-center justify-between text-xs px-1 text-muted-foreground">
        <span className="font-medium text-foreground">
          Clinical Input Categories (54 features)
        </span>
        <button
          type="button"
          onClick={toggleAll}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-secondary/80 hover:bg-secondary text-foreground border border-border/60 transition-colors cursor-pointer"
        >
          <ChevronsUpDown className="w-3 h-3 text-muted-foreground" />
          <span>{allOpen ? "Collapse All Groups" : "Expand All Groups"}</span>
        </button>
      </div>

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
            isOpen={openSections[cat]}
            onToggle={() => toggleSection(cat)}
          />
        )
      })}
    </div>
  )
}

