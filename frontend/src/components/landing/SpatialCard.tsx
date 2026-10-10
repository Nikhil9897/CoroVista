import React, { useState, useRef } from "react"

interface SpatialCardProps {
  children: React.ReactNode
  className?: string
  glowColor?: string
  tilt?: boolean
  onClick?: () => void
}

export const SpatialCard: React.FC<SpatialCardProps> = ({
  children,
  className = "",
  glowColor = "rgba(129, 140, 248, 0.15)",
  tilt = true,
  onClick,
}) => {
  const cardRef = useRef<HTMLDivElement>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)
  const [tiltStyle, setTiltStyle] = useState("")

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current
    if (!card) return

    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    setMousePos({ x, y })

    if (tilt) {
      // Gentle spatial tilt
      const centerX = rect.width / 2
      const centerY = rect.height / 2
      const rotateX = ((y - centerY) / centerY) * -3.5
      const rotateY = ((x - centerX) / centerX) * 3.5
      setTiltStyle(
        `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-2px)`
      )
    }
  }

  const handleMouseEnter = () => {
    setIsHovered(true)
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
    setTiltStyle("perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)")
  }

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{
        transform: isHovered && tilt ? tiltStyle : "perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)",
        transition: isHovered ? "transform 0.1s ease-out" : "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
      }}
      className={`group relative overflow-hidden transition-shadow duration-300 ${className}`}
    >
      {/* ── Spatial AI Dynamic Spotlight Layer ── */}
      <div
        className="pointer-events-none absolute -inset-px rounded-[inherit] transition-opacity duration-300"
        style={{
          opacity: isHovered ? 1 : 0,
          background: `radial-gradient(400px circle at ${mousePos.x}px ${mousePos.y}px, ${glowColor}, transparent 80%)`,
        }}
        aria-hidden="true"
      />

      {/* ── Content ── */}
      <div className="relative z-10 h-full">{children}</div>
    </div>
  )
}
