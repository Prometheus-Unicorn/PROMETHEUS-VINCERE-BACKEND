/**
 * OriginRippleWave
 *
 * Source: Expansion Plan #14
 *
 * Kinematics: Continuous per-char sine y-wave (idle motion during hold).
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { interpolate } from "remotion";

export interface RippleWaveProps {
  color: string;
  text: string;
  frame: number;
  fps: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginRippleWave({
  color,
  text,
  frame,
  fps,
  wordPaintStyle,
}: RippleWaveProps): React.ReactElement[] {
  const chars = Array.from(text);
  if (chars.length === 0) return [];

  // Wave speed relative to fps
  const frequency = 2 * Math.PI / (1.5 * fps); // 1.5 seconds per wave cycle

  return chars.map((char, i) => {
    // Phase offset per character
    const phase = i * 0.4;
    const yOffset = Math.sin(frame * frequency - phase) * 8; // ±8px ripple

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      transform: `translateY(${yOffset.toFixed(2)}px)`,
      willChange: "transform",
      ...wordPaintStyle,
    };

    return (
      <span key={`orw-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
