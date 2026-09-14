import React from "react";
import { NoiseOverlay } from "./NoiseOverlay";

export interface LiquidMeshGradientProps {
  frame?: number;
  fps?: number;
  primaryColor?: string;
  accentColor?: string;
  opacity?: number;
  noise?: boolean;
  borderRadius?: string;
  style?: React.CSSProperties;
}

export const LiquidMeshGradient: React.FC<LiquidMeshGradientProps> = ({
  frame = 0,
  fps = 30,
  primaryColor = "#8B5CF6", // Electric Violet
  accentColor = "#06B6D4",  // Cyan Glow
  opacity = 0.85,
  noise = true,
  borderRadius = "28px",
  style = {},
}) => {
  const time = frame / fps;

  // Undulating focal points
  const cx1 = (50 + 25 * Math.sin(time * 1.4)).toFixed(2);
  const cy1 = (45 + 20 * Math.cos(time * 1.1)).toFixed(2);

  const cx2 = (55 - 22 * Math.cos(time * 0.9)).toFixed(2);
  const cy2 = (55 + 22 * Math.sin(time * 1.3)).toFixed(2);

  const angleDeg = ((frame * 1.2) % 360).toFixed(1);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        borderRadius,
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 0,
        opacity,
        ...style,
      }}
    >
      <svg
        width="100%"
        height="100%"
        xmlns="http://www.w3.org/2000/svg"
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
      >
        <defs>
          <radialGradient id={`liquid-rad-1-${frame % 60}`} cx={`${cx1}%`} cy={`${cy1}%`} r="75%">
            <stop offset="0%" stopColor={primaryColor} stopOpacity="0.8" />
            <stop offset="45%" stopColor={accentColor} stopOpacity="0.45" />
            <stop offset="85%" stopColor="#0F172A" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#050811" stopOpacity="0.95" />
          </radialGradient>

          <radialGradient id={`liquid-rad-2-${frame % 60}`} cx={`${cx2}%`} cy={`${cy2}%`} r="65%">
            <stop offset="0%" stopColor={accentColor} stopOpacity="0.6" />
            <stop offset="50%" stopColor={primaryColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </radialGradient>
        </defs>

        <rect width="100%" height="100%" fill={`url(#liquid-rad-1-${frame % 60})`} />
        <rect
          width="100%"
          height="100%"
          fill={`url(#liquid-rad-2-${frame % 60})`}
          style={{ mixBlendMode: "screen" }}
        />
      </svg>

      {/* Sweeping linear chromatic sheen */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(${angleDeg}deg, rgba(255,255,255,0.06) 0%, transparent 60%)`,
          mixBlendMode: "overlay",
        }}
      />

      {noise && <NoiseOverlay opacity={0.06} frame={frame} />}
    </div>
  );
};
