import React, { useState } from "react"
import { Outlet, useLocation } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { TopBar } from "./TopBar"
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner"
import type { HealthResponse } from "@/types/patient"

interface AppShellProps {
  health: HealthResponse | null
}

export const AppShell: React.FC<AppShellProps> = ({ health }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const location = useLocation()

  // Dashboard and simulator get full-bleed spatial layout
  const isSpatialPage = location.pathname === "/dashboard" || location.pathname === "/simulator"

  return (
    <div className="min-h-screen bg-[#011719] text-foreground flex flex-col">
      {/* TopBar anchored at top across full width - logo never shifts */}
      <TopBar health={health} onOpenSidebar={() => setSidebarOpen(true)} />

      <div className="flex-1 flex relative min-h-0">
        {/* Spatial Navigation Rail */}
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          isExpanded={isExpanded}
          onToggleExpanded={() => setIsExpanded(!isExpanded)}
          onExpand={() => setIsExpanded(true)}
        />

        {/* Main Content Area */}
        <main
          className={`flex-1 min-w-0 lg:pl-[76px] ${
            isSpatialPage
              ? "px-0 py-0"
              : "px-4 lg:px-8 py-6 max-w-5xl w-full mx-auto"
          }`}
        >
          <Outlet />
          {!isSpatialPage && <DisclaimerBanner className="mt-8" />}
        </main>
      </div>
    </div>
  )
}
