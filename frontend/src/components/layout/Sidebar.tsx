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
      badge: "Active",
    },
    {
      to: "/simulator",
      label: "Patient Simulator",
      icon: Sliders,
      badge: "Stage 5C",
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
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-card border-r border-border flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Sidebar Navigation"
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-primary-foreground shadow-md shadow-primary/20">
                <HeartPulse className="w-5 h-5" />
              </div>
              <div>
                <h1 className="font-bold text-base tracking-tight text-foreground flex items-center gap-1.5">
                  CoroVista
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-primary/20 text-primary border border-primary/30">
                    v1.0
                  </span>
                </h1>
                <p className="text-[11px] text-muted-foreground truncate">
                  Cardiovascular Risk AI
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
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-primary/10 text-primary border border-primary/20 shadow-sm"
                      : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-secondary text-muted-foreground border border-border">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Footer Info */}
        <div className="p-4 border-t border-border space-y-3">
          <div className="p-3 rounded-lg bg-secondary/50 border border-border/60 text-[11px] text-muted-foreground space-y-1">
            <span className="font-medium text-foreground block">Hackathon 2026</span>
            <p className="text-muted-foreground/80 leading-snug">
              Track A: Multi-Target Cardiovascular Risk & Anatomical Prediction.
            </p>
          </div>

          <div className="flex items-center justify-between text-[11px] text-muted-foreground/70 px-1">
            <span>Locked Models: 4</span>
            <span className="font-mono">API v1.0.0</span>
          </div>
        </div>
      </aside>
    </>
  )
}
