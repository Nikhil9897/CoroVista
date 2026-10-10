import React from "react"
import { Menu } from "lucide-react"
import type { HealthResponse } from "@/types/patient"
import { SystemStatusBadge } from "@/components/common/SystemStatusBadge"

interface TopBarProps {
  health: HealthResponse | null
  onOpenSidebar: () => void
}

export const TopBar: React.FC<TopBarProps> = ({ health, onOpenSidebar }) => {
  return (
    <header className="sticky top-0 z-30 bg-[#011719]/85 backdrop-blur-md border-b border-white/10 px-4 lg:px-6 py-2.5 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSidebar}
          className="p-1.5 rounded-lg text-[#7C9692] hover:text-[#E8F1EE] hover:bg-[#112321] lg:hidden cursor-pointer transition-colors"
          aria-label="Open navigation sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <img
            src="/corovista-heart.png"
            alt="CoroVista"
            className="w-5 h-5 object-contain lg:hidden"
          />
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-[#E8F1EE] tracking-tight">
              CoroVista
            </span>
            <span className="text-[#7C9692]/40 text-xs hidden sm:inline">&bull;</span>
            <span className="text-xs text-[#7C9692] font-normal tracking-normal hidden sm:inline">
              Cardiovascular Risk Visualization & Prediction
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <SystemStatusBadge health={health} />
      </div>
    </header>
  )
}
