import React from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { LandingPage } from "@/pages/LandingPage"
import { Dashboard } from "@/pages/Dashboard"
import { Simulator } from "@/pages/Simulator"
import { About } from "@/pages/About"
import { usePatientAnalysis } from "@/hooks/usePatientAnalysis"

export const App: React.FC = () => {
  const { health } = usePatientAnalysis()

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Scientific Landing Page */}
        <Route path="/" element={<LandingPage health={health} />} />

        {/* Clinical Application Workstation Shell */}
        <Route element={<AppShell health={health} />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
