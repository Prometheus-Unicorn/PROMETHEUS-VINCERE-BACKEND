/**
 * OriginCinematicZoomBlur
 *
 * Source: Expansion Plan #11
 *
 * Kinematics: Chars scale down from scale(4) and blur(20px) to scale(1) and blur(0).
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";

export interface CinematicZoomBlurProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginCinematicZoomBlur({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: CinematicZoomBlurProps): React.ReactElement[] {
  const chars = Array.from(text);
  if (chars.length === 0) return [];

  const staggerFrames = Math.max(1, Math.round(0.03 * fps));

  return chars.map((char, i) => {
    const p = spring({
      frame: Math.max(0, localFrame - i * staggerFrames),
      fps,
      config: { stiffness: 140, damping: 20 },
    });

    const scale = interpolate(p, [0, 1], [4, 1]);
    const blur = interpolate(p, [0, 1], [20, 0]);
    const opacity = interpolate(p, [0, 0.2, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      opacity,
      transform: `scale(${scale.toFixed(3)})`,
      filter: blur > 0.01 ? `blur(${blur.toFixed(1)}px)` : "none",
      willChange: "transform, filter, opacity",
      ...wordPaintStyle,
    };

    return (
      <span key={`oczb-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
