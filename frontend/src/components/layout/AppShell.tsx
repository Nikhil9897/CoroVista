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
  const location = useLocation()

  // Dashboard and simulator get full-bleed spatial layout
  const isSpatialPage = location.pathname === "/dashboard" || location.pathname === "/simulator"

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Spatial Navigation Rail */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-[56px]">
        <TopBar health={health} onOpenSidebar={() => setSidebarOpen(true)} />

        <main
          className={`flex-1 ${
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
