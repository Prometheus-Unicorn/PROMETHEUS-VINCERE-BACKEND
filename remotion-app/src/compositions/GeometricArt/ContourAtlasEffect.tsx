import React from "react";
import type { ContourAtlasOptions } from "./types";

interface ContourAtlasEffectProps extends ContourAtlasOptions {
  frame: number;
  fps: number;
  width?: number;
  height?: number;
}

// Deterministic pseudo-random float generator from seed
function pseudoRandom(seed: number): number {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
}

export const ContourAtlasEffect: React.FC<ContourAtlasEffectProps> = ({
  frame,
  fps,
  width = 1080,
  height = 1920,
  levels = 12,
  opacity = 0.65,
  drift = 16,
  style = "topographic",
  strokeColor = "rgba(0, 240, 255, 0.4)",
  seed = 101,
}) => {
  // Deterministic time drift
  const timeSec = frame / fps;
  const driftPhase = timeSec * 0.8;

  // Generate deterministic isocontour loops or flowlines
  const contours = Array.from({ length: levels }).map((_, i) => {
    const levelRatio = (i + 1) / (levels + 1);
    const radiusX = (width * 0.42 * levelRatio);
    const radiusY = (height * 0.38 * levelRatio);
    const centerX = width / 2 + Math.sin(driftPhase + i * 0.6) * drift;
    const centerY = height / 2 + Math.cos(driftPhase + i * 0.4) * drift;

    // Create 8-point smooth closed contour path with undulations
    const pointCount = 10;
    const points: Array<{ x: number; y: number }> = [];

    for (let p = 0; p < pointCount; p++) {
      const angle = (p / pointCount) * Math.PI * 2;
      const noiseVal = pseudoRandom(seed + i * 19 + p * 7);
      const wave = Math.sin(angle * 3 + driftPhase + i) * 22 * (1 - levelRatio * 0.4);
      const rX = radiusX + (noiseVal - 0.5) * 36 + wave;
      const rY = radiusY + (noiseVal - 0.5) * 48 + wave;

      const px = centerX + Math.cos(angle) * rX;
      const py = centerY + Math.sin(angle) * rY;
      points.push({ x: px, y: py });
    }

    // Build smooth SVG cubic bezier path
    let d = `M ${points[0].x.toFixed(1)} ${points[0].y.toFixed(1)}`;
    for (let p = 0; p < pointCount; p++) {
      const curr = points[p];
      const next = points[(p + 1) % pointCount];
      const nextNext = points[(p + 2) % pointCount];
      const cp1x = curr.x + (next.x - points[(p - 1 + pointCount) % pointCount].x) * 0.18;
      const cp1y = curr.y + (next.y - points[(p - 1 + pointCount) % pointCount].y) * 0.18;
      const cp2x = next.x - (nextNext.x - curr.x) * 0.18;
      const cp2y = next.y - (nextNext.y - curr.y) * 0.18;
      d += ` C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${next.x.toFixed(1)} ${next.y.toFixed(1)}`;
    }
    d += " Z";

    // Elevation label position
    const labelX = points[0].x;
    const labelY = points[0].y;
    const elevationMeters = Math.round(150 + i * 85);

    return {
      d,
      labelX,
      labelY,
      elevation: `+${elevationMeters}m`,
      isMajorIndex: i % 3 === 0,
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
        zIndex: 15,
        opacity,
      }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
      >
        {contours.map((c, i) => (
          <React.Fragment key={`contour-${i}`}>
            <path
              d={c.d}
              fill="none"
              stroke={strokeColor}
              strokeWidth={c.isMajorIndex ? "1.2" : "0.6"}
              strokeDasharray={c.isMajorIndex ? "none" : "4 6"}
              strokeOpacity={c.isMajorIndex ? 0.8 : 0.45}
            />
            {/* Major index elevation text along the contour */}
            {c.isMajorIndex && (
              <text
                x={c.labelX + 8}
                y={c.labelY - 4}
                fill={strokeColor}
                fontFamily="var(--font-mono, 'JetBrains Mono', monospace)"
                fontSize="9"
                letterSpacing="0.12em"
                opacity={0.7}
              >
                ISO {c.elevation}
              </text>
            )}
          </React.Fragment>
        ))}
      </svg>
    </div>
  );
};
