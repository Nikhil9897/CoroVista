import React from "react"
import { NavLink } from "react-router-dom"
import {
  LayoutDashboard,
  Sliders,
  Info,
  Sparkles,
  X,
} from "lucide-react"

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    {
      to: "/",
      label: "Platform Overview",
      icon: Sparkles,
    },
    {
      to: "/dashboard",
      label: "Clinical Dashboard",
      icon: LayoutDashboard,
    },
    {
      to: "/simulator",
      label: "Patient Simulator",
      icon: Sliders,
    },
    {
      to: "/about",
      label: "About & Methodology",
      icon: Info,
    },
  ]

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar — quiet clinical slim rail on desktop */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col justify-between transition-all duration-300 ease-in-out
          lg:w-[56px] lg:translate-x-0
          ${isOpen ? "w-[220px] translate-x-0" : "w-[220px] -translate-x-full lg:translate-x-0"}
          bg-[#011012] border-r border-white/10
        `}
        aria-label="Sidebar Navigation"
      >
        {/* Brand Header */}
        <div className="p-3 lg:px-2.5 lg:py-3.5 border-b border-white/10 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2.5 overflow-hidden group/brand" title="CoroVista Home">
            <div className="w-8 h-8 rounded-lg bg-[#F26F69]/10 border border-[#F26F69]/20 flex items-center justify-center shrink-0 overflow-hidden transition-transform group-hover/brand:scale-105">
              <img
                src="/corovista-heart.png"
                alt="CoroVista"
                className="w-5 h-5 object-contain"
              />
            </div>
            <div className="lg:hidden whitespace-nowrap">
              <h1 className="font-semibold text-xs tracking-tight text-[#E8F1EE] leading-tight">
                CoroVista
              </h1>
              <p className="text-[10px] text-[#7C9692] leading-tight">
                Clinical CAD
              </p>
            </div>
          </NavLink>

          <button
            onClick={onClose}
            className="p-1 rounded-md text-[#7C9692] hover:text-[#E8F1EE] lg:hidden cursor-pointer"
            aria-label="Close navigation"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-1.5 py-4 space-y-1.5 overflow-y-auto" role="navigation">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <div key={item.to} className="relative group/navitem flex items-center">
                <NavLink
                  to={item.to}
                  onClick={onClose}
                  className={({ isActive }) =>
                    `relative flex items-center gap-3 w-full px-2.5 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 ${
                      isActive
                        ? "bg-[#F26F69]/12 text-[#F26F69]"
                        : "text-[#8fa6a8] hover:text-[#E8F1EE] hover:bg-white/10"
                    }`
                  }
                  aria-label={item.label}
                >
                  {({ isActive }) => (
                    <>
                      {/* Active Coral Indicator Bar */}
                      {isActive && (
                        <span
                          className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r bg-[#F26F69]"
                          aria-hidden="true"
                        />
                      )}
                      <Icon className="w-[18px] h-[18px] shrink-0" />
                      <span className="whitespace-nowrap max-lg:inline lg:hidden lg:group-hover/navitem:block lg:absolute lg:left-[54px] lg:px-2.5 lg:py-1 lg:rounded-lg lg:text-[11px] lg:font-medium lg:bg-[#182326] lg:text-[#E8F1EE] lg:border lg:border-white/15 lg:shadow-xl lg:z-50 pointer-events-none">
                        {item.label}
                      </span>
                    </>
                  )}
                </NavLink>
              </div>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-2.5 border-t border-white/10 flex items-center justify-center">
          <span className="text-[10px] text-[#8fa6a8]/50 font-mono" title="CoroVista Platform Version 1.0">
            v1.0
          </span>
        </div>
      </aside>
    </>
  )
}
