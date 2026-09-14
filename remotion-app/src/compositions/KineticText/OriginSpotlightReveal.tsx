/**
 * OriginSpotlightReveal
 *
 * Source: Expansion Plan #9
 *
 * Kinematics: Radial spotlight mask sweeping across glyphs.
 *
 * Remotion compliance:
 * - Pure function returning an element (wrapper div).
 * - Zero browser APIs.
 */

import React from "react";
import { interpolate, Easing } from "remotion";

export interface SpotlightRevealProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginSpotlightReveal({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: SpotlightRevealProps): React.ReactElement {
  const durationFrames = Math.max(1, Math.round(1.1 * fps)); // 1100ms

  const spotX = interpolate(localFrame, [0, durationFrames], [-20, 120], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  const opacity = interpolate(localFrame, [0, Math.round(0.1 * fps)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const style: React.CSSProperties = {
    display: "inline-block",
    color,
    opacity,
    WebkitMaskImage: `radial-gradient(ellipse 40% 60% at ${spotX}% 50%, black 30%, transparent 100%)`,
    maskImage: `radial-gradient(ellipse 40% 60% at ${spotX}% 50%, black 30%, transparent 100%)`,
    willChange: "mask-image, -webkit-mask-image, opacity",
    ...wordPaintStyle,
  };

  return (
    <div style={style}>
      {text}
    </div>
  );
}
