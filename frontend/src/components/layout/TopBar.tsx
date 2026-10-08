import React from "react"
import { Menu, ShieldCheck } from "lucide-react"
import type { HealthResponse } from "@/types/patient"
import { SystemStatusBadge } from "@/components/common/SystemStatusBadge"

interface TopBarProps {
  health: HealthResponse | null
  onOpenSidebar: () => void
}

export const TopBar: React.FC<TopBarProps> = ({ health, onOpenSidebar }) => {
  return (
    <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-md border-b border-border px-4 lg:px-8 py-3.5 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSidebar}
          className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary lg:hidden cursor-pointer"
          aria-label="Open navigation sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold tracking-tight text-foreground">
              CoroVista
            </h2>
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium text-primary px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20">
              <ShieldCheck className="w-3 h-3" />
              <span>Decision Support</span>
            </span>
          </div>
          <p className="text-xs text-muted-foreground hidden md:block">
            Cardiovascular Risk Visualization & Prediction
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <SystemStatusBadge health={health} />
      </div>
    </header>
  )
}
