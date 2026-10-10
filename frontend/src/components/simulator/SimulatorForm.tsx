import React, { useState, useMemo } from "react"
import { Search, X } from "lucide-react"
import type { ClinicalCategory, SimulatorFeatureMeta } from "@/lib/simulatorRegistry"
import { SIMULATOR_FEATURES } from "@/lib/simulatorRegistry"
import { KeyFactorsSection } from "./KeyFactorsSection"
import { KEY_FEATURE_NAMES } from "./simulatorConstants"
import { FeatureSection } from "./FeatureSection"
import { ClinicalInput } from "./ClinicalInput"

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
  const [searchQuery, setSearchQuery] = useState("")
  // Only one accordion group open at a time; all start collapsed
  const [activeCategory, setActiveCategory] = useState<ClinicalCategory | null>(null)

  const keyFeatureSet = useMemo(() => new Set<string>(KEY_FEATURE_NAMES), [])

  // Filter features matching search query across all 54 features
  const searchResults: SimulatorFeatureMeta[] = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return []
    return SIMULATOR_FEATURES.filter(
      (f) =>
        f.label.toLowerCase().includes(q) ||
        f.machine_name.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q) ||
        (f.unit && f.unit.toLowerCase().includes(q))
    )
  }, [searchQuery])

  const handleToggleCategory = (cat: ClinicalCategory) => {
    setActiveCategory((prev) => (prev === cat ? null : cat))
  }

  return (
    <div className="space-y-4" role="form" aria-label="Clinical Feature Input Form">
      {/* 1. Feature Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-[#7C9692] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Find a feature (e.g. cholesterol, blood pressure, ST elevation)…"
          className="w-full h-10 pl-9 pr-9 text-xs rounded-xl bg-[#0A1514] border border-[#7C9692]/20 text-[#E8F1EE] placeholder:text-[#7C9692]/60 focus:outline-none focus:border-[#F26F69] transition-colors"
          aria-label="Search clinical features"
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 text-[#7C9692] hover:text-[#E8F1EE]"
            aria-label="Clear search"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* 2. If searching, show search results directly */}
      {searchQuery.trim() ? (
        <div className="instrument-surface rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between text-xs text-[#7C9692]">
            <span>
              Search results for &ldquo;{searchQuery}&rdquo; ({searchResults.length} found)
            </span>
            <button
              onClick={() => setSearchQuery("")}
              className="text-[#F26F69] hover:underline cursor-pointer"
            >
              Clear
            </button>
          </div>

          {searchResults.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {searchResults.map((feat) => (
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
          ) : (
            <p className="text-xs text-[#7C9692] py-4 text-center">
              No matching clinical features found.
            </p>
          )}
        </div>
      ) : (
        <>
          {/* 3. Key Factors Section (Top 10 Clinical Features) */}
          <KeyFactorsSection
            values={values}
            onChange={onChange}
            errors={errors}
            warnings={warnings}
            disabled={disabled}
          />

          {/* 4. Collapsed Accordion Groups for Remaining Features */}
          <div className="space-y-2.5 pt-1">
            <div className="flex items-center justify-between text-xs px-1 text-[#7C9692]">
              <span className="font-medium text-[#E8F1EE] text-[11px] uppercase tracking-wider">
                Additional Diagnostic Categories (44 features)
              </span>
              <span className="text-[10px] font-mono text-[#7C9692]/60">
                One group open at a time
              </span>
            </div>

            {CATEGORIES.map((cat) => {
              // Exclude features already presented in the Key Factors section
              const remainingFeatures = SIMULATOR_FEATURES.filter(
                (f) => f.category === cat && !keyFeatureSet.has(f.machine_name)
              )

              if (remainingFeatures.length === 0) return null

              return (
                <FeatureSection
                  key={cat}
                  category={cat}
                  features={remainingFeatures}
                  values={values}
                  onChange={onChange}
                  errors={errors}
                  warnings={warnings}
                  disabled={disabled}
                  isOpen={activeCategory === cat}
                  onToggle={() => handleToggleCategory(cat)}
                />
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
