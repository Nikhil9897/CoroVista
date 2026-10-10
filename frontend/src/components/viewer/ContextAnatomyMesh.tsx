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
  // Left main stem connects aorta bulb to LAD/LCX
  struct_left_main: {
    color: 0xf8fafc,
    opacity: 0.96,
    roughness: 0.22,
    metalness: 0.15,
    transparent: false,
    depthWrite: true,
    emissive: 0x1e293b,
    emissiveIntensity: 0.15,
  },
  // Aortic bulb / root (source of coronary ostia) — soft translucent porcelain
  struct_aorta_bulb: {
    color: 0xdbeafe,
    opacity: 0.62,
    roughness: 0.26,
    metalness: 0.10,
    transparent: true,
    depthWrite: false,
    emissive: 0x1e3a5f,
    emissiveIntensity: 0.20,
  },
  // Ascending aorta — continuous great vessel outflow
  struct_aorta_ascending: {
    color: 0xbfdbfe,
    opacity: 0.58,
    roughness: 0.28,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
    emissive: 0x172554,
    emissiveIntensity: 0.18,
  },
  // Left ventricle free wall — living myocardial silhouette
  struct_lv_wall: {
    color: 0x60a5fa,
    opacity: 0.42,
    roughness: 0.32,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
    emissive: 0x172554,
    emissiveIntensity: 0.25,
  },
  // Muscular interventricular septum — central muscular cardiac pillar
  struct_septum: {
    color: 0x38bdf8,
    opacity: 0.38,
    roughness: 0.34,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
    emissive: 0x0c4a6e,
    emissiveIntensity: 0.22,
  },
  // Pulmonary trunk — anterior outflow tract
  struct_pulmonary_trunk: {
    color: 0x93c5fd,
    opacity: 0.48,
    roughness: 0.30,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
    emissive: 0x1e3a8a,
    emissiveIntensity: 0.18,
  },
}

const DEFAULT_STYLE: MaterialConfig = {
  color: 0x93c5fd,
  opacity: 0.40,
  roughness: 0.35,
  metalness: 0.1,
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
