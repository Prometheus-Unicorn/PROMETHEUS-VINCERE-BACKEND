import React from "react";
import { interpolate, spring } from "remotion";
import type { GeometricDraftingOptions } from "./types";

interface GeometricDraftingOverlayProps extends GeometricDraftingOptions {
  frame: number;
  fps: number;
  width?: number;
  height?: number;
}

export const GeometricDraftingOverlay: React.FC<GeometricDraftingOverlayProps> = ({
  frame,
  fps,
  width = 1080,
  height = 1920,
  gridModules = 8,
  showCoordinates = true,
  showBrackets = true,
  showCrosshairs = true,
  accentColor = "#00F0FF",
  textColor = "rgba(255, 255, 255, 0.7)",
  seed = 42,
  metadataLabels,
}) => {
  // Deterministic entrance animation
  const entrance = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 140 },
  });

  const bracketLength = Math.max(16, Math.round(width * 0.035));
  const inset = Math.max(18, Math.round(width * 0.03));
  const innerW = width - inset * 2;
  const innerH = height - inset * 2;

  // Grid line scan animation
  const scanProgress = (frame % (fps * 3)) / (fps * 3);
  const scanY = inset + innerH * scanProgress;

  // Deterministic pseudo-random lat/long from seed
  const latDeg = (34 + ((seed * 17) % 50) * 0.1).toFixed(4);
  const longDeg = (118 + ((seed * 31) % 50) * 0.1).toFixed(4);
  const scaleTag = "1:1.000";
  const dimTag = `${width}x${height}`;
  const secTag = `SEC-${String((seed % 99) + 1).padStart(2, "0")}`;

  const defaultLabels = [
    `LAT ${latDeg}° N / LONG ${longDeg}° W`,
    `SCALE ${scaleTag} · ${dimTag}`,
    `PROMETHEUS DRAFTING ${secTag}`,
    `FRAME ${String(frame).padStart(4, "0")}`,
  ];

  const labelsToRender = metadataLabels && metadataLabels.length > 0 ? metadataLabels : defaultLabels;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        overflow: "hidden",
        zIndex: 20,
        opacity: interpolate(entrance, [0, 1], [0, 1]),
      }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
      >
        {/* Subtle Outer Technical Frame */}
        <rect
          x={inset}
          y={inset}
          width={innerW}
          height={innerH}
          fill="none"
          stroke={accentColor}
          strokeWidth="0.75"
          strokeOpacity="0.25"
          strokeDasharray="4 8"
        />

        {/* 4 Corner Drafting Brackets: ⌜ ⌝ ⌞ ⌟ */}
        {showBrackets && (
          <g stroke={accentColor} strokeWidth="1.5" strokeLinecap="square" fill="none">
            {/* Top-Left ⌜ */}
            <path
              d={`M ${inset} ${inset + bracketLength} L ${inset} ${inset} L ${inset + bracketLength} ${inset}`}
            />
            {/* Top-Right ⌝ */}
            <path
              d={`M ${inset + innerW - bracketLength} ${inset} L ${inset + innerW} ${inset} L ${inset + innerW} ${inset + bracketLength}`}
            />
            {/* Bottom-Left ⌞ */}
            <path
              d={`M ${inset} ${inset + innerH - bracketLength} L ${inset} ${inset + innerH} L ${inset + bracketLength} ${inset + innerH}`}
            />
            {/* Bottom-Right ⌟ */}
            <path
              d={`M ${inset + innerW - bracketLength} ${inset + innerH} L ${inset + innerW} ${inset + innerH} L ${inset + innerW} ${inset + innerH - bracketLength}`}
            />
          </g>
        )}

        {/* Center & Quadrant Crosshairs ＋ */}
        {showCrosshairs && (
          <g stroke={accentColor} strokeWidth="1" strokeOpacity="0.4" fill="none">
            {/* Center Reticle */}
            <path
              d={`M ${width / 2 - 12} ${height / 2} L ${width / 2 + 12} ${height / 2} M ${width / 2} ${height / 2 - 12} L ${width / 2} ${height / 2 + 12}`}
            />
            <circle
              cx={width / 2}
              cy={height / 2}
              r="20"
              stroke={accentColor}
              strokeWidth="0.5"
              strokeDasharray="2 4"
            />

            {/* Quadrant Crosshairs */}
            <path
              d={`M ${width * 0.25 - 6} ${height * 0.25} L ${width * 0.25 + 6} ${height * 0.25} M ${width * 0.25} ${height * 0.25 - 6} L ${width * 0.25} ${height * 0.25 + 6}`}
            />
            <path
              d={`M ${width * 0.75 - 6} ${height * 0.25} L ${width * 0.75 + 6} ${height * 0.25} M ${width * 0.75} ${height * 0.25 - 6} L ${width * 0.75} ${height * 0.25 + 6}`}
            />
            <path
              d={`M ${width * 0.25 - 6} ${height * 0.75} L ${width * 0.25 + 6} ${height * 0.75} M ${width * 0.25} ${height * 0.75 - 6} L ${width * 0.25} ${height * 0.75 + 6}`}
            />
            <path
              d={`M ${width * 0.75 - 6} ${height * 0.75} L ${width * 0.75 + 6} ${height * 0.75} M ${width * 0.75} ${height * 0.75 - 6} L ${width * 0.75} ${height * 0.75 + 6}`}
            />
          </g>
        )}

        {/* Edge Tick Marks along X and Y axes */}
        <g stroke={accentColor} strokeWidth="0.75" strokeOpacity="0.35">
          {Array.from({ length: gridModules + 1 }).map((_, i) => {
            const tx = inset + (innerW / gridModules) * i;
            const ty = inset + (innerH / gridModules) * i;
            return (
              <React.Fragment key={`tick-${i}`}>
                {/* Top and bottom ticks */}
                <line x1={tx} y1={inset - 4} x2={tx} y2={inset + 4} />
                <line x1={tx} y1={inset + innerH - 4} x2={tx} y2={inset + innerH + 4} />
                {/* Left and right ticks */}
                <line x1={inset - 4} y1={ty} x2={inset + 4} y2={ty} />
                <line x1={inset + innerW - 4} y1={ty} x2={inset + innerW + 4} y2={ty} />
              </React.Fragment>
            );
          })}
        </g>

        {/* Dynamic Scanning Hairline */}
        <line
          x1={inset}
          y1={scanY}
          x2={inset + innerW}
          y2={scanY}
          stroke={accentColor}
          strokeWidth="0.5"
          strokeOpacity="0.18"
        />
      </svg>

      {/* Technical HUD Metadata Labels */}
      {showCoordinates && (
        <div
          style={{
            position: "absolute",
            top: inset + 8,
            left: inset + bracketLength + 10,
            right: inset + bracketLength + 10,
            display: "flex",
            justifyContent: "space-between",
            fontFamily: "var(--font-mono, 'JetBrains Mono', 'Courier New', monospace)",
            fontSize: "10px",
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: textColor,
          }}
        >
          <span>{labelsToRender[0]}</span>
          <span style={{ color: accentColor }}>{labelsToRender[1]}</span>
        </div>
      )}

      {showCoordinates && (
        <div
          style={{
            position: "absolute",
            bottom: inset + 8,
            left: inset + bracketLength + 10,
            right: inset + bracketLength + 10,
            display: "flex",
            justifyContent: "space-between",
            fontFamily: "var(--font-mono, 'JetBrains Mono', 'Courier New', monospace)",
            fontSize: "10px",
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: textColor,
          }}
        >
          <span>{labelsToRender[2] || `INDEX ${(seed % 9999).toString(16).toUpperCase()}`}</span>
          <span style={{ color: accentColor }}>{labelsToRender[3]}</span>
        </div>
      )}
    </div>
  );
};
