import React, { useEffect, useRef } from "react"
import { useGLTF, OrbitControls } from "@react-three/drei"
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

interface CoronarySceneProps {
  predictions?: PredictionResponse["predictions"]
  selectedTarget?: TargetName
  visibility: ViewerVisibilityState
  presetTrigger: { preset: ViewPreset; timestamp: number } | null
  onSelectVessel: (id: CoronaryVesselId) => void
  onHoverVessel: (info: HoveredVesselInfo | null) => void
}

// Global heart center offset from BodyParts3D DICOM inventory:
// Centroid in mm: X=20.10, Y=-124.14, Z=1236.43
const OFFSET_X = -20.1
const OFFSET_Y = 124.14
const OFFSET_Z = -1236.43

export const CoronaryScene: React.FC<CoronarySceneProps> = ({
  predictions,
  selectedTarget,
  visibility,
  presetTrigger,
  onSelectVessel,
  onHoverVessel,
}) => {
  const controlsRef = useRef<OrbitControlsImpl>(null)

  // Load the pre-processed master scene GLB
  const gltf = useGLTF("/models/corovista_heart.glb")

  // Camera preset handler
  useEffect(() => {
    if (!presetTrigger || !controlsRef.current) return

    const controls = controlsRef.current
    const camera = controls.object as THREE.PerspectiveCamera

    const presetPositions: Record<ViewPreset, [number, number, number]> = {
      ap: [0, -6, 138],
      rao: [-72, -6, 118],
      lao: [96, -6, 96],
      posterior: [0, -6, -138],
      reset: [0, -6, 138],
    }

    const targetPos = presetPositions[presetTrigger.preset] || [0, -6, 138]
    camera.position.set(...targetPos)
    controls.target.set(0, 0, 0)
    controls.update()
  }, [presetTrigger])

  // Extract geometries from loaded nodes
  const nodes = gltf.nodes as Record<string, THREE.Mesh>

  // Continuous predictions or defaults
  const ladPred = predictions?.lad
  const lcxPred = predictions?.lcx
  const rcaPred = predictions?.rca

  return (
    <>
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.08}
        minDistance={45}
        maxDistance={320}
        target={[0, 0, 0]}
        rotateSpeed={0.8}
        zoomSpeed={0.9}
        panSpeed={0.7}
      />

      {/* Anatomical Studio Lighting */}
      <ambientLight intensity={0.9} />
      <directionalLight position={[60, 90, 100]} intensity={1.3} castShadow={false} />
      <directionalLight position={[-60, 30, 80]} intensity={0.8} />
      <directionalLight position={[0, 40, -100]} intensity={1.1} /> {/* Rim light for LCX */}
      <directionalLight position={[0, -80, 40]} intensity={0.4} /> {/* Under light for apex */}

      {/* Coordinate transformation group: centers heart at (0, 0, 0) and orients AP face forward */}
      <group rotation={[-Math.PI / 2, 0, 0]}>
        <group position={[OFFSET_X, OFFSET_Y, OFFSET_Z]}>
          {/* Primary Coronary Artery Vessels */}
          {nodes.vessel_lad && (
            <CoronaryVesselMesh
              id="lad"
              geometry={nodes.vessel_lad.geometry}
              probability={ladPred ? ladPred.probability : 0.0}
              threshold={ladPred ? ladPred.threshold : 0.46}
              isStenotic={ladPred ? ladPred.probability >= ladPred.threshold : false}
              isSelected={selectedTarget === "lad"}
              visible={visibility.lad}
              onClick={onSelectVessel}
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
              isSelected={selectedTarget === "lcx"}
              visible={visibility.lcx}
              onClick={onSelectVessel}
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
              isSelected={selectedTarget === "rca"}
              visible={visibility.rca}
              onClick={onSelectVessel}
              onHover={onHoverVessel}
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
