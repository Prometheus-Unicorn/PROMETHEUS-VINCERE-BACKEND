import React from "react";
import type { DitherPrintOptions } from "./types";

interface DitherPrintEffectProps extends DitherPrintOptions {
  children?: React.ReactNode;
  width?: number;
  height?: number;
}

const PALETTES: Record<string, { ink: string; paper: string }> = {
  cobalt: { ink: "#2446E8", paper: "#F4F4F6" },
  signal: { ink: "#EF3D2F", paper: "#0E1013" },
  mono: { ink: "#101417", paper: "#FAFAFA" },
  cyan: { ink: "#00F0FF", paper: "#0A0E17" },
  electric: { ink: "#A855F7", paper: "#0F0A1C" },
};

// 4x4 Bayer Dither Matrix Thresholds (0-15 normalized to 0.0 - 1.0)
const BAYER_4X4 = [
  [0 / 16, 8 / 16, 2 / 16, 10 / 16],
  [12 / 16, 4 / 16, 14 / 16, 6 / 16],
  [3 / 16, 11 / 16, 1 / 16, 9 / 16],
  [15 / 16, 7 / 16, 13 / 16, 5 / 16],
];

export const DitherPrintEffect: React.FC<DitherPrintEffectProps> = ({
  children,
  algorithm = "bayer4",
  palette = "cobalt",
  cellSize = 6,
  contrast = 1.4,
  invert = false,
  blendMode = "multiply",
  opacity = 0.95,
  width = 1080,
  height = 1920,
}) => {
  const chosenPalette = PALETTES[palette] || PALETTES.cobalt;
  const inkColor = invert ? chosenPalette.paper : chosenPalette.ink;
  const paperColor = invert ? chosenPalette.ink : chosenPalette.paper;

  // Unique filter ID
  const filterId = `dither-filter-${palette}-${algorithm}-${cellSize}`;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: paperColor,
      }}
    >
      {/* SVG Dither & Duotone Shader Filter */}
      <svg width="0" height="0" style={{ position: "absolute", pointerEvents: "none" }}>
        <defs>
          <filter id={filterId} colorInterpolationFilters="sRGB">
            {/* 1. Desaturate to Luminance Grayscale */}
            <feColorMatrix
              type="matrix"
              values="0.2126 0.7152 0.0722 0 0
                      0.2126 0.7152 0.0722 0 0
                      0.2126 0.7152 0.0722 0 0
                      0      0      0      1 0"
              result="grayscale"
            />
            {/* 2. Contrast Amplification */}
            <feComponentTransfer in="grayscale" result="contrast">
              <feFuncR type="linear" slope={contrast} intercept={-(contrast - 1) * 0.5} />
              <feFuncG type="linear" slope={contrast} intercept={-(contrast - 1) * 0.5} />
              <feFuncB type="linear" slope={contrast} intercept={-(contrast - 1) * 0.5} />
            </feComponentTransfer>
          </filter>

          {/* Bayer 4x4 Pattern Raster */}
          <pattern
            id={`bayer-pat-${cellSize}`}
            width={cellSize * 4}
            height={cellSize * 4}
            patternUnits="userSpaceOnUse"
          >
            {BAYER_4X4.map((row, y) =>
              row.map((val, x) => (
                <rect
                  key={`b-${x}-${y}`}
                  x={x * cellSize}
                  y={y * cellSize}
                  width={cellSize}
                  height={cellSize}
                  fill={val > 0.45 ? inkColor : "transparent"}
                  opacity={0.35}
                />
              ))
            )}
          </pattern>
        </defs>
      </svg>

      {/* Filtered Base Content */}
      <div
        style={{
          width: "100%",
          height: "100%",
          filter: `url(#${filterId})`,
          opacity,
        }}
      >
        {children}
      </div>

      {/* Duotone Color Tint Wash */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: inkColor,
          mixBlendMode: blendMode as any,
          pointerEvents: "none",
          opacity: 0.85,
        }}
      />

      {/* Dither Halftone Dot Raster Grid */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='${
            cellSize * 4
          }' height='${cellSize * 4}'><rect width='${cellSize}' height='${cellSize}' fill='${encodeURIComponent(
            inkColor
          )}' opacity='0.4'/><rect x='${cellSize * 2}' y='${
            cellSize * 2
          }' width='${cellSize}' height='${cellSize}' fill='${encodeURIComponent(
            inkColor
          )}' opacity='0.3'/></svg>")`,
          backgroundRepeat: "repeat",
          mixBlendMode: "multiply",
          pointerEvents: "none",
          opacity: 0.65,
        }}
      />

      {/* Fine-art Print Paper Texture / Border Framing */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          boxShadow: `inset 0 0 60px rgba(0, 0, 0, 0.4)`,
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
