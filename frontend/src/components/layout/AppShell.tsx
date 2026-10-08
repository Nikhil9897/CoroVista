import React, { useState } from "react"
import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { TopBar } from "./TopBar"
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner"
import type { HealthResponse } from "@/types/patient"

interface AppShellProps {
  health: HealthResponse | null
}

export const AppShell: React.FC<AppShellProps> = ({ health }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        <TopBar health={health} onOpenSidebar={() => setSidebarOpen(true)} />

        <main className="flex-1 px-4 lg:px-8 py-6 max-w-7xl w-full mx-auto space-y-6">
          <Outlet />
          <DisclaimerBanner className="mt-8" />
        </main>
      </div>
    </div>
  )
}
