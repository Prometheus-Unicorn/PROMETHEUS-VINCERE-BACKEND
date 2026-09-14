import React from "react";
import { interpolate } from "remotion";
import { NoiseOverlay } from "./NoiseOverlay";

export interface LiquidGlassCardProps {
  children: React.ReactNode;
  frame?: number;
  fps?: number;
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  glowColor?: string;
  borderColor?: string;
  noise?: boolean;
  style?: React.CSSProperties;
}

export const LiquidGlassCard: React.FC<LiquidGlassCardProps> = ({
  children,
  frame = 0,
  fps = 30,
  width = "auto",
  height = "auto",
  borderRadius = "28px",
  glowColor = "rgba(168, 85, 247, 0.35)",
  borderColor = "rgba(255, 255, 255, 0.25)",
  noise = true,
  style = {},
}) => {
  // Deterministic subtle liquid wave breathing
  const time = frame / fps;
  const displacementScale = 160 + 40 * Math.sin(time * 2.5);
  const baseFreqX = 0.003 + 0.001 * Math.sin(time * 1.8);
  const baseFreqY = 0.007 + 0.001 * Math.cos(time * 1.8);

  // Specular shine sweep across glass face (runs once every 90 frames)
  const shineProgress = interpolate((frame % 90), [0, 40], [-100, 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const filterId = `liquid-glass-blur-${Math.floor(frame % 30)}`;

  return (
    <div
      style={{
        position: "relative",
        borderRadius,
        width,
        height,
        boxSizing: "border-box",
        overflow: "hidden",
        backgroundColor: "rgba(18, 24, 38, 0.65)",
        border: `1.5px solid ${borderColor}`,
        boxShadow: `0 8px 32px rgba(0, 0, 0, 0.4), 0 0 24px ${glowColor}`,
        ...style,
      }}
    >
      {/* SVG Liquid Distortion Filter */}
      <svg
        style={{
          position: "absolute",
          width: 0,
          height: 0,
          pointerEvents: "none",
        }}
      >
        <defs>
          <filter
            id={filterId}
            x="0%"
            y="0%"
            width="100%"
            height="100%"
            filterUnits="objectBoundingBox"
          >
            <feTurbulence
              type="fractalNoise"
              baseFrequency={`${baseFreqX.toFixed(5)} ${baseFreqY.toFixed(5)}`}
              numOctaves="1"
              result="turbulence"
            />
            <feDisplacementMap
              in="SourceGraphic"
              in2="turbulence"
              scale={displacementScale.toFixed(1)}
              xChannelSelector="R"
              yChannelSelector="G"
            />
          </filter>
        </defs>
      </svg>

      {/* Bend Layer (Liquid Refraction + Backdrop Blur) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius,
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          filter: `url(#${filterId})`,
          zIndex: 0,
        }}
      />

      {/* Edge Bevel Layer (Inner Highlights and Specular Chamfers) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius,
          pointerEvents: "none",
          zIndex: 1,
          boxShadow:
            "inset 2px 2px 3px 0 rgba(255, 255, 255, 0.4), inset -2px -2px 3px 0 rgba(255, 255, 255, 0.2)",
        }}
      />

      {/* Specular Shine Sweep Highlight */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "60%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 2,
          background:
            "linear-gradient(105deg, transparent 20%, rgba(255, 255, 255, 0.22) 50%, transparent 80%)",
          transform: `translateX(${shineProgress}%) skewX(-20deg)`,
        }}
      />

      {/* Organic Noise Texture */}
      {noise && <NoiseOverlay opacity={0.05} frame={frame} />}

      {/* Card Content Stage */}
      <div
        style={{
          position: "relative",
          zIndex: 3,
          width: "100%",
          height: "100%",
        }}
      >
        {children}
      </div>
    </div>
  );
};
