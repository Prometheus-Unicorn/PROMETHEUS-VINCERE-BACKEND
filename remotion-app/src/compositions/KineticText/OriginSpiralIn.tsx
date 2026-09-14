/**
 * OriginSpiralIn
 *
 * Source: Expansion Plan #10
 *
 * Kinematics: Chars spiral along arc into place.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";

export interface SpiralInProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginSpiralIn({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: SpiralInProps): React.ReactElement[] {
  const chars = Array.from(text);
  const total = chars.length;
  if (total === 0) return [];

  const startRadius = 80;
  const startAngle = -Math.PI / 2;
  const staggerFrames = Math.max(1, Math.round(0.04 * fps));

  return chars.map((char, i) => {
    const p = spring({
      frame: Math.max(0, localFrame - i * staggerFrames),
      fps,
      config: { stiffness: 180, damping: 22 },
    });

    const r = startRadius * (1 - p);
    const theta = startAngle + (i / total) * 2 * Math.PI * (1 - p);

    const x = r * Math.cos(theta);
    const y = r * Math.sin(theta);
    const opacity = interpolate(p, [0, 0.5, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      opacity,
      transform: `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px)`,
      willChange: "transform, opacity",
      ...wordPaintStyle,
    };

    return (
      <span key={`osi-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
