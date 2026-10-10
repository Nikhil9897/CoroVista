import React, { useEffect, useRef, useMemo } from "react"
import * as THREE from "three"

interface HeroVisualProps {
  pointer: { x: number; y: number } // Normalized -1 to 1
  isHovered?: boolean
  reducedMotion: boolean
}

// Generate organic sphere positions along a well-proportioned torus/wreath
function generateWreathSpheres(count: number) {
  const data: Array<{
    x: number
    y: number
    z: number
    baseScale: number
    phase: number
    freq: number
    colorGreen: THREE.Color
    colorRed: THREE.Color
    scatterDir: [number, number, number]
    scatterDist: number
  }> = []

  // Torus dimensions sized carefully so NO spheres clip canvas edges
  const majorRadius = 1.85
  const tubeRadius = 0.44

  // Green Palette (Resting State - Sampled Reference Mint)
  const mintBase = new THREE.Color("#5ea88f")
  const mintBright = new THREE.Color("#8ce6c7")
  const mintGlow = new THREE.Color("#d9fbef")
  const mintDeep = new THREE.Color("#3d7866")

  // Red Palette (Hover State - Arterial Coronary Risk)
  const redBase = new THREE.Color("#a83232")
  const redBright = new THREE.Color("#e84a4a")
  const redGlow = new THREE.Color("#ffa3a3")
  const redDeep = new THREE.Color("#781e1e")

  for (let i = 0; i < count; i++) {
    // Distribute angles evenly around the ring
    const theta = (i / count) * Math.PI * 2 + (Math.random() - 0.5) * 0.35

    // Cross-section tube angle
    const phi = Math.random() * Math.PI * 2
    // Radial distance inside tube (concentrated around tube core, minimal stray outliers)
    const rDist = Math.pow(Math.random(), 0.8) * tubeRadius

    // Torus parametric coords
    let x = (majorRadius + rDist * Math.cos(phi)) * Math.cos(theta)
    let y = (majorRadius + rDist * Math.cos(phi)) * Math.sin(theta)
    let z = rDist * Math.sin(phi)

    // Controlled, tight organic jitter (prevents balls from wandering apart)
    const jX = (Math.random() - 0.5) * 0.08
    const jY = (Math.random() - 0.5) * 0.08
    const jZ = (Math.random() - 0.5) * 0.1
    x += jX
    y += jY
    z += jZ

    // Sphere scale: controlled sizes that stay fully within the viewport
    const sizeRoll = Math.random()
    let scale: number
    if (sizeRoll < 0.25) {
      scale = 0.23 + Math.random() * 0.05
    } else if (sizeRoll < 0.75) {
      scale = 0.16 + Math.random() * 0.06
    } else {
      scale = 0.10 + Math.random() * 0.05
    }

    // Determine green shade (resting)
    const innerFacing = Math.cos(phi) < -0.2
    const colorGreen = new THREE.Color()
    if (innerFacing && y > 0.2) {
      colorGreen.copy(mintGlow)
    } else if (Math.random() < 0.45) {
      colorGreen.copy(mintBright)
    } else if (Math.random() < 0.8) {
      colorGreen.copy(mintBase)
    } else {
      colorGreen.copy(mintDeep)
    }

    // Determine red shade (hover)
    const colorRed = new THREE.Color()
    if (innerFacing && y > 0.2) {
      colorRed.copy(redGlow)
    } else if (Math.random() < 0.45) {
      colorRed.copy(redBright)
    } else if (Math.random() < 0.8) {
      colorRed.copy(redBase)
    } else {
      colorRed.copy(redDeep)
    }

    // Localized scatter direction: slight displacement in place (DO NOT expand the ring)
    const sDirX = (Math.random() - 0.5) * 2.0
    const sDirY = (Math.random() - 0.5) * 2.0
    const sDirZ = (Math.random() - 0.5) * 2.0
    const sLen = Math.sqrt(sDirX * sDirX + sDirY * sDirY + sDirZ * sDirZ) || 1
    const scatterDir: [number, number, number] = [sDirX / sLen, sDirY / sLen, sDirZ / sLen]

    // Disintegration extent in place: very small (0.07 to 0.13), keeping ring unexpanded
    const scatterDist = 0.07 + Math.random() * 0.06

    data.push({
      x,
      y,
      z,
      baseScale: scale,
      phase: Math.random() * Math.PI * 2,
      freq: 0.5 + Math.random() * 0.5,
      colorGreen,
      colorRed,
      scatterDir,
      scatterDist,
    })
  }

  return data
}

export const HeroVisual: React.FC<HeroVisualProps> = ({
  pointer,
  reducedMotion,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Keep a stable ref for pointer to avoid recreating the 3D scene on mousemove
  const pointerRef = useRef(pointer)
  useEffect(() => {
    pointerRef.current = pointer
  }, [pointer])

  // Adjust sphere count cleanly based on viewport width
  const sphereCount = useMemo(() => {
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      return 100
    }
    return 165
  }, [])

  useEffect(() => {
    const container = containerRef.current
    const canvas = canvasRef.current
    if (!container || !canvas) return

    let animationFrameId: number
    let isVisible = true
    let isTabActive = true

    // ── 1. Three.js Scene, Camera, Renderer ──
    const scene = new THREE.Scene()

    const width = container.clientWidth || 520
    const height = container.clientHeight || 520

    // Camera distance with comfortable padding so spheres never get cut off
    const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100)
    camera.position.set(0, 0, 8.8)

    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    })
    renderer.setSize(width, height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.15

    // ── 2. Create Spheres with InstancedMesh ──
    const spheres = generateWreathSpheres(sphereCount)
    const sphereGeometry = new THREE.SphereGeometry(1, 26, 26)
    sphereGeometry.computeBoundingSphere()

    // Custom Shader Material:
    // Only the localized region near the cursor turns red and disintegrates in-place!
    const sphereMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uEntranceProgress: { value: reducedMotion ? 1.0 : 0.0 },
        uHitPos: { value: new THREE.Vector3(999, 999, 999) },
        uHitActive: { value: 0.0 },
        uHitRadius: { value: 0.85 }, // Influence radius of localized hover
        uHeartbeat: { value: 1.0 },
      },
      vertexShader: `
        attribute vec3 aColorGreen;
        attribute vec3 aColorRed;
        attribute vec3 aScatterDir;
        attribute float aScatterDist;
        attribute float aPhase;
        attribute float aFreq;
        attribute float aBaseScale;
        attribute vec3 aBasePos;

        uniform float uTime;
        uniform float uEntranceProgress;
        uniform vec3 uHitPos;
        uniform float uHitActive;
        uniform float uHitRadius;
        uniform float uHeartbeat;

        varying vec3 vNormal;
        varying vec3 vViewPosition;
        varying vec3 vColorGreen;
        varying vec3 vColorRed;
        varying vec3 vWorldPos;
        varying float vLocalHover;

        void main() {
          vNormal = normalize(normalMatrix * normal);
          vColorGreen = aColorGreen;
          vColorRed = aColorRed;

          // Compute sphere base world position to measure distance to cursor hit point
          vec4 baseWorld = modelMatrix * vec4(aBasePos, 1.0);
          float distToHit = distance(baseWorld.xyz, uHitPos);

          // ONLY the hovered region receives localHover > 0
          float localHover = smoothstep(uHitRadius, 0.0, distToHit) * uHitActive;
          vLocalHover = localHover;

          // Controlled subtle breathing drift
          float floatTime = uTime * aFreq + aPhase;
          vec3 floatOffset = vec3(
            sin(floatTime * 0.6) * 0.005,
            cos(floatTime * 0.7) * 0.005,
            sin(floatTime * 0.5) * 0.003
          );

          // Disintegrate strictly in place for the hovered region (DO NOT expand the ring)
          vec3 localJitter = vec3(
            sin(uTime * 14.0 + aPhase * 2.0) * 0.015,
            cos(uTime * 16.0 + aPhase * 3.0) * 0.015,
            sin(uTime * 12.0 + aPhase) * 0.012
          );
          vec3 crumbleOffset = (aScatterDir * (aScatterDist * localHover)) + (localJitter * localHover);

          // Heartbeat pulse slightly active on hovered part
          float scaleMod = mix(
            1.0 + sin(uTime * 1.2 + aPhase) * 0.01,
            uHeartbeat,
            localHover * 0.5
          );

          // Entrance stagger scale
          float stagger = clamp((uEntranceProgress * 1.4) - (aPhase / 6.28) * 0.4, 0.0, 1.0);
          float easeScale = smoothstep(0.0, 1.0, stagger);

          float finalScale = aBaseScale * scaleMod * easeScale;

          vec3 finalLocalPos = aBasePos + floatOffset + crumbleOffset;
          vec4 worldPos = modelMatrix * vec4(finalLocalPos + (position * finalScale), 1.0);
          vWorldPos = worldPos.xyz;

          vec4 mvPosition = viewMatrix * worldPos;
          vViewPosition = -mvPosition.xyz;

          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform float uTime;
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        varying vec3 vColorGreen;
        varying vec3 vColorRed;
        varying vec3 vWorldPos;
        varying float vLocalHover;

        void main() {
          vec3 N = normalize(vNormal);
          vec3 V = normalize(vViewPosition);

          // 1. Key Directional Light (Top Left)
          vec3 L1 = normalize(vec3(-0.55, 0.75, 1.0));
          float diff1 = max(dot(N, L1), 0.0);

          // 2. Inner Backlight
          vec3 innerLightPos = vec3(0.0, 0.6, -0.5);
          vec3 L_inner = normalize(innerLightPos - vWorldPos);
          float innerBacklight = max(dot(N, -L_inner), 0.0);

          // 3. Specular Highlight
          vec3 H1 = normalize(L1 + V);
          float spec1 = pow(max(dot(N, H1), 0.0), 32.0) * 0.75;

          // 4. Fresnel Rim Glow
          float fresnel = pow(1.0 - max(dot(N, V), 0.0), 2.3);

          // 5. Translucent Subsurface feel
          float sss = pow(max(dot(-V, L1), 0.0), 2.5) * 0.32;

          // ONLY the hovered part transforms into Red; everything else remains pure Green!
          vec3 baseCol = mix(vColorGreen, vColorRed, vLocalHover);

          vec3 finalColor = baseCol * (0.3 + diff1 * 0.55);

          vec3 innerGlowCol = mix(vec3(0.85, 0.98, 0.94), vec3(1.0, 0.75, 0.75), vLocalHover);
          vec3 rimGlowCol   = mix(vec3(0.55, 0.90, 0.80), vec3(1.0, 0.55, 0.55), vLocalHover);

          finalColor += innerGlowCol * (innerBacklight * 0.42);
          finalColor += rimGlowCol * (fresnel * 0.45);
          finalColor += vec3(0.95, 0.98, 0.98) * spec1;
          finalColor += baseCol * sss;

          gl_FragColor = vec4(finalColor, 1.0);
        }
      `,
      transparent: false,
    })

    const instancedMesh = new THREE.InstancedMesh(sphereGeometry, sphereMaterial, spheres.length)

    // Set custom instance attributes
    const colorsGreen = new Float32Array(spheres.length * 3)
    const colorsRed = new Float32Array(spheres.length * 3)
    const scatterDirs = new Float32Array(spheres.length * 3)
    const scatterDists = new Float32Array(spheres.length)
    const phases = new Float32Array(spheres.length)
    const freqs = new Float32Array(spheres.length)
    const baseScales = new Float32Array(spheres.length)
    const basePositions = new Float32Array(spheres.length * 3)

    const dummy = new THREE.Object3D()

    for (let i = 0; i < spheres.length; i++) {
      const s = spheres[i]
      colorsGreen[i * 3 + 0] = s.colorGreen.r
      colorsGreen[i * 3 + 1] = s.colorGreen.g
      colorsGreen[i * 3 + 2] = s.colorGreen.b

      colorsRed[i * 3 + 0] = s.colorRed.r
      colorsRed[i * 3 + 1] = s.colorRed.g
      colorsRed[i * 3 + 2] = s.colorRed.b

      scatterDirs[i * 3 + 0] = s.scatterDir[0]
      scatterDirs[i * 3 + 1] = s.scatterDir[1]
      scatterDirs[i * 3 + 2] = s.scatterDir[2]

      scatterDists[i] = s.scatterDist

      phases[i] = s.phase
      freqs[i] = s.freq
      baseScales[i] = s.baseScale

      basePositions[i * 3 + 0] = s.x
      basePositions[i * 3 + 1] = s.y
      basePositions[i * 3 + 2] = s.z

      dummy.position.set(s.x, s.y, s.z)
      dummy.scale.set(s.baseScale, s.baseScale, s.baseScale)
      dummy.updateMatrix()
      instancedMesh.setMatrixAt(i, dummy.matrix)
    }

    sphereGeometry.setAttribute("aColorGreen", new THREE.InstancedBufferAttribute(colorsGreen, 3))
    sphereGeometry.setAttribute("aColorRed", new THREE.InstancedBufferAttribute(colorsRed, 3))
    sphereGeometry.setAttribute("aScatterDir", new THREE.InstancedBufferAttribute(scatterDirs, 3))
    sphereGeometry.setAttribute("aScatterDist", new THREE.InstancedBufferAttribute(scatterDists, 1))
    sphereGeometry.setAttribute("aPhase", new THREE.InstancedBufferAttribute(phases, 1))
    sphereGeometry.setAttribute("aFreq", new THREE.InstancedBufferAttribute(freqs, 1))
    sphereGeometry.setAttribute("aBaseScale", new THREE.InstancedBufferAttribute(baseScales, 1))
    sphereGeometry.setAttribute("aBasePos", new THREE.InstancedBufferAttribute(basePositions, 3))

    instancedMesh.instanceMatrix.needsUpdate = true
    instancedMesh.computeBoundingSphere()

    // Ring pivot group for perpetual continuous 3D rotation
    const ringGroup = new THREE.Group()
    ringGroup.add(instancedMesh)
    scene.add(ringGroup)

    ringGroup.rotation.x = 0.15
    ringGroup.rotation.y = -0.1

    // ── 3. Precise Raycasting for Hover STRICTLY on the Circle of Spheres ──
    const raycaster = new THREE.Raycaster()
    const mouseNDC = new THREE.Vector2(-999, -999)
    const targetHitPos = new THREE.Vector3(999, 999, 999)
    const currentHitPos = new THREE.Vector3(999, 999, 999)
    let targetHitActive = 0.0
    let currentHitActive = 0.0

    const handleCanvasPointerMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect()
      mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
      mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
    }

    const handleCanvasPointerLeave = () => {
      mouseNDC.set(-999, -999)
    }

    canvas.addEventListener("pointermove", handleCanvasPointerMove)
    canvas.addEventListener("pointerleave", handleCanvasPointerLeave)

    // ── 4. Calm Cardiovascular Heartbeat Impulse (~65 bpm) ──
    function getHeartbeat(time: number): number {
      const cycle = (time % 0.923) / 0.923
      if (cycle < 0.12) {
        return 1.0 + Math.sin((cycle / 0.12) * Math.PI) * 0.06
      } else if (cycle > 0.18 && cycle < 0.32) {
        const sub = (cycle - 0.18) / 0.14
        return 1.0 + Math.sin(sub * Math.PI) * 0.035
      }
      return 1.0
    }

    // ── 5. Animation Loop with Perpetual Rotation ──
    let entranceProgress = reducedMotion ? 1.0 : 0.0
    let continuousAngle = 0.0
    const clock = new THREE.Clock()

    const currentRotation = { x: 0.15, y: -0.1 }
    const targetRotation = { x: 0.15, y: -0.1 }

    function animate() {
      if (!isVisible || !isTabActive) {
        animationFrameId = requestAnimationFrame(animate)
        return
      }

      const delta = clock.getDelta()
      const elapsedTime = clock.getElapsedTime()

      // Entrance animation
      if (entranceProgress < 1.0) {
        entranceProgress = Math.min(1.0, entranceProgress + 0.016)
        sphereMaterial.uniforms.uEntranceProgress.value = entranceProgress
      }

      // Check raycast intersection STRICTLY on the sphere mesh
      let isStrictlyOverSpheres = false
      if (mouseNDC.x >= -1.05 && mouseNDC.x <= 1.05 && mouseNDC.y >= -1.05 && mouseNDC.y <= 1.05) {
        raycaster.setFromCamera(mouseNDC, camera)
        const intersects = raycaster.intersectObject(instancedMesh)
        if (intersects.length > 0) {
          isStrictlyOverSpheres = true
          targetHitPos.copy(intersects[0].point)
          targetHitActive = 1.0
        }
      }

      if (!isStrictlyOverSpheres) {
        targetHitActive = 0.0
      }

      // Smoothly lerp hit activation & position
      currentHitActive += (targetHitActive - currentHitActive) * 0.09
      if (isStrictlyOverSpheres) {
        currentHitPos.lerp(targetHitPos, 0.2)
      }

      sphereMaterial.uniforms.uHitPos.value.copy(currentHitPos)
      sphereMaterial.uniforms.uHitActive.value = currentHitActive
      sphereMaterial.uniforms.uTime.value = elapsedTime
      sphereMaterial.uniforms.uHeartbeat.value = getHeartbeat(elapsedTime)

      // ── PERPETUAL CONTINUOUS ROTATION (Rotates forever) ──
      if (!reducedMotion) {
        continuousAngle += delta * 0.32
        ringGroup.rotation.z = continuousAngle

        // Subtle 3D tilt with gentle cursor parallax
        targetRotation.x = 0.15 + pointerRef.current.y * 0.08
        targetRotation.y = -0.1 + pointerRef.current.x * 0.1

        currentRotation.x += (targetRotation.x - currentRotation.x) * 0.04
        currentRotation.y += (targetRotation.y - currentRotation.y) * 0.04

        ringGroup.rotation.x = currentRotation.x
        ringGroup.rotation.y = currentRotation.y
      }

      renderer.render(scene, camera)
      animationFrameId = requestAnimationFrame(animate)
    }

    animate()

    // ── 6. Resize Handler ──
    const handleResize = () => {
      if (!container || !renderer || !camera) return
      const w = container.clientWidth
      const h = container.clientHeight
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h)
    }

    const resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(container)

    // ── 7. Visibility & Tab Change Optimization ──
    const handleVisibilityChange = () => {
      isTabActive = !document.hidden
    }
    document.addEventListener("visibilitychange", handleVisibilityChange)

    const intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          isVisible = entry.isIntersecting
        })
      },
      { threshold: 0.05 }
    )
    intersectionObserver.observe(container)

    // ── 8. Cleanup on Unmount ──
    return () => {
      cancelAnimationFrame(animationFrameId)
      resizeObserver.disconnect()
      intersectionObserver.disconnect()
      document.removeEventListener("visibilitychange", handleVisibilityChange)
      canvas.removeEventListener("pointermove", handleCanvasPointerMove)
      canvas.removeEventListener("pointerleave", handleCanvasPointerLeave)

      scene.remove(ringGroup)
      ringGroup.remove(instancedMesh)
      sphereGeometry.dispose()
      sphereMaterial.dispose()
      renderer.dispose()
    }
  }, [sphereCount, reducedMotion])

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[380px] sm:min-h-[460px] lg:min-h-[500px] max-h-[540px] flex items-center justify-center select-none overflow-visible"
      aria-hidden="true"
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full block cursor-pointer outline-none"
      />
    </div>
  )
}
