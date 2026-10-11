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
  side?: THREE.Side
}

const CONTEXT_STYLES: Record<string, MaterialConfig> = {
  // Unified ventricular myocardium — cohesive rounded muscular cone in rich anatomical burgundy
  struct_myocardium: {
    color: 0x88202d,
    opacity: 1.0,
    roughness: 0.58,
    metalness: 0.02,
    transparent: false,
    depthWrite: true,
    emissive: 0x22070a,
    emissiveIntensity: 0.12,
    side: THREE.FrontSide,
  },
  // Auricles / Atrial appendages — capping the cardiac base smoothly
  struct_auricles: {
    color: 0x7c1c28,
    opacity: 1.0,
    roughness: 0.56,
    metalness: 0.02,
    transparent: false,
    depthWrite: true,
    emissive: 0x200609,
    emissiveIntensity: 0.10,
    side: THREE.FrontSide,
  },
  // Left main stem connects aorta bulb to LAD/LCX bifurcation — crisp arterial conduit take-off
  struct_left_main: {
    color: 0xfca5a5,
    opacity: 1.0,
    roughness: 0.32,
    metalness: 0.08,
    transparent: false,
    depthWrite: true,
    emissive: 0x450a0a,
    emissiveIntensity: 0.18,
    side: THREE.DoubleSide,
  },
  // Aortic bulb / root (origin of coronary ostia) — warm anatomical arterial ivory-rose
  struct_aorta_bulb: {
    color: 0xd98b83,
    opacity: 1.0,
    roughness: 0.44,
    metalness: 0.04,
    transparent: false,
    depthWrite: true,
    emissive: 0x331412,
    emissiveIntensity: 0.12,
    side: THREE.DoubleSide,
  },
  // Ascending aorta — superior arterial outflow tract
  struct_aorta_ascending: {
    color: 0xe29b93,
    opacity: 1.0,
    roughness: 0.44,
    metalness: 0.04,
    transparent: false,
    depthWrite: true,
    emissive: 0x331412,
    emissiveIntensity: 0.12,
    side: THREE.DoubleSide,
  },
  // Pulmonary trunk — anterior outflow tract, anatomical slate cyan
  struct_pulmonary_trunk: {
    color: 0x547d96,
    opacity: 1.0,
    roughness: 0.44,
    metalness: 0.04,
    transparent: false,
    depthWrite: true,
    emissive: 0x102533,
    emissiveIntensity: 0.12,
    side: THREE.DoubleSide,
  },
  // Muscular interventricular septum — internal ventricular divider
  struct_septum: {
    color: 0x6e1925,
    opacity: 0.90,
    roughness: 0.60,
    metalness: 0.02,
    transparent: true,
    depthWrite: true,
    emissive: 0x1a0407,
    emissiveIntensity: 0.08,
    side: THREE.FrontSide,
  },
  // Fallbacks for individual chamber walls
  struct_lv_wall: {
    color: 0x88202d,
    opacity: 1.0,
    roughness: 0.58,
    metalness: 0.02,
    transparent: false,
    depthWrite: true,
    emissive: 0x22070a,
    emissiveIntensity: 0.12,
    side: THREE.FrontSide,
  },
  struct_rv_wall: {
    color: 0x88202d,
    opacity: 1.0,
    roughness: 0.58,
    metalness: 0.02,
    transparent: false,
    depthWrite: true,
    emissive: 0x22070a,
    emissiveIntensity: 0.12,
    side: THREE.FrontSide,
  },
  struct_ra_wall: {
    color: 0x7c1c28,
    opacity: 1.0,
    roughness: 0.56,
    metalness: 0.02,
    transparent: false,
    depthWrite: true,
    emissive: 0x200609,
    emissiveIntensity: 0.10,
    side: THREE.FrontSide,
  },
  struct_la_wall: {
    color: 0x7c1c28,
    opacity: 1.0,
    roughness: 0.56,
    metalness: 0.02,
    transparent: false,
    depthWrite: true,
    emissive: 0x200609,
    emissiveIntensity: 0.10,
    side: THREE.FrontSide,
  },
}

const DEFAULT_STYLE: MaterialConfig = {
  color: 0x88202d,
  opacity: 1.0,
  roughness: 0.58,
  metalness: 0.02,
  transparent: false,
  depthWrite: true,
  emissive: 0x22070a,
  emissiveIntensity: 0.12,
  side: THREE.FrontSide,
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
      side: style.side ?? THREE.FrontSide,
    })
  }, [id])

  if (!visible) return null

  return <mesh geometry={geometry} material={material} />
}
