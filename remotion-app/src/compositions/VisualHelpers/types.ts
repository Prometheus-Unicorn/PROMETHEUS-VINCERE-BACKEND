import React from "react";

export type VisualHelperType =
  | "before_after_comparison"
  | "listicle"
  | "motion_number"
  | "callout_badge";

export type VisualHelperTexture =
  | "liquid_glass"
  | "mesh_gradient"
  | "liquid_gradient"
  | "blur_vignette"
  | "clean";

export type VisualHelperPosition =
  | "flank_left"
  | "flank_right"
  | "lower_deck"
  | "cranial_top"
  | "center";

export interface ListicleItem {
  id: string;
  text: string;
  label?: string;
  icon?: string;
  number?: number;
  highlight?: boolean;
}

export interface VisualHelper {
  type: VisualHelperType;
  title?: string;
  subtitle?: string;
  badge?: string;
  texture?: VisualHelperTexture;
  rippleEffect?: boolean;
  noiseOverlay?: boolean;
  position?: VisualHelperPosition;
  accentColor?: string;
  primaryColor?: string;

  // Archetype 1: before_after_comparison
  beforeLabel?: string;
  beforeImage?: string;
  beforeValue?: string;
  afterLabel?: string;
  afterImage?: string;
  afterValue?: string;
  splitRatio?: number; // 0..1 or frame-driven

  // Archetype 2: listicle
  items?: ListicleItem[];
  activeIndex?: number;

  // Archetype 3: motion_number
  value?: number;
  targetValue?: number;
  prefix?: string;
  suffix?: string;
  format?: "number" | "currency" | "percent";
  decimals?: number;

  // Archetype 4: callout_badge
  icon?: "star" | "zap" | "check" | "alert" | "trending" | "shield" | "flame" | "target";
  calloutStyle?: "minimal" | "pill" | "banner";
}

export interface VisualHelperComponentProps {
  helper: VisualHelper;
  frame: number;
  fps: number;
  palette?: {
    hero_color?: string;
    companion_color?: string;
    accent_border?: string;
    glow?: string;
    shadow?: string;
  };
}
