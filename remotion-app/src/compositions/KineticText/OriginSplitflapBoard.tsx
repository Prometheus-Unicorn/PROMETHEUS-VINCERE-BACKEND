/**
 * OriginSplitflapBoard
 *
 * Source: Expansion Plan #13
 *
 * Kinematics: Flaps rotate around X axis (rotateX from 90 to 0).
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";

export interface SplitflapBoardProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginSplitflapBoard({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: SplitflapBoardProps): React.ReactElement[] {
  const chars = Array.from(text);
  if (chars.length === 0) return [];

  const staggerFrames = Math.max(1, Math.round(0.04 * fps));

  return chars.map((char, i) => {
    const p = spring({
      frame: Math.max(0, localFrame - i * staggerFrames),
      fps,
      config: { stiffness: 200, damping: 20 },
    });

    const rotateX = interpolate(p, [0, 1], [90, 0]);
    const opacity = interpolate(p, [0, 0.3, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      opacity,
      transform: `perspective(400px) rotateX(${rotateX.toFixed(1)}deg)`,
      transformOrigin: "center center",
      willChange: "transform, opacity",
      ...wordPaintStyle,
    };

    return (
      <span key={`osb-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
