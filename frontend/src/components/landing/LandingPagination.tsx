import React, { useEffect, useState } from "react"
import { ChevronDown } from "lucide-react"

interface SectionItem {
  id: string
  label: string
  color: string
}

const SECTIONS: SectionItem[] = [
  { id: "hero", label: "01 // Visual Overview", color: "#8ce6c7" },
  { id: "capabilities", label: "02 // Multimodal AI", color: "#818cf8" },
  { id: "anatomy", label: "03 // 3D Anatomy", color: "#06b6d4" },
  { id: "workflow", label: "04 // Decision Pipeline", color: "#10b981" },
  { id: "cta", label: "05 // Clinical Workspace", color: "#ff7e81" },
]

export const LandingPagination: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>("hero")
  const [hoveredDot, setHoveredDot] = useState<string | null>(null)

  // Track active section via IntersectionObserver on scroll
  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id)
          }
        })
      },
      {
        threshold: 0.25,
        rootMargin: "-15% 0px -35% 0px",
      }
    )

    SECTIONS.forEach((sec) => {
      const el = document.getElementById(sec.id)
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id)
    if (el) {
      el.scrollIntoView({ behavior: "smooth" })
      setActiveSection(id)
    }
  }

  const handleNextSection = () => {
    const currentIndex = SECTIONS.findIndex((s) => s.id === activeSection)
    const nextIndex = (currentIndex + 1) % SECTIONS.length
    scrollToSection(SECTIONS[nextIndex].id)
  }

  const activeItem = SECTIONS.find((s) => s.id === activeSection) || SECTIONS[0]

  return (
    <aside
      className="hidden md:flex fixed right-6 sm:right-7 top-1/2 -translate-y-1/2 z-40 flex-col items-center gap-3.5"
      aria-label="Section Navigation"
    >
      {/* ── Circled Down Arrow Button (advances to next section/dot on click) ── */}
      <button
        type="button"
        onClick={handleNextSection}
        className="w-7 h-7 rounded-full border border-white/20 bg-black/40 backdrop-blur-md flex items-center justify-center text-white/70 hover:text-white transition-all cursor-pointer hover:scale-110 active:scale-95 shadow-lg shadow-black/40 group relative"
        aria-label="Scroll to next section"
        style={{
          borderColor: `${activeItem.color}55`,
        }}
      >
        <ChevronDown
          className="w-3.5 h-3.5 transition-transform group-hover:translate-y-0.5"
          style={{ color: activeItem.color }}
        />
        {/* Tooltip on arrow hover */}
        <span className="pointer-events-none absolute right-9 px-2.5 py-1 rounded-md text-[10px] font-mono tracking-wider whitespace-nowrap bg-black/80 text-white/90 border border-white/10 backdrop-blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          Next Section &darr;
        </span>
      </button>

      {/* ── Vertical Pagination Dots ── */}
      <nav
        className="flex flex-col items-center gap-2.5 p-1 rounded-full bg-black/20 backdrop-blur-sm border border-white/5"
        aria-label="Page Sections"
      >
        {SECTIONS.map((sec) => {
          const isActive = activeSection === sec.id
          const isHovered = hoveredDot === sec.id

          return (
            <div key={sec.id} className="relative flex items-center justify-center">
              <button
                type="button"
                onClick={() => scrollToSection(sec.id)}
                onMouseEnter={() => setHoveredDot(sec.id)}
                onMouseLeave={() => setHoveredDot(null)}
                className="w-5 h-5 flex items-center justify-center rounded-full cursor-pointer transition-transform hover:scale-125 focus:outline-none"
                aria-label={`Jump to ${sec.label}`}
                aria-current={isActive ? "true" : undefined}
              >
                <span
                  className="rounded-full transition-all duration-300"
                  style={{
                    width: isActive ? "8px" : "5px",
                    height: isActive ? "8px" : "5px",
                    backgroundColor: isActive ? sec.color : "rgba(255, 255, 255, 0.25)",
                    boxShadow: isActive
                      ? `0 0 10px ${sec.color}, 0 0 18px ${sec.color}88`
                      : isHovered
                      ? `0 0 6px rgba(255, 255, 255, 0.5)`
                      : "none",
                  }}
                />
              </button>

              {/* Tooltip label revealing section info on hover */}
              {isHovered && (
                <div
                  className="pointer-events-none absolute right-8 px-2.5 py-1 rounded-md text-[10px] font-mono tracking-wide whitespace-nowrap bg-black/85 text-white border backdrop-blur-md z-50 animate-in fade-in duration-150"
                  style={{
                    borderColor: `${sec.color}40`,
                    color: sec.color,
                  }}
                >
                  {sec.label}
                </div>
              )}
            </div>
          )
        })}
      </nav>
    </aside>
  )
}
