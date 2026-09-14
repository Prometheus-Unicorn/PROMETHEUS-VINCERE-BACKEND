/**
 * OriginFuzzyNoiseOverlay
 *
 * Source: S1:953-1338
 *
 * CSS-based text-shadow shimmer with deterministic per-frame row offset.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { interpolate } from "remotion";

export interface FuzzyNoiseOverlayProps {
  color: string;
  text: string;
  frame: number;
  fps: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginFuzzyNoiseOverlay({
  color,
  text,
  frame,
  fps,
  wordPaintStyle,
}: FuzzyNoiseOverlayProps): React.ReactElement[] {
  const words = text.split(" ");
  
  // Deterministic per-frame row offset using interpolate(frame % cyclePeriod, [0, cyclePeriod], [-3, 3])
  const cyclePeriod = Math.max(1, Math.round(0.8 * fps)); // 800ms per-cycle
  const progress = frame % cyclePeriod;
  
  const yOffset = interpolate(progress, [0, cyclePeriod], [-3, 3]);

  return words.map((w, idx) => {
    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color: "transparent",
      textShadow: `0px ${yOffset.toFixed(2)}px 2px ${color}`,
      mixBlendMode: "overlay",
      marginRight: idx === words.length - 1 ? 0 : "0.3em",
      ...wordPaintStyle,
    };

    return (
      <span key={`ofno-word-${idx}`} style={style}>
        {w}
      </span>
    );
  });
}
