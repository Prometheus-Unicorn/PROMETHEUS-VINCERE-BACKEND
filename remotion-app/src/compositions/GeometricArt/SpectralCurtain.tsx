import React from "react";
import { interpolate } from "remotion";
import type { SpectralCurtainOptions } from "./types";

interface SpectralCurtainProps extends SpectralCurtainOptions {
  frame: number;
  fps: number;
  width?: number;
  height?: number;
}

export const SpectralCurtain: React.FC<SpectralCurtainProps> = ({
  frame,
  fps,
  width = 1080,
  height = 1920,
  curtainDensity = 32,
  curtainLength = 0.65,
  curtainOpacity = 0.55,
  direction = "down",
  chromaticShift = 4,
}) => {
  const slitCount = Math.max(16, Math.min(64, curtainDensity));
  const slitWidth = width / slitCount;
  const time = frame / fps;

  // Slit ribbons
  const slits = Array.from({ length: slitCount }).map((_, i) => {
    const x = i * slitWidth;
    // Deterministic wave phase for each slit
    const phase = Math.sin(time * 2.5 + i * 0.35);
    const length = height * curtainLength * (0.5 + 0.5 * Math.abs(phase));
    const yStart = direction === "up" ? height - length : 0;
    const yEnd = direction === "up" ? height : length;

    return {
      x,
      yStart,
      yEnd,
      length,
      opacity: 0.3 + 0.5 * Math.abs(Math.cos(time * 1.8 + i * 0.2)),
    };
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 16,
        mixBlendMode: "screen",
        opacity: curtainOpacity,
        overflow: "hidden",
      }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
      >
        <defs>
          <linearGradient id="curtain-grad-down" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#A855F7" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#EF3D2F" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="curtain-grad-up" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#A855F7" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#EF3D2F" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Chromatic Red Channel Slits */}
        <g transform={`translate(${-chromaticShift}, 0)`} opacity={0.6}>
          {slits.map((s, i) => (
            <rect
              key={`slit-r-${i}`}
              x={s.x}
              y={s.yStart}
              width={slitWidth * 0.65}
              height={s.length}
              fill="#EF3D2F"
              opacity={s.opacity * 0.5}
            />
          ))}
        </g>

        {/* Main Gradient Curtain Slits */}
        <g>
          {slits.map((s, i) => (
            <rect
              key={`slit-m-${i}`}
              x={s.x}
              y={s.yStart}
              width={slitWidth * 0.8}
              height={s.length}
              fill={direction === "up" ? "url(#curtain-grad-up)" : "url(#curtain-grad-down)"}
              opacity={s.opacity}
            />
          ))}
        </g>

        {/* Chromatic Cyan Channel Slits */}
        <g transform={`translate(${chromaticShift}, 0)`} opacity={0.7}>
          {slits.map((s, i) => (
            <rect
              key={`slit-c-${i}`}
              x={s.x}
              y={s.yStart}
              width={slitWidth * 0.65}
              height={s.length}
              fill="#00F0FF"
              opacity={s.opacity * 0.6}
            />
          ))}
        </g>
      </svg>
    </div>
  );
};
