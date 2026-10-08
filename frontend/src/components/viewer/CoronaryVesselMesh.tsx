import React, { useMemo, useState } from "react"
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
  visible,
  onClick,
  onHover,
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const meta = VESSEL_NAMES[id]

  // Compute continuous color from actual probability
  const { hex } = useMemo(() => getVesselColor(probability), [probability])

  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(hex),
      roughness: 0.32,
      metalness: 0.18,
      emissive: isSelected
        ? new THREE.Color(hex)
        : isHovered
        ? new THREE.Color(hex)
        : new THREE.Color(0x000000),
      emissiveIntensity: isSelected ? 0.55 : isHovered ? 0.35 : 0.0,
      side: THREE.DoubleSide,
    })
  }, [hex, isSelected, isHovered])

  if (!visible) return null

  return (
    <mesh
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
