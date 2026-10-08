import type { TargetName, PredictionResponse } from "@/types/prediction"

export type CoronaryVesselId = "lad" | "lcx" | "rca"

export interface ViewerVisibilityState {
  lad: boolean
  lcx: boolean
  rca: boolean
  context: boolean
}

export type ViewPreset = "ap" | "lao" | "rao" | "posterior" | "reset"

export interface CoronaryViewerProps {
  predictions?: PredictionResponse["predictions"]
  selectedTarget?: TargetName
  onSelectTarget?: (target: TargetName) => void
  className?: string
}

export interface HoveredVesselInfo {
  id: CoronaryVesselId
  short: string
  full: string
  probability: number
  threshold: number
  isStenotic: boolean
  territory: string
  screenX?: number
  screenY?: number
}
