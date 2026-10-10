import React from "react"
import { NavLink } from "react-router-dom"
import {
  LayoutDashboard,
  Sliders,
  Info,
  HeartPulse,
  X,
} from "lucide-react"

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
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

      {/* Sidebar — slim icon rail on desktop, expanded on mobile */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col justify-between transition-all duration-300 ease-in-out
          lg:w-[56px] lg:translate-x-0 lg:hover:w-[200px] lg:group
          ${isOpen ? "w-[220px] translate-x-0" : "w-[220px] -translate-x-full lg:translate-x-0"}
          surface-1 border-r border-border/40
        `}
        aria-label="Sidebar Navigation"
      >
        {/* Brand Header */}
        <div className="p-3 lg:px-2 lg:py-4 border-b border-border/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-lg bg-primary/15 flex items-center justify-center text-primary shrink-0">
                <HeartPulse className="w-[18px] h-[18px]" />
              </div>
              <div className="overflow-hidden lg:opacity-0 lg:group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                <h1 className="font-semibold text-[13px] tracking-tight text-foreground leading-tight">
                  CoroVista
                </h1>
                <p className="text-[10px] text-muted-foreground leading-tight">
                  v1.0
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-1 rounded-md text-muted-foreground hover:text-foreground lg:hidden cursor-pointer"
              aria-label="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-2 py-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-2.5 py-2 rounded-lg text-xs font-medium transition-all duration-200 group/item overflow-hidden ${
                    isActive
                      ? "bg-primary/12 text-primary"
                      : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
                  }`
                }
              >
                <Icon className="w-[18px] h-[18px] shrink-0" />
                <span className="whitespace-nowrap lg:opacity-0 lg:group-hover:opacity-100 transition-opacity duration-200">
                  {item.label}
                </span>
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-2 border-t border-border/30 flex items-center justify-center lg:group-hover:justify-between overflow-hidden">
          <span className="text-[10px] text-muted-foreground/50 font-mono hidden lg:group-hover:inline whitespace-nowrap">
            Decision Support
          </span>
          <span className="text-[10px] text-muted-foreground/40 font-mono">
            v1.0
          </span>
        </div>
      </aside>
    </>
  )
}
