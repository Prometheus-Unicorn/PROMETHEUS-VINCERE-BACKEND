/**
 * OriginInkdropSpread - Remotion-native port of the Origin Kit "Inkdrop Spread" preset.
 *
 * Source: S1:804-948
 *
 * Kinematics: Words scale(0) + blur(4px) -> scale(1) + blur(0), stagger radiating FROM CENTER.
 * Center is midpoint of word array. distanceFromCenter determines stagger offset.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { interpolate, spring } from "remotion";

export interface InkdropSpreadProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginInkdropSpread({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: InkdropSpreadProps): React.ReactElement[] {
  const words = text.split(" ");
  const total = words.length;
  if (total === 0) return [];

  const centerIndex = (total - 1) / 2;
  const maxStaggerFrames = Math.max(1, Math.round(0.25 * fps)); // 0.25s max stagger from center to edge

  return words.map((w, idx) => {
    const distanceFromCenter = Math.abs(idx - centerIndex);
    const normalizedDist = total > 1 ? distanceFromCenter / ((total - 1) / 2) : 0;
    
    // offset: center enters first (offset 0), edges enter later
    const wordStaggerOffset = normalizedDist * maxStaggerFrames;

    const springProgress = spring({
      frame: Math.max(0, localFrame - wordStaggerOffset),
      fps,
      config: { stiffness: 200, damping: 28, mass: 1.0 },
    });

    const scale = interpolate(springProgress, [0, 1], [0, 1]);
    const blur = interpolate(springProgress, [0, 1], [4, 0]);
    const opacity = interpolate(springProgress, [0, 0.5, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      transform: `scale(${scale})`,
      filter: blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : undefined,
      opacity,
      marginRight: idx === total - 1 ? 0 : "0.3em",
      willChange: "transform, opacity, filter",
      ...wordPaintStyle,
    };

    return (
      <span key={`ois-word-${idx}`} style={style}>
        {w}
      </span>
    );
  });
}
