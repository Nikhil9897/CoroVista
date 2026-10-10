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
    <header className="sticky top-0 z-30 bg-background/60 backdrop-blur-xl border-b border-border/30 px-4 lg:px-5 py-2.5 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSidebar}
          className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-surface-2 lg:hidden cursor-pointer transition-colors"
          aria-label="Open navigation sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:block">
          <span className="text-xs text-muted-foreground/60 font-medium tracking-wide">
            Cardiovascular Risk Visualization & Prediction
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <SystemStatusBadge health={health} />
      </div>
    </header>
  )
}
