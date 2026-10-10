import React from "react"

interface HeroBokehProps {
  pointerOffset: { x: number; y: number }
}

export const HeroBokeh: React.FC<HeroBokehProps> = ({ pointerOffset }) => {
  return (
    <div
      className="absolute inset-0 overflow-hidden pointer-events-none select-none z-0"
      aria-hidden="true"
    >
      {/* ── Ambient Radial Backlight behind the Sphere Wreath ── */}
      <div
        className="absolute w-[620px] h-[620px] rounded-full blur-[100px] pointer-events-none transition-transform duration-700 ease-out"
        style={{
          top: "45%",
          left: "68%",
          transform: `translate(-50%, -50%) translate(${pointerOffset.x * 20}px, ${pointerOffset.y * 20}px)`,
          background: "radial-gradient(circle, rgba(27, 74, 71, 0.55) 0%, rgba(19, 59, 58, 0.3) 50%, rgba(1, 23, 25, 0) 75%)",
        }}
      />

      {/* ── Ambient Secondary Glow near Center ── */}
      <div
        className="absolute w-[440px] h-[440px] rounded-full blur-[90px] pointer-events-none transition-transform duration-700 ease-out"
        style={{
          top: "30%",
          left: "62%",
          transform: `translate(-50%, -50%) translate(${pointerOffset.x * 12}px, ${pointerOffset.y * 12}px)`,
          background: "radial-gradient(circle, rgba(140, 230, 199, 0.16) 0%, rgba(1, 23, 25, 0) 70%)",
        }}
      />

      {/* ── Bokeh Disc 1 (Top Center-Left) ── */}
      <div
        className="absolute w-44 h-44 rounded-full pointer-events-none transition-transform duration-500 ease-out"
        style={{
          top: "18%",
          left: "34%",
          background: "radial-gradient(circle, rgba(84, 122, 113, 0.32) 0%, rgba(84, 122, 113, 0.1) 60%, transparent 100%)",
          filter: "blur(22px)",
          animation: "heroBokehDrift1 24s ease-in-out infinite",
          transform: `translate(${pointerOffset.x * -18}px, ${pointerOffset.y * -18}px)`,
        }}
      />

      {/* ── Bokeh Disc 2 (Bottom Center - Large Distinct Bokeh from Reference) ── */}
      <div
        className="absolute w-64 h-64 rounded-full pointer-events-none transition-transform duration-500 ease-out"
        style={{
          bottom: "-4%",
          left: "38%",
          background: "radial-gradient(circle, rgba(75, 94, 85, 0.42) 0%, rgba(75, 94, 85, 0.15) 60%, transparent 100%)",
          filter: "blur(26px)",
          animation: "heroBokehDrift2 28s ease-in-out infinite",
          transform: `translate(${pointerOffset.x * 15}px, ${pointerOffset.y * 15}px)`,
        }}
      />

      {/* ── Bokeh Disc 3 (Bottom Left Edge) ── */}
      <div
        className="absolute w-72 h-72 rounded-full pointer-events-none transition-transform duration-500 ease-out"
        style={{
          bottom: "-8%",
          left: "-6%",
          background: "radial-gradient(circle, rgba(94, 125, 113, 0.35) 0%, rgba(94, 125, 113, 0.1) 65%, transparent 100%)",
          filter: "blur(32px)",
          animation: "heroBokehDrift3 32s ease-in-out infinite",
          transform: `translate(${pointerOffset.x * -22}px, ${pointerOffset.y * -22}px)`,
        }}
      />

      {/* ── Bokeh Disc 4 (Far Right Mid) ── */}
      <div
        className="absolute w-36 h-36 rounded-full pointer-events-none transition-transform duration-500 ease-out"
        style={{
          top: "31%",
          right: "6%",
          background: "radial-gradient(circle, rgba(84, 122, 113, 0.28) 0%, rgba(84, 122, 113, 0.08) 60%, transparent 100%)",
          filter: "blur(20px)",
          animation: "heroBokehDrift1 20s ease-in-out infinite reverse",
          transform: `translate(${pointerOffset.x * 12}px, ${pointerOffset.y * 12}px)`,
        }}
      />

      {/* ── Bokeh Disc 5 (Top Left Subtle) ── */}
      <div
        className="absolute w-48 h-48 rounded-full pointer-events-none transition-transform duration-500 ease-out"
        style={{
          top: "-5%",
          left: "2%",
          background: "radial-gradient(circle, rgba(144, 172, 167, 0.18) 0%, transparent 70%)",
          filter: "blur(30px)",
          animation: "heroBokehDrift2 26s ease-in-out infinite",
          transform: `translate(${pointerOffset.x * 8}px, ${pointerOffset.y * 8}px)`,
        }}
      />
    </div>
  )
}
