import React, { useMemo, useState, useRef } from "react"
import { useFrame } from "@react-three/fiber"
import * as THREE from "three"
import type { CoronaryVesselId, HoveredVesselInfo } from "./ViewerTypes"
import { getVesselColor, VESSEL_NAMES } from "@/lib/vesselColors"

interface CoronaryVesselMeshProps {
  id: CoronaryVesselId
  geometry: THREE.BufferGeometry
  probability: number
  threshold: number
  isStenotic: boolean
  isSelected: boolean
  isAnyFocused?: boolean
  visible: boolean
  onClick: (id: CoronaryVesselId) => void
  onHover: (info: HoveredVesselInfo | null) => void
}

export const CoronaryVesselMesh: React.FC<CoronaryVesselMeshProps> = ({
  id,
  geometry,
  probability,
  threshold,
  isStenotic,
  isSelected,
  isAnyFocused = false,
  visible,
  onClick,
  onHover,
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const meshRef = useRef<THREE.Mesh>(null)
  const meta = VESSEL_NAMES[id]

  // Compute continuous color from actual probability
  const { hex } = useMemo(() => getVesselColor(probability), [probability])

  const isDimmed = isAnyFocused && !isSelected

  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(hex),
      roughness: 0.22,
      metalness: 0.20,
      emissive: new THREE.Color(hex),
      emissiveIntensity: isSelected ? 0.70 : isHovered ? 0.50 : isStenotic ? 0.35 : 0.16,
      transparent: isDimmed,
      opacity: isDimmed ? 0.28 : 1.0,
      depthWrite: !isDimmed,
      side: THREE.DoubleSide,
    })
  }, [hex, isSelected, isHovered, isStenotic, isDimmed])

  // Soft pulsing glow/halo around vessels above threshold, scaling with probability
  useFrame(({ clock }) => {
    if (!meshRef.current || !isStenotic || isDimmed) return

    // Respect prefers-reduced-motion
    if (typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return
    }

    const mat = meshRef.current.material as THREE.MeshStandardMaterial
    if (!mat) return

    // Pulse frequency: 1.8 to 4.2 rad/s scaling with probability
    const pulseSpeed = 1.8 + Math.min(1, probability) * 2.4
    // Pulse amplitude: 0.12 to 0.28 scaling with probability
    const pulseAmp = 0.12 + Math.min(1, probability) * 0.16
    const baseEmissive = isSelected ? 0.75 : isHovered ? 0.55 : 0.32

    mat.emissiveIntensity = baseEmissive + Math.sin(clock.getElapsedTime() * pulseSpeed) * pulseAmp
  })

  if (!visible) return null

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      material={material}
      onClick={(e) => {
        e.stopPropagation()
        onClick(id)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setIsHovered(true)
        document.body.style.cursor = "pointer"
        onHover({
          id,
          short: meta.short,
          full: meta.full,
          probability,
          threshold,
          isStenotic,
          territory: meta.territory,
        })
      }}
      onPointerOut={(e) => {
        e.stopPropagation()
        setIsHovered(false)
        document.body.style.cursor = "auto"
        onHover(null)
      }}
    />
  )
}
