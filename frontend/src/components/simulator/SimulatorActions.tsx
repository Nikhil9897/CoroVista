import React, { useState, useRef, useEffect } from "react"
import { Play, RotateCcw, Trash2, Loader2, MoreHorizontal, AlertCircle, Sparkles } from "lucide-react"

interface SimulatorActionsProps {
  onAnalyze: () => void
  onLoadDemo: () => void
  onResetDemo: () => void
  onClearForm?: () => void
  isLoading: boolean
  isDirty?: boolean
  hasResults?: boolean
  hasErrors?: boolean
}

export const SimulatorActions: React.FC<SimulatorActionsProps> = ({
  onAnalyze,
  onResetDemo,
  onClearForm,
  isLoading,
  isDirty = false,
  hasResults = false,
  hasErrors = false,
}) => {
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside)
    }
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [menuOpen])

  return (
    <div
      className="sticky top-14 z-20 instrument-surface rounded-2xl p-3 border border-[#7C9692]/20 shadow-xl backdrop-blur-xl select-none"
      role="toolbar"
      aria-label="Simulator Action Bar"
    >
      <div className="flex items-center justify-between gap-3">
        {/* Left: ONE Primary Coral Action Button */}
        <div className="flex items-center gap-2.5 flex-1 min-w-0">
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isLoading}
            className={`inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md active:scale-[0.98] ${
              isLoading
                ? "bg-[#F26F69]/60 text-[#0A1514] cursor-not-allowed"
                : "bg-[#F26F69] text-[#0A1514] hover:bg-[#F26F69]/90 hover:shadow-[#F26F69]/25 hover:shadow-lg"
            }`}
            aria-label="Analyze Patient"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Evaluating Models...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Analyze Patient</span>
              </>
            )}
          </button>

          <span className="text-[11px] text-[#7C9692]/60 hidden sm:inline-block truncate">
            Demo / synthetic patient — not a real patient record
          </span>

          {isDirty && hasResults && !isLoading && (
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-mono text-[#F26F69] bg-[#F26F69]/10 px-2 py-0.5 rounded-md border border-[#F26F69]/20 truncate">
              <Sparkles className="w-3 h-3 shrink-0" />
              <span>Unsent edits</span>
            </span>
          )}

          {hasErrors && (
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] text-rose-300 bg-rose-500/15 px-2 py-0.5 rounded-md border border-rose-500/30 truncate">
              <AlertCircle className="w-3 h-3 shrink-0" />
              <span>Fix invalid fields</span>
            </span>
          )}
        </div>

        {/* Right: Small overflow menu for Reset / Clear */}
        <div className="relative shrink-0" ref={menuRef}>
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 rounded-xl text-[#7C9692] hover:text-[#E8F1EE] bg-[#0A1514]/60 hover:bg-[#112321] border border-[#7C9692]/15 transition-colors cursor-pointer"
            title="Form actions menu"
            aria-expanded={menuOpen}
            aria-label="Form actions menu"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>

          <div
            className={`absolute right-0 top-full mt-2 w-48 instrument-surface rounded-xl p-1.5 shadow-2xl border border-[#7C9692]/25 z-50 transition-all duration-150 ${
              menuOpen ? "opacity-100 scale-100 pointer-events-auto" : "opacity-0 scale-95 pointer-events-none"
            }`}
            role="menu"
          >
            <button
              type="button"
              onClick={() => {
                setMenuOpen(false)
                onResetDemo()
              }}
              disabled={isLoading}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-[#E8F1EE] hover:bg-[#162C2A] transition-colors cursor-pointer text-left"
              role="button"
              aria-label="Reset to Demo Values"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#2dd4bf]" />
              <span>Reset to Demo Values</span>
            </button>

            {onClearForm && (
              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false)
                  onClearForm()
                }}
                disabled={isLoading}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-rose-300 hover:bg-rose-950/20 transition-colors cursor-pointer text-left"
                role="button"
                aria-label="Clear form"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-400" />
                <span>Clear form</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
