import React from "react"
import { NavLink, useNavigate } from "react-router-dom"
import {
  HeartPulse,
  SlidersHorizontal,
  FileText,
  Power,
  ChevronLeft,
} from "lucide-react"

export interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  isExpanded?: boolean
  onToggleExpanded?: () => void
  onExpand?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  isExpanded = false,
  onToggleExpanded,
  onExpand,
}) => {
  const navigate = useNavigate()

  const navItems = [
    {
      to: "/dashboard",
      label: "Clinical Dashboard",
      subtitle: "3D Coronary Digital Twin",
      icon: HeartPulse,
    },
    {
      to: "/simulator",
      label: "Patient Simulator",
      subtitle: "54 Clinical Parameters",
      icon: SlidersHorizontal,
    },
    {
      to: "/about",
      label: "About & Methodology",
      subtitle: "Clinical Validation & SHAP",
      icon: FileText,
    },
  ]

  const handleItemClick = () => {
    // Reveal text names by expanding if collapsed, or close on mobile
    if (!isExpanded && onExpand) {
      onExpand()
    }
    onClose()
  }

  const handlePowerClick = () => {
    navigate("/")
    onClose()
  }

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Floating Boxed Sidebar: Centered vertically on left margin, merged with dashboard interface */}
      <aside
        className={`fixed z-40 transition-all duration-300 ease-in-out select-none
          /* Desktop: Floating centered dock, zero blank column space */
          lg:left-3 lg:top-1/2 lg:-translate-y-1/2
          /* Mobile drawer mode */
          ${isOpen ? "left-4 top-1/2 -translate-y-1/2" : "-left-full lg:left-3 top-1/2 -translate-y-1/2"}
        `}
        aria-label="Sidebar Navigation"
      >
        <div
          className={`transition-all duration-300 ease-in-out border border-white/[0.12] backdrop-blur-2xl shadow-2xl shadow-black/70 ${
            isExpanded || isOpen
              ? "w-[245px] p-3 rounded-3xl bg-[#071618]/95 flex flex-col gap-2"
              : "w-[58px] p-2 rounded-full bg-[#071618]/85 flex flex-col items-center gap-2.5"
          }`}
          role="navigation"
          aria-label="Primary Navigation Options"
        >
          {/* Expanded Header with Collapse Toggle */}
          {(isExpanded || isOpen) && (
            <div className="flex items-center justify-between pb-2 mb-1 border-b border-white/[0.08] px-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#7C9692]">
                Navigation
              </span>
              <button
                type="button"
                onClick={onToggleExpanded || onClose}
                className="w-6 h-6 rounded-lg text-[#7C9692] hover:text-[#E8F1EE] hover:bg-white/10 flex items-center justify-center transition-colors cursor-pointer"
                title="Collapse sidebar"
                aria-label="Collapse sidebar"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Navigation Items */}
          <div className="flex flex-col items-center w-full gap-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <div key={item.to} className="relative group/navitem w-full flex items-center justify-center">
                  <NavLink
                    to={item.to}
                    onClick={handleItemClick}
                    className={({ isActive }) =>
                      `relative transition-all duration-200 cursor-pointer ${
                        isExpanded || isOpen
                          ? `flex items-center gap-3 w-full p-2 rounded-2xl text-left ${
                              isActive
                                ? "bg-white/[0.14] text-[#E8F1EE] border border-white/25 shadow-md shadow-black/30"
                                : "text-[#7C9692] hover:text-[#E8F1EE] hover:bg-white/[0.06] border border-transparent"
                            }`
                          : `flex items-center justify-center w-11 h-11 rounded-full ${
                              isActive
                                ? "bg-white/[0.20] text-[#E8F1EE] border border-white/35 shadow-lg shadow-black/40 ring-1 ring-white/15 scale-105"
                                : "bg-white/[0.04] text-[#7C9692] hover:text-[#E8F1EE] hover:bg-white/[0.10] border border-white/[0.06] hover:border-white/15"
                            }`
                      }`
                    }
                    aria-label={item.label}
                  >
                    {({ isActive }) => (
                      <>
                        {/* Circular Icon Container */}
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-transform ${
                            isExpanded || isOpen
                              ? isActive
                                ? "bg-white/[0.15] text-[#E8F1EE]"
                                : "bg-white/[0.04] text-[#7C9692]"
                              : ""
                          }`}
                        >
                          <Icon className="w-5 h-5 shrink-0" />
                        </div>

                        {/* Text Label: Expands inline when menu is open, flies out as tooltip when collapsed on hover */}
                        <div
                          className={`flex flex-col min-w-0 transition-all duration-300 ${
                            isExpanded || isOpen
                              ? "opacity-100 max-w-[170px] ml-0.5"
                              : "max-w-0 opacity-0 pointer-events-none group-hover/navitem:opacity-100 group-hover/navitem:max-w-[220px] group-hover/navitem:pointer-events-auto absolute left-[64px] z-50 px-3 py-1.5 rounded-xl bg-[#071618]/95 border border-white/20 shadow-2xl backdrop-blur-xl whitespace-nowrap"
                          }`}
                        >
                          <span className="text-xs font-semibold tracking-tight text-[#E8F1EE] truncate block leading-tight">
                            {item.label}
                          </span>
                          <span className="text-[10px] text-[#7C9692] truncate block leading-tight mt-0.5">
                            {item.subtitle}
                          </span>
                        </div>
                      </>
                    )}
                  </NavLink>
                </div>
              )
            })}
          </div>

          {/* Thin Divider Line */}
          <div className="w-full px-2 my-0.5" aria-hidden="true">
            <div className="w-full h-px bg-white/[0.10]" />
          </div>

          {/* Bottom Action: Circular Power / Home Button */}
          <div className="w-full flex items-center justify-center">
            <button
              type="button"
              onClick={handlePowerClick}
              className={`group/power relative transition-all duration-200 cursor-pointer ${
                isExpanded || isOpen
                  ? "flex items-center gap-3 w-full p-2 rounded-2xl border border-white/[0.08] bg-white/[0.02] hover:bg-rose-500/15 hover:border-rose-500/30 text-[#7C9692] hover:text-rose-400"
                  : "w-11 h-11 rounded-full border border-white/[0.10] bg-white/[0.04] hover:bg-rose-500/15 hover:border-rose-500/30 text-[#7C9692] hover:text-rose-400 flex items-center justify-center shadow-sm"
              }`}
              title="Return to Scientific Portal / System Standby"
              aria-label="Return to Scientific Portal / System Standby"
            >
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0">
                <Power className="w-4 h-4 transition-transform group-hover/power:scale-110" />
              </div>

              <div
                className={`flex flex-col min-w-0 transition-all duration-300 text-left overflow-hidden ${
                  isExpanded || isOpen
                    ? "opacity-100 max-w-[170px]"
                    : "opacity-0 max-w-0 pointer-events-none hidden"
                }`}
              >
                <span className="text-xs font-medium text-[#E8F1EE] group-hover/power:text-rose-300 leading-tight">
                  System Standby
                </span>
                <span className="text-[10px] text-[#7C9692]/70 leading-tight">
                  v1.0 &bull; Scientific Portal
                </span>
              </div>
            </button>
          </div>
        </div>
      </aside>
    </>
  )
}
