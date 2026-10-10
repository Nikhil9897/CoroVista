import React, { useEffect, useRef } from "react"
import { useGLTF, OrbitControls } from "@react-three/drei"
import { useFrame } from "@react-three/fiber"
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib"
import * as THREE from "three"
import type {
  CoronaryVesselId,
  HoveredVesselInfo,
  ViewerVisibilityState,
  ViewPreset,
} from "./ViewerTypes"
import type { TargetName, PredictionResponse } from "@/types/prediction"
import { CoronaryVesselMesh } from "./CoronaryVesselMesh"
import { ContextAnatomyMesh } from "./ContextAnatomyMesh"
import { VesselFloatingLabel } from "./VesselFloatingLabel"

interface CoronarySceneProps {
  predictions?: PredictionResponse["predictions"]
  selectedTarget?: TargetName | null
  focusedVessel?: CoronaryVesselId | null
  visibility: ViewerVisibilityState
  presetTrigger: { preset: ViewPreset; timestamp: number } | null
  onSelectVessel: (id: CoronaryVesselId | null) => void
  onHoverVessel: (info: HoveredVesselInfo | null) => void
}

// Global heart center offset from BodyParts3D DICOM inventory:
// Centroid in mm: X=20.10, Y=-124.14, Z=1236.43
const OFFSET_X = -20.1
const OFFSET_Y = 124.14
const OFFSET_Z = -1236.43

// Optimal camera positions at ~96mm distance for ideal 70% viewport fill
const PRESET_POSITIONS: Record<ViewPreset, [number, number, number]> = {
  ap: [0, -6, 96],
  rao: [-54, -6, 78],
  lao: [68, -6, 68],
  posterior: [0, -6, -96],
  reset: [0, -6, 96],
}

// Vessel-specific focus camera positions for clear, unobstructed diagnostic views
const FOCUS_POSITIONS: Record<CoronaryVesselId, [number, number, number]> = {
  lad: [14, -8, 64],
  lcx: [52, -4, 54],
  rca: [-44, -8, 62],
}

const FOCUS_TARGETS: Record<CoronaryVesselId, [number, number, number]> = {
  lad: [2, -8, 0],
  lcx: [10, -4, 0],
  rca: [-8, -8, 0],
}

export const CoronaryScene: React.FC<CoronarySceneProps> = ({
  predictions,
  selectedTarget,
  focusedVessel,
  visibility,
  presetTrigger,
  onSelectVessel,
  onHoverVessel,
}) => {
  const controlsRef = useRef<OrbitControlsImpl>(null)
  const targetCamPos = useRef<THREE.Vector3 | null>(null)
  const targetLookAt = useRef<THREE.Vector3 | null>(null)

  // Load the pre-processed master scene GLB
  const gltf = useGLTF("/models/corovista_heart.glb")

  // Camera preset trigger sets smooth interpolation target
  useEffect(() => {
    if (!presetTrigger || !controlsRef.current) return
    const pos = PRESET_POSITIONS[presetTrigger.preset] || PRESET_POSITIONS.ap
    targetCamPos.current = new THREE.Vector3(...pos)
    targetLookAt.current = new THREE.Vector3(0, -6, 0)
  }, [presetTrigger])

  // Focus mode camera transition
  useEffect(() => {
    if (!controlsRef.current) return
    if (focusedVessel && focusedVessel in FOCUS_POSITIONS) {
      targetCamPos.current = new THREE.Vector3(...FOCUS_POSITIONS[focusedVessel])
      targetLookAt.current = new THREE.Vector3(...FOCUS_TARGETS[focusedVessel])
    }
  }, [focusedVessel])

  // Smooth camera flight on preset change and vessel focus
  useFrame((_, delta) => {
    if (!controlsRef.current) return
    const controls = controlsRef.current
    const camera = controls.object as THREE.PerspectiveCamera

    if (targetCamPos.current) {
      camera.position.lerp(targetCamPos.current, Math.min(1, delta * 4.5))
      if (camera.position.distanceTo(targetCamPos.current) < 0.25) {
        targetCamPos.current = null
      }
    }

    if (targetLookAt.current) {
      controls.target.lerp(targetLookAt.current, Math.min(1, delta * 4.5))
      if (controls.target.distanceTo(targetLookAt.current) < 0.2) {
        targetLookAt.current = null
      }
    }

    controls.update()
  })

  // Extract geometries from loaded nodes
  const nodes = gltf.nodes as Record<string, THREE.Mesh>

  // Continuous predictions or defaults
  const ladPred = predictions?.lad
  const lcxPred = predictions?.lcx
  const rcaPred = predictions?.rca

  const isAnyFocused = Boolean(focusedVessel)

  return (
    <>
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.08}
        minDistance={40}
        maxDistance={220}
        target={[0, -6, 0]}
        rotateSpeed={0.8}
        zoomSpeed={0.9}
        panSpeed={0.7}
      />

      {/* Clean Clinical Studio Lighting for White Viewport */}
      <ambientLight intensity={1.1} color="#ffffff" />
      <directionalLight position={[70, 80, 90]} intensity={1.4} color="#ffffff" />
      <directionalLight position={[-70, 30, 70]} intensity={0.8} color="#e2e8f0" />
      <directionalLight position={[0, 45, -90]} intensity={0.9} color="#cbd5e1" />
      <directionalLight position={[0, -90, 40]} intensity={0.4} color="#f1f5f9" />
      <hemisphereLight args={["#ffffff", "#e2e8f0", 0.6]} />

      {/* Coordinate transformation group: centers heart at (0, 0, 0) and orients AP face forward */}
      <group
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerMissed={() => {
          if (focusedVessel) onSelectVessel(null)
        }}
      >
        <group position={[OFFSET_X, OFFSET_Y, OFFSET_Z]}>
          {/* Primary Coronary Artery Vessels */}
          {nodes.vessel_lad && (
            <CoronaryVesselMesh
              id="lad"
              geometry={nodes.vessel_lad.geometry}
              probability={ladPred ? ladPred.probability : 0.0}
              threshold={ladPred ? ladPred.threshold : 0.46}
              isStenotic={ladPred ? ladPred.probability >= ladPred.threshold : false}
              isSelected={focusedVessel === "lad" || selectedTarget === "lad"}
              isAnyFocused={isAnyFocused}
              visible={visibility.lad}
              onClick={(id) => onSelectVessel(id)}
              onHover={onHoverVessel}
            />
          )}

          {nodes.vessel_lcx && (
            <CoronaryVesselMesh
              id="lcx"
              geometry={nodes.vessel_lcx.geometry}
              probability={lcxPred ? lcxPred.probability : 0.0}
              threshold={lcxPred ? lcxPred.threshold : 0.5}
              isStenotic={lcxPred ? lcxPred.probability >= lcxPred.threshold : false}
              isSelected={focusedVessel === "lcx" || selectedTarget === "lcx"}
              isAnyFocused={isAnyFocused}
              visible={visibility.lcx}
              onClick={(id) => onSelectVessel(id)}
              onHover={onHoverVessel}
            />
          )}

          {nodes.vessel_rca && (
            <CoronaryVesselMesh
              id="rca"
              geometry={nodes.vessel_rca.geometry}
              probability={rcaPred ? rcaPred.probability : 0.0}
              threshold={rcaPred ? rcaPred.threshold : 0.38}
              isStenotic={rcaPred ? rcaPred.probability >= rcaPred.threshold : false}
              isSelected={focusedVessel === "rca" || selectedTarget === "rca"}
              isAnyFocused={isAnyFocused}
              visible={visibility.rca}
              onClick={(id) => onSelectVessel(id)}
              onHover={onHoverVessel}
            />
          )}

          {/* Anchored In-scene Diagnostic Annotations */}
          {visibility.lad && nodes.vessel_lad && (
            <VesselFloatingLabel
              id="lad"
              geometry={nodes.vessel_lad.geometry}
              probability={ladPred ? ladPred.probability : 0.0}
              threshold={ladPred ? ladPred.threshold : 0.46}
              isSelected={focusedVessel === "lad" || selectedTarget === "lad"}
              isAnyFocused={isAnyFocused}
              onClick={(id) => onSelectVessel(id)}
            />
          )}

          {visibility.lcx && nodes.vessel_lcx && (
            <VesselFloatingLabel
              id="lcx"
              geometry={nodes.vessel_lcx.geometry}
              probability={lcxPred ? lcxPred.probability : 0.0}
              threshold={lcxPred ? lcxPred.threshold : 0.50}
              isSelected={focusedVessel === "lcx" || selectedTarget === "lcx"}
              isAnyFocused={isAnyFocused}
              onClick={(id) => onSelectVessel(id)}
            />
          )}

          {visibility.rca && nodes.vessel_rca && (
            <VesselFloatingLabel
              id="rca"
              geometry={nodes.vessel_rca.geometry}
              probability={rcaPred ? rcaPred.probability : 0.0}
              threshold={rcaPred ? rcaPred.threshold : 0.38}
              isSelected={focusedVessel === "rca" || selectedTarget === "rca"}
              isAnyFocused={isAnyFocused}
              onClick={(id) => onSelectVessel(id)}
            />
          )}

          {/* Left Main Stem (Root) */}
          {nodes.struct_left_main && (
            <ContextAnatomyMesh
              id="struct_left_main"
              geometry={nodes.struct_left_main.geometry}
              visible={true}
            />
          )}

          {/* Supporting Context Anatomy */}
          {nodes.struct_aorta_bulb && (
            <ContextAnatomyMesh
              id="struct_aorta_bulb"
              geometry={nodes.struct_aorta_bulb.geometry}
              visible={visibility.context}
            />
          )}

          {nodes.struct_aorta_ascending && (
            <ContextAnatomyMesh
              id="struct_aorta_ascending"
              geometry={nodes.struct_aorta_ascending.geometry}
              visible={visibility.context}
            />
          )}

          {nodes.struct_lv_wall && (
            <ContextAnatomyMesh
              id="struct_lv_wall"
              geometry={nodes.struct_lv_wall.geometry}
              visible={visibility.context}
            />
          )}

          {nodes.struct_septum && (
            <ContextAnatomyMesh
              id="struct_septum"
              geometry={nodes.struct_septum.geometry}
              visible={visibility.context}
            />
          )}

          {nodes.struct_pulmonary_trunk && (
            <ContextAnatomyMesh
              id="struct_pulmonary_trunk"
              geometry={nodes.struct_pulmonary_trunk.geometry}
              visible={visibility.context}
            />
          )}
        </group>
      </group>
    </>
  )
}

// Preload the master GLB to guarantee instant snappy rendering
useGLTF.preload("/models/corovista_heart.glb")
