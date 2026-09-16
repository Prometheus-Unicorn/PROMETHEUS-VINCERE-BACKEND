import { SpringConfig } from "remotion";

/**
 * Governed Motion Physics Tokens for Animated Visual Assets.
 * Banning arbitrary magic numbers to prevent visual cellulite, jitter, and erratic overshoots.
 */
export const SPRING_TACTILE: SpringConfig = {
  damping: 28,
  stiffness: 220,
  mass: 0.8,
  overshootClamping: true,
};

export const SPRING_ORGANIC: SpringConfig = {
  damping: 18,
  stiffness: 140,
  mass: 1.0,
  overshootClamping: false,
};

export const SPRING_KINETIC: SpringConfig = {
  damping: 14,
  stiffness: 160,
  mass: 0.9,
  overshootClamping: false,
};

/**
 * Standardized High-End Glass Backplate & Lighting Tokens (Rec.709 safe).
 * Prevents ad-hoc CSS backplates with shadow crush or flat, mid-tier aesthetics.
 */
export const GLASS_SURFACE_TOKENS = {
  background: "rgba(15, 23, 42, 0.72)",
  backdropFilter: "blur(24px) saturate(180%)",
  WebkitBackdropFilter: "blur(24px) saturate(180%)",
  borderRadius: "20px",
  border: "1px solid rgba(255, 255, 255, 0.12)",
  innerBorder: "inset 0 1px 1px rgba(255, 255, 255, 0.18)",
  boxShadow:
    "0 24px 48px -12px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.05), inset 0 1px 1px rgba(255, 255, 255, 0.18)",
  specularSheenGradient:
    "linear-gradient(135deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.04) 40%, rgba(255,255,255,0) 100%)",
};

/**
 * Standard Typography Tokens for UI & Metric Cards.
 */
export const ASSET_TYPOGRAPHY_TOKENS = {
  kicker: {
    fontFamily: '"Montserrat", sans-serif',
    fontSize: "11px",
    fontWeight: 800,
    letterSpacing: "0.14em",
    textTransform: "uppercase" as const,
    color: "rgba(255, 255, 255, 0.65)",
  },
  title: {
    fontFamily: '"Montserrat", "Plus Jakarta Sans", sans-serif',
    fontSize: "18px",
    fontWeight: 800,
    letterSpacing: "-0.01em",
    color: "#FFFFFF",
  },
  metricDisplay: {
    fontFamily: '"Anton", "Montserrat", sans-serif',
    fontSize: "64px",
    fontWeight: 900,
    lineHeight: 1.0,
    letterSpacing: "-0.02em",
  },
  dateGrid: {
    fontFamily: '"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif',
    fontSize: "13px",
    fontWeight: 600,
  },
};

/**
 * Architectural Contract for Visual Assets.
 * Every registered component must declare its provenance and validate dynamic props.
 */
export interface IAnimatedAssetArchetype {
  archetypeId: string;
  provenance: "21st.dev-authentic" | "origin-kit-authentic" | "governed-core";
  version: string;
  hasStaticMockData: false;
  physicsProfile: "tactile" | "organic" | "kinetic";
  maxFrameOccupancyPct: number;
}
