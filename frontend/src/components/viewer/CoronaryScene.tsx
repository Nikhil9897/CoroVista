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
  dismissedLabels?: Set<CoronaryVesselId>
  onDismissLabel?: (id: CoronaryVesselId) => void
  onSelectVessel: (id: CoronaryVesselId | null) => void
  onHoverVessel: (info: HoveredVesselInfo | null) => void
}

// Anatomical heart center offset from complete 18-mesh cohesive assembly:
// Centroid in mm: X=23.09, Y=-128.55, Z=1233.94
const OFFSET_X = -23.09
const OFFSET_Y = 128.55
const OFFSET_Z = -1233.94

// Anatomical camera target: centered slightly below base towards ventricular body
const TARGET_POINT: [number, number, number] = [0, -5, 0]

// Presets calibrated for full 110.5 x 93.1 x 117.4 mm cohesive heart at ~210 mm distance
const PRESET_POSITIONS: Record<ViewPreset, [number, number, number]> = {
  ap: [0, -5, 210],
  rao: [-120, -5, 175],
  lao: [135, -5, 160],
  posterior: [0, -5, -210],
  reset: [0, -5, 210],
}

// Vessel-specific viewing angles preserving full anatomical heart context
const FOCUS_POSITIONS: Record<CoronaryVesselId, [number, number, number]> = {
  lad: [45, -12, 190],
  lcx: [145, -5, 145],
  rca: [-125, -5, 165],
}

const FOCUS_TARGETS: Record<CoronaryVesselId, [number, number, number]> = {
  lad: [12, -12, 0],
  lcx: [18, -5, -8],
  rca: [-14, -5, 0],
}

export const CoronaryScene: React.FC<CoronarySceneProps> = ({
  predictions,
  selectedTarget,
  focusedVessel,
  visibility,
  presetTrigger,
  dismissedLabels,
  onDismissLabel,
  onSelectVessel,
  onHoverVessel,
}) => {
  const controlsRef = useRef<OrbitControlsImpl>(null)
  const targetCamPos = useRef<THREE.Vector3 | null>(null)
  const targetLookAt = useRef<THREE.Vector3 | null>(null)

  // Load the pre-processed master scene GLB containing all reconstructed anatomical nodes
  const gltf = useGLTF("/models/corovista_heart.glb")

  // Camera preset trigger sets smooth interpolation target
  useEffect(() => {
    if (!presetTrigger || !controlsRef.current) return
    const pos = PRESET_POSITIONS[presetTrigger.preset] || PRESET_POSITIONS.ap
    targetCamPos.current = new THREE.Vector3(...pos)
    targetLookAt.current = new THREE.Vector3(...TARGET_POINT)
  }, [presetTrigger])

  // Focus mode camera transition: smooth re-orientation at natural default distance
  useEffect(() => {
    if (!controlsRef.current) return
    if (focusedVessel && focusedVessel in FOCUS_POSITIONS) {
      targetCamPos.current = new THREE.Vector3(...FOCUS_POSITIONS[focusedVessel])
      targetLookAt.current = new THREE.Vector3(...FOCUS_TARGETS[focusedVessel])
    } else if (!focusedVessel) {
      targetCamPos.current = new THREE.Vector3(...PRESET_POSITIONS.ap)
      targetLookAt.current = new THREE.Vector3(...TARGET_POINT)
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
        minDistance={80}
        maxDistance={400}
        target={TARGET_POINT}
        rotateSpeed={0.8}
        zoomSpeed={0.9}
        panSpeed={0.7}
      />

      {/* Clinical Anatomical Studio Lighting: soft balanced illumination without harsh hotspots */}
      <ambientLight intensity={0.85} color="#f8fafc" />
      <directionalLight position={[60, 70, 80]} intensity={1.15} color="#ffffff" />
      <directionalLight position={[-60, 30, 60]} intensity={0.75} color="#f1f5f9" />
      <directionalLight position={[0, 40, -85]} intensity={0.65} color="#cbd5e1" />
      <directionalLight position={[0, -75, 30]} intensity={0.25} color="#64748b" />
      <hemisphereLight args={["#f8fafc", "#1e293b", 0.45]} />

      {/* Coordinate transformation group: centers complete heart at (0, 0, 0) and orients AP face forward */}
      <group
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerMissed={() => {
          if (focusedVessel) onSelectVessel(null)
        }}
      >
        <group position={[OFFSET_X, OFFSET_Y, OFFSET_Z]}>
          {/* Primary Coronary Artery Vessels with Risk Prediction Shaders */}
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
          {visibility.lad && nodes.vessel_lad && !dismissedLabels?.has("lad") && (
            <VesselFloatingLabel
              id="lad"
              geometry={nodes.vessel_lad.geometry}
              probability={ladPred ? ladPred.probability : 0.0}
              threshold={ladPred ? ladPred.threshold : 0.46}
              isSelected={focusedVessel === "lad" || selectedTarget === "lad"}
              isAnyFocused={isAnyFocused}
              onClick={(id) => onSelectVessel(id)}
              onDismiss={onDismissLabel}
            />
          )}

          {visibility.lcx && nodes.vessel_lcx && !dismissedLabels?.has("lcx") && (
            <VesselFloatingLabel
              id="lcx"
              geometry={nodes.vessel_lcx.geometry}
              probability={lcxPred ? lcxPred.probability : 0.0}
              threshold={lcxPred ? lcxPred.threshold : 0.50}
              isSelected={focusedVessel === "lcx" || selectedTarget === "lcx"}
              isAnyFocused={isAnyFocused}
              onClick={(id) => onSelectVessel(id)}
              onDismiss={onDismissLabel}
            />
          )}

          {visibility.rca && nodes.vessel_rca && !dismissedLabels?.has("rca") && (
            <VesselFloatingLabel
              id="rca"
              geometry={nodes.vessel_rca.geometry}
              probability={rcaPred ? rcaPred.probability : 0.0}
              threshold={rcaPred ? rcaPred.threshold : 0.38}
              isSelected={focusedVessel === "rca" || selectedTarget === "rca"}
              isAnyFocused={isAnyFocused}
              onClick={(id) => onSelectVessel(id)}
              onDismiss={onDismissLabel}
            />
          )}

          {/* Left Main Stem (Root arterial trunk) */}
          {nodes.struct_left_main && (
            <ContextAnatomyMesh
              id="struct_left_main"
              geometry={nodes.struct_left_main.geometry}
              visible={true}
            />
          )}

          {/* Great Vessels */}
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

          {nodes.struct_pulmonary_trunk && (
            <ContextAnatomyMesh
              id="struct_pulmonary_trunk"
              geometry={nodes.struct_pulmonary_trunk.geometry}
              visible={visibility.context}
            />
          )}

          {/* Cohesive Reconstructed Ventricular Myocardium */}
          {nodes.struct_myocardium && (
            <ContextAnatomyMesh
              id="struct_myocardium"
              geometry={nodes.struct_myocardium.geometry}
              visible={visibility.context}
            />
          )}

          {/* Reconstructed Auricles framing the base */}
          {nodes.struct_auricles && (
            <ContextAnatomyMesh
              id="struct_auricles"
              geometry={nodes.struct_auricles.geometry}
              visible={visibility.context}
            />
          )}

          {/* Compatibility fallbacks if separate chamber walls are provided */}
          {nodes.struct_lv_wall && (
            <ContextAnatomyMesh
              id="struct_lv_wall"
              geometry={nodes.struct_lv_wall.geometry}
              visible={visibility.context}
            />
          )}
          {nodes.struct_rv_wall && (
            <ContextAnatomyMesh
              id="struct_rv_wall"
              geometry={nodes.struct_rv_wall.geometry}
              visible={visibility.context}
            />
          )}
          {nodes.struct_ra_wall && (
            <ContextAnatomyMesh
              id="struct_ra_wall"
              geometry={nodes.struct_ra_wall.geometry}
              visible={visibility.context}
            />
          )}
          {nodes.struct_la_wall && (
            <ContextAnatomyMesh
              id="struct_la_wall"
              geometry={nodes.struct_la_wall.geometry}
              visible={visibility.context}
            />
          )}

          {/* Internal Interventricular Septum */}
          {nodes.struct_septum && (
            <ContextAnatomyMesh
              id="struct_septum"
              geometry={nodes.struct_septum.geometry}
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
