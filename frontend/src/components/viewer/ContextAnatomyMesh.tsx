import React, { useMemo } from "react"
import * as THREE from "three"

interface ContextAnatomyMeshProps {
  id: string
  geometry: THREE.BufferGeometry
  visible: boolean
}

interface MaterialConfig {
  color: number
  opacity: number
  roughness: number
  metalness: number
  transparent: boolean
  depthWrite: boolean
  wireframe?: boolean
}

const CONTEXT_STYLES: Record<string, MaterialConfig> = {
  // Left main stem connects aorta bulb to LAD/LCX
  struct_left_main: {
    color: 0xe2e8f0,
    opacity: 0.95,
    roughness: 0.35,
    metalness: 0.2,
    transparent: false,
    depthWrite: true,
  },
  // Aortic bulb / root (source of coronary ostia)
  struct_aorta_bulb: {
    color: 0x94a3b8,
    opacity: 0.45,
    roughness: 0.4,
    metalness: 0.1,
    transparent: true,
    depthWrite: false,
  },
  // Ascending aorta
  struct_aorta_ascending: {
    color: 0x64748b,
    opacity: 0.40,
    roughness: 0.45,
    metalness: 0.1,
    transparent: true,
    depthWrite: false,
  },
  // Left ventricle free wall (translucent silhouette background)
  struct_lv_wall: {
    color: 0x334155,
    opacity: 0.18,
    roughness: 0.6,
    metalness: 0.05,
    transparent: true,
    depthWrite: false,
  },
  // Muscular interventricular septum
  struct_septum: {
    color: 0x475569,
    opacity: 0.18,
    roughness: 0.6,
    metalness: 0.05,
    transparent: true,
    depthWrite: false,
  },
  // Pulmonary trunk
  struct_pulmonary_trunk: {
    color: 0x64748b,
    opacity: 0.30,
    roughness: 0.5,
    metalness: 0.1,
    transparent: true,
    depthWrite: false,
  },
}

const DEFAULT_STYLE: MaterialConfig = {
  color: 0x64748b,
  opacity: 0.3,
  roughness: 0.5,
  metalness: 0.1,
  transparent: true,
  depthWrite: false,
}

export const ContextAnatomyMesh: React.FC<ContextAnatomyMeshProps> = ({
  id,
  geometry,
  visible,
}) => {
  const material = useMemo(() => {
    const style = CONTEXT_STYLES[id] || DEFAULT_STYLE
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(style.color),
      opacity: style.opacity,
      transparent: style.transparent,
      depthWrite: style.depthWrite,
      roughness: style.roughness,
      metalness: style.metalness,
      side: THREE.DoubleSide,
    })
  }, [id])

  if (!visible) return null

  return <mesh geometry={geometry} material={material} />
}
