import React, { useEffect, useRef, useState } from "react"

interface ScrollRevealProps {
  children: React.ReactNode
  className?: string
  delay?: number // ms stagger delay
  direction?: "up" | "down" | "none"
}

export const ScrollReveal: React.FC<ScrollRevealProps> = ({
  children,
  className = "",
  delay = 0,
  direction = "up",
}) => {
  const [isVisible, setIsVisible] = useState(() => typeof IntersectionObserver === "undefined")
  const domRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = domRef.current
    if (!el) return

    // Fallback for environments where IntersectionObserver is unsupported
    if (typeof IntersectionObserver === "undefined") {
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
            observer.unobserve(entry.target)
          }
        })
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -40px 0px",
      }
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  const transformStyle = isVisible
    ? "perspective(1000px) translateY(0px) scale(1) rotateX(0deg)"
    : direction === "up"
    ? "perspective(1000px) translateY(36px) scale(0.97) rotateX(3.5deg)"
    : direction === "down"
    ? "perspective(1000px) translateY(-36px) scale(0.97) rotateX(-3.5deg)"
    : "scale(0.97)"

  return (
    <div
      ref={domRef}
      className={`transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform ${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: transformStyle,
        transitionDelay: `${delay}ms`,
      }}
    >
      {children}
    </div>
  )
}
