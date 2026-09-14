export type PhotoTreatmentType =
  | "none"
  | "geometric_drafting"
  | "dither_print"
  | "contour_atlas"
  | "spectral_curtain";

export type DitherAlgorithm = "bayer4" | "atkinson" | "floyd-steinberg";
export type DitherPalette = "cobalt" | "signal" | "mono" | "cyan" | "electric";

export interface GeometricDraftingOptions {
  gridModules?: number;
  showCoordinates?: boolean;
  showBrackets?: boolean;
  showCrosshairs?: boolean;
  accentColor?: string;
  textColor?: string;
  seed?: number;
  metadataLabels?: string[];
}

export interface DitherPrintOptions {
  algorithm?: DitherAlgorithm;
  palette?: DitherPalette;
  cellSize?: number;
  contrast?: number;
  invert?: boolean;
  blendMode?: string;
  opacity?: number;
}

export interface ContourAtlasOptions {
  levels?: number;
  opacity?: number;
  drift?: number;
  style?: "topographic" | "flow";
  strokeColor?: string;
  seed?: number;
}

export interface SpectralCurtainOptions {
  curtainDensity?: number;
  curtainLength?: number;
  curtainOpacity?: number;
  direction?: "down" | "up" | "both";
  chromaticShift?: number;
}

export interface PhotoTreatmentConfig {
  type: PhotoTreatmentType;
  drafting?: GeometricDraftingOptions;
  dither?: DitherPrintOptions;
  contour?: ContourAtlasOptions;
  curtain?: SpectralCurtainOptions;
}

export interface MultiImageStrobeProps {
  images: string[];
  frame: number;
  fps: number;
  durationInFrames: number;
  strobeInterval?: number; // frames per image slice, default 1
  enableLensFlash?: boolean;
  enableChromaticAberration?: boolean;
  enableDraftingHUD?: boolean;
  accentColor?: string;
  sfxCue?: string;
}

export type ContactSheetLayout =
  | "split_duo"
  | "tri_slice"
  | "quad_grid"
  | "asymmetric_hero";

export interface GeometricContactSheetProps {
  images: string[];
  layout?: ContactSheetLayout;
  frame: number;
  fps: number;
  durationInFrames: number;
  accentColor?: string;
  coordinates?: string[];
  showDraftingMarks?: boolean;
}
