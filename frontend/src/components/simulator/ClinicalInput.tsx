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
    <div className="space-y-2 p-3 rounded-xl bg-surface-1/70 border border-border/60 hover:border-border transition-colors">
      {/* Label and Unit Row */}
      <div className="flex items-start justify-between gap-1.5 min-h-[20px]">
        <label
          htmlFor={inputId}
          className="text-xs font-semibold text-foreground cursor-pointer flex items-center flex-wrap gap-1 leading-snug tracking-tight"
          title={feature.description}
        >
          <span>{feature.label}</span>
          {feature.unit && (
            <span className="text-[10px] text-muted-foreground font-mono bg-surface-2 px-1.5 py-0.5 rounded border border-border/50 shrink-0 font-normal">
              {feature.unit}
            </span>
          )}
        </label>

        {feature.observedRange && (
          <span
            className="text-[10px] text-muted-foreground/70 font-mono shrink-0 whitespace-nowrap pt-0.5"
            title={`Observed cohort range: ${feature.observedRange}`}
          >
            {feature.observedRange.split("(")[0].trim()}
          </span>
        )}
      </div>

      {/* Control Row based on Type */}
      {feature.type === "numeric" ? (
        <div className="space-y-1.5">
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
            className={`w-full h-8 px-2.5 py-1 text-xs font-mono rounded-lg bg-surface-2 border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-colors ${
              error
                ? "border-destructive focus:ring-destructive"
                : "border-border/70 hover:border-border"
            }`}
          />

          {/* Range Slider with Min/Max Endpoints if bounded */}
          {feature.range && isNumericValid && (
            <div className="flex items-center gap-1.5 pt-0.5">
              <span className="text-[9px] font-mono text-muted-foreground/70 shrink-0">
                {feature.range.min}
              </span>
              <input
                type="range"
                min={feature.range.min}
                max={feature.range.max}
                step={feature.range.step}
                value={Math.min(Math.max(numericVal, feature.range.min), feature.range.max)}
                onChange={handleSliderChange}
                disabled={disabled}
                aria-label={`${feature.label} slider`}
                className="w-full h-1.5 bg-surface-3 rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <span className="text-[9px] font-mono text-muted-foreground/70 shrink-0">
                {feature.range.max}
              </span>
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
          className={`w-full h-8 px-2.5 py-1 text-xs rounded-lg bg-surface-2 border text-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-colors cursor-pointer ${
            error
              ? "border-destructive focus:ring-destructive"
              : "border-border/70 hover:border-border"
          }`}
        >
          {feature.options?.map((opt) => (
            <option key={String(opt.value)} value={String(opt.value)}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        /* Binary 2-option Segmented Selector */
        <div
          role="radiogroup"
          aria-label={feature.label}
          className="grid grid-cols-2 gap-1 p-0.5 bg-surface-2 rounded-lg border border-border/60"
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
                className={`h-7 px-2 text-xs font-medium rounded-md transition-all cursor-pointer ${
                  isSelected
                    ? "bg-surface-3 text-foreground shadow-xs border border-border/80 font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-surface-2/60"
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
