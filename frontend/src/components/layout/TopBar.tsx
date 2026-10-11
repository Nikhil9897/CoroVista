import React from "react"
import { Menu } from "lucide-react"
import { Link } from "react-router-dom"
import type { HealthResponse } from "@/types/patient"
import { SystemStatusBadge } from "@/components/common/SystemStatusBadge"

interface TopBarProps {
  health: HealthResponse | null
  onOpenSidebar: () => void
}

export const TopBar: React.FC<TopBarProps> = ({ health, onOpenSidebar }) => {
  return (
    <header className="sticky top-0 z-30 bg-[#011719]/90 backdrop-blur-xl border-b border-white/[0.08] px-4 lg:px-6 py-2.5 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3.5">
        {/* Mobile menu toggle */}
        <button
          onClick={onOpenSidebar}
          className="p-2 rounded-xl text-[#7C9692] hover:text-[#E8F1EE] hover:bg-white/[0.06] lg:hidden cursor-pointer transition-colors"
          aria-label="Open navigation sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Enlarged Prominent CoroVista Logo */}
        <Link
          to="/"
          className="flex items-center gap-3 group/logo focus:outline-hidden"
          title="CoroVista — Cardiovascular AI Platform"
        >
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-white/[0.06] border border-white/15 p-1.5 flex items-center justify-center shrink-0 shadow-lg shadow-black/40 backdrop-blur-md group-hover/logo:border-[#2dd4bf]/40 group-hover/logo:scale-105 transition-all">
            <img
              src="/corovista-heart.png"
              alt="CoroVista Logo"
              className="w-7 h-7 sm:w-8 sm:h-8 object-contain drop-shadow-[0_0_10px_rgba(45,212,191,0.35)]"
            />
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-sm sm:text-base tracking-tight text-[#E8F1EE] leading-none">
                CoroVista
              </h1>
              <span className="w-1.5 h-1.5 rounded-full bg-[#2dd4bf] shadow-[0_0_8px_#2dd4bf] animate-pulse" />
            </div>
            <p className="text-[11px] text-[#7C9692] font-mono leading-tight mt-1 hidden sm:block">
              Cardiovascular Risk Visualization &bull; Stenosis Prediction System
            </p>
          </div>
        </Link>
      </div>

      {/* Right: API Status Badge */}
      <div className="flex items-center gap-3">
        <SystemStatusBadge health={health} />
      </div>
    </header>
  )
}
