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
  emissive?: number
  emissiveIntensity?: number
}

const CONTEXT_STYLES: Record<string, MaterialConfig> = {
  // Left main stem connects aorta bulb to LAD/LCX — crisp, prominent anatomical arterial conduit
  struct_left_main: {
    color: 0xf8fafc,
    opacity: 0.96,
    roughness: 0.22,
    metalness: 0.18,
    transparent: false,
    depthWrite: true,
    emissive: 0x334155,
    emissiveIntensity: 0.25,
  },
  // Aortic bulb / root (source of coronary ostia) — soft translucent porcelain anatomy
  struct_aorta_bulb: {
    color: 0xdbeafe,
    opacity: 0.52,
    roughness: 0.28,
    metalness: 0.12,
    transparent: true,
    depthWrite: false,
    emissive: 0x1e3a5f,
    emissiveIntensity: 0.20,
  },
  // Ascending aorta — great vessel outflow contour
  struct_aorta_ascending: {
    color: 0xbfdbfe,
    opacity: 0.46,
    roughness: 0.30,
    metalness: 0.12,
    transparent: true,
    depthWrite: false,
    emissive: 0x172554,
    emissiveIntensity: 0.18,
  },
  // Left ventricle free wall — living translucent myocardial silhouette
  struct_lv_wall: {
    color: 0x38bdf8,
    opacity: 0.30,
    roughness: 0.36,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
    emissive: 0x0c4a6e,
    emissiveIntensity: 0.22,
  },
  // Muscular interventricular septum — central cardiac pillar
  struct_septum: {
    color: 0x2563eb,
    opacity: 0.28,
    roughness: 0.40,
    metalness: 0.06,
    transparent: true,
    depthWrite: false,
    emissive: 0x0f172a,
    emissiveIntensity: 0.18,
  },
  // Pulmonary trunk — anterior outflow tract
  struct_pulmonary_trunk: {
    color: 0x93c5fd,
    opacity: 0.42,
    roughness: 0.32,
    metalness: 0.10,
    transparent: true,
    depthWrite: false,
    emissive: 0x1e3a8a,
    emissiveIntensity: 0.18,
  },
}

const DEFAULT_STYLE: MaterialConfig = {
  color: 0x93c5fd,
  opacity: 0.35,
  roughness: 0.36,
  metalness: 0.08,
  transparent: true,
  depthWrite: false,
  emissive: 0x0f172a,
  emissiveIntensity: 0.15,
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
      emissive: style.emissive ? new THREE.Color(style.emissive) : undefined,
      emissiveIntensity: style.emissiveIntensity ?? 0,
      side: THREE.DoubleSide,
    })
  }, [id])

  if (!visible) return null

  return <mesh geometry={geometry} material={material} />
}
