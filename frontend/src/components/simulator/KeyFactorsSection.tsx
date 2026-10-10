import React from "react"
import { Sparkles } from "lucide-react"
import type { PatientRecord } from "@/types/patient"
import { SIMULATOR_FEATURES, type SimulatorFeatureMeta } from "@/lib/simulatorRegistry"
import { ClinicalInput } from "./ClinicalInput"
import { KEY_FEATURE_NAMES } from "./simulatorConstants"

interface KeyFactorsSectionProps {
  values: PatientRecord
  onChange: (name: string, value: string | number) => void
  errors?: Record<string, string>
  warnings?: Record<string, string>
  disabled?: boolean
}

export const KeyFactorsSection: React.FC<KeyFactorsSectionProps> = ({
  values,
  onChange,
  errors = {},
  warnings = {},
  disabled = false,
}) => {
  const featureMetaMap = React.useMemo(() => {
    const map = new Map<string, SimulatorFeatureMeta>()
    for (const f of SIMULATOR_FEATURES) {
      map.set(f.machine_name, f)
    }
    return map
  }, [])

  return (
    <div
      className="instrument-surface rounded-2xl p-5 select-none space-y-4"
      role="region"
      aria-label="Key Clinical Risk Factors"
    >
      <div className="flex items-center justify-between pb-2 border-b border-[#7C9692]/15">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-full bg-[#F26F69]/15 flex items-center justify-center text-[#F26F69]">
            <Sparkles className="w-3 h-3" />
          </div>
          <div>
            <h3 className="font-semibold text-xs text-[#E8F1EE] tracking-tight">
              Key Clinical Factors
            </h3>
            <p className="text-[10px] text-[#7C9692]">
              Primary diagnostic drivers with highest SHAP feature attribution
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-[#7C9692] bg-[#0A1514]/60 px-2 py-0.5 rounded-full border border-[#7C9692]/15">
          10 key inputs
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {KEY_FEATURE_NAMES.map((name) => {
          const meta = featureMetaMap.get(name)
          if (!meta) return null

          return (
            <ClinicalInput
              key={name}
              feature={meta}
              value={values[name]}
              onChange={(val) => onChange(name, val)}
              error={errors[name]}
              warning={warnings[name]}
              disabled={disabled}
            />
          )
        })}
      </div>
    </div>
  )
}
