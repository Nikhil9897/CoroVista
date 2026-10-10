import React from "react"
import { AlertCircle, AlertTriangle } from "lucide-react"
import type { SimulatorFeatureMeta } from "@/lib/simulatorRegistry"

interface ClinicalInputProps {
  feature: SimulatorFeatureMeta
  value: string | number | boolean | undefined
  onChange: (value: string | number) => void
  error?: string
  warning?: string
  disabled?: boolean
}

export const ClinicalInput: React.FC<ClinicalInputProps> = ({
  feature,
  value,
  onChange,
  error,
  warning,
  disabled = false,
}) => {
  const inputId = `input-${feature.machine_name.replace(/\s+/g, "-")}`

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value
    if (raw === "") {
      onChange("")
      return
    }
    const parsed = Number(raw)
    onChange(isNaN(parsed) ? raw : parsed)
  }

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const parsed = Number(e.target.value)
    onChange(parsed)
  }

  const numericVal = typeof value === "number" ? value : Number(value)
  const isNumericValid = !isNaN(numericVal)

  return (
    <div className="space-y-2 p-3 rounded-xl bg-[#0A1514]/50 border border-[#7C9692]/15 hover:border-[#7C9692]/30 transition-colors group">
      {/* Label and Unit Row */}
      <div className="flex items-baseline justify-between gap-2 min-h-[18px]">
        <label
          htmlFor={inputId}
          className="text-xs font-medium text-[#E8F1EE] cursor-pointer truncate"
          title={feature.description}
        >
          {feature.label}
        </label>
        {feature.unit && (
          <span className="text-[10px] text-[#7C9692] font-mono shrink-0">
            {feature.unit}
          </span>
        )}
      </div>

      {/* Control Row based on Type */}
      {feature.type === "numeric" ? (
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            {feature.range && isNumericValid && (
              <input
                type="range"
                min={feature.range.min}
                max={feature.range.max}
                step={feature.range.step}
                value={Math.min(Math.max(numericVal, feature.range.min), feature.range.max)}
                onChange={handleSliderChange}
                disabled={disabled}
                aria-label={`${feature.label} slider`}
                className="w-full h-1.5 rounded-lg appearance-none cursor-pointer accent-[#F26F69]"
              />
            )}
            <input
              id={inputId}
              name={feature.machine_name}
              aria-label={feature.label}
              type="number"
              value={typeof value === "number" || typeof value === "string" ? value : ""}
              onChange={handleNumberChange}
              min={feature.range?.min}
              max={feature.range?.max}
              step={feature.range?.step || 1}
              disabled={disabled}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? `${inputId}-error` : undefined}
              className={`h-7 px-2 py-0.5 text-xs font-mono rounded-lg bg-[#162C2A] text-[#E8F1EE] text-right border focus:outline-none focus:border-[#F26F69] transition-colors ${
                feature.range ? "w-16" : "w-full"
              } ${
                error
                  ? "border-rose-500 focus:border-rose-400"
                  : "border-[#7C9692]/20 hover:border-[#7C9692]/40"
              }`}
            />
          </div>

          {/* Min/Max shown only on hover/focus */}
          {feature.range && (
            <div className="flex justify-between text-[9px] font-mono text-[#7C9692]/40 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity">
              <span>min {feature.range.min}</span>
              <span>max {feature.range.max}</span>
            </div>
          )}
        </div>
      ) : feature.options && feature.options.length > 2 ? (
        <select
          id={inputId}
          name={feature.machine_name}
          value={String(value)}
          onChange={(e) => {
            const selectedVal = e.target.value
            const isNumericOption = feature.options?.some((o) => typeof o.value === "number")
            onChange(isNumericOption && !isNaN(Number(selectedVal)) ? Number(selectedVal) : selectedVal)
          }}
          disabled={disabled}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : undefined}
          className={`w-full h-7 px-2 text-xs rounded-lg bg-[#162C2A] border text-[#E8F1EE] focus:outline-none focus:border-[#F26F69] transition-colors cursor-pointer ${
            error
              ? "border-rose-500 focus:border-rose-400"
              : "border-[#7C9692]/20 hover:border-[#7C9692]/40"
          }`}
        >
          {feature.options?.map((opt) => (
            <option key={String(opt.value)} value={String(opt.value)} className="bg-[#112321] text-[#E8F1EE]">
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        /* Binary 2-option Segmented Selector */
        <div
          role="radiogroup"
          aria-label={feature.label}
          className="grid grid-cols-2 gap-1 p-0.5 bg-[#162C2A]/60 rounded-lg border border-[#7C9692]/15"
        >
          {feature.options?.map((opt) => {
            const isSelected =
              String(value).toLowerCase() === String(opt.value).toLowerCase() ||
              (typeof opt.value === "number" && Number(value) === opt.value)

            return (
              <button
                key={String(opt.value)}
                type="button"
                role="radio"
                aria-checked={isSelected}
                disabled={disabled}
                onClick={() => onChange(opt.value)}
                className={`h-6 px-2 text-[11px] font-medium rounded-md transition-all cursor-pointer ${
                  isSelected
                    ? "bg-[#0A1514] text-[#E8F1EE] border border-[#7C9692]/30 font-semibold shadow-xs"
                    : "text-[#7C9692] hover:text-[#E8F1EE]"
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      )}

      {/* Field-level error */}
      {error && (
        <p
          id={`${inputId}-error`}
          role="alert"
          className="text-[11px] text-destructive flex items-center gap-1 font-medium mt-1"
        >
          <AlertCircle className="w-3 h-3 shrink-0" />
          <span>{error}</span>
        </p>
      )}

      {/* Field-level non-blocking warning */}
      {warning && !error && (
        <p
          role="note"
          className="text-[10px] text-amber-400 flex items-center gap-1 mt-0.5 leading-tight"
        >
          <AlertTriangle className="w-2.5 h-2.5 shrink-0" />
          <span>{warning}</span>
        </p>
      )}
    </div>
  )
}
