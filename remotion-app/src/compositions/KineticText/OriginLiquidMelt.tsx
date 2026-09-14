/**
 * OriginLiquidMelt
 *
 * Source: Expansion Plan #12
 *
 * Kinematics: Vertical stretch down with heavy blur.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";

export interface LiquidMeltProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginLiquidMelt({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: LiquidMeltProps): React.ReactElement[] {
  const chars = Array.from(text);
  if (chars.length === 0) return [];

  const staggerFrames = Math.max(1, Math.round(0.04 * fps));

  return chars.map((char, i) => {
    const p = spring({
      frame: Math.max(0, localFrame - i * staggerFrames),
      fps,
      config: { stiffness: 160, damping: 25 },
    });

    const scaleY = interpolate(p, [0, 1], [3, 1]);
    const translateY = interpolate(p, [0, 1], [-50, 0]);
    const blur = interpolate(p, [0, 1], [15, 0]);
    const opacity = interpolate(p, [0, 0.3, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      opacity,
      transform: `translateY(${translateY.toFixed(1)}px) scaleY(${scaleY.toFixed(2)})`,
      filter: blur > 0.01 ? `blur(${blur.toFixed(1)}px)` : "none",
      willChange: "transform, filter, opacity",
      ...wordPaintStyle,
    };

    return (
      <span key={`olm-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
