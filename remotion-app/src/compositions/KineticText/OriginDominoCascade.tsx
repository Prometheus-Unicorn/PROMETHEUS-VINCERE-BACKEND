/**
 * OriginDominoCascade
 *
 * Source: Expansion Plan #11
 *
 * Kinematics: Chars fall with chained rotation/bounce.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";

export interface DominoCascadeProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginDominoCascade({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: DominoCascadeProps): React.ReactElement[] {
  const chars = Array.from(text);
  if (chars.length === 0) return [];

  const staggerFrames = Math.max(1, Math.round(0.04 * fps));

  return chars.map((char, i) => {
    const p = spring({
      frame: Math.max(0, localFrame - i * staggerFrames),
      fps,
      config: { stiffness: 180, damping: 14 },
    });

    const rotateY = interpolate(p, [0, 1], [90, 0]);
    const translateZ = interpolate(p, [0, 1], [100, 0]);
    const opacity = interpolate(p, [0, 0.4, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      opacity,
      transform: `perspective(600px) translateZ(${translateZ.toFixed(1)}px) rotateY(${rotateY.toFixed(1)}deg)`,
      transformOrigin: "left center",
      willChange: "transform, opacity",
      ...wordPaintStyle,
    };

    return (
      <span key={`odc-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
