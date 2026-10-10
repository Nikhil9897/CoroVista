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
  // Left main stem connects aorta bulb to LAD/LCX — smooth slate-teal conduit
  struct_left_main: {
    color: 0x64748b,
    opacity: 0.85,
    roughness: 0.32,
    metalness: 0.12,
    transparent: true,
    depthWrite: false,
  },
  // Aortic bulb / root — clean translucent pearlescent anatomy
  struct_aorta_bulb: {
    color: 0xb0bcc9,
    opacity: 0.45,
    roughness: 0.45,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
  },
  // Ascending aorta — great vessel contour
  struct_aorta_ascending: {
    color: 0xb0bcc9,
    opacity: 0.40,
    roughness: 0.45,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
  },
  // Left ventricle free wall — clear myocardial chamber silhouette
  struct_lv_wall: {
    color: 0xc2cdd8,
    opacity: 0.38,
    roughness: 0.50,
    metalness: 0.05,
    transparent: true,
    depthWrite: false,
  },
  // Muscular interventricular septum — central anatomical core
  struct_septum: {
    color: 0xa4b2c0,
    opacity: 0.40,
    roughness: 0.50,
    metalness: 0.05,
    transparent: true,
    depthWrite: false,
  },
  // Pulmonary trunk — anterior outflow tract
  struct_pulmonary_trunk: {
    color: 0xb0bcc9,
    opacity: 0.42,
    roughness: 0.45,
    metalness: 0.08,
    transparent: true,
    depthWrite: false,
  },
}

const DEFAULT_STYLE: MaterialConfig = {
  color: 0xbac5d2,
  opacity: 0.38,
  roughness: 0.48,
  metalness: 0.06,
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
      emissive: style.emissive ? new THREE.Color(style.emissive) : undefined,
      emissiveIntensity: style.emissiveIntensity ?? 0,
      side: THREE.DoubleSide,
    })
  }, [id])

  if (!visible) return null

  return <mesh geometry={geometry} material={material} />
}
