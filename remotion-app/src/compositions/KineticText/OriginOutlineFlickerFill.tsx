/**
 * OriginOutlineFlickerFill
 *
 * Source: S1:1345-2043
 *
 * Kinematics: Starts outline-only, flickers independently at staggered frames to solid.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { interpolate } from "remotion";

export interface OutlineFlickerFillProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginOutlineFlickerFill({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: OutlineFlickerFillProps): React.ReactElement[] {
  const chars = Array.from(text);
  
  const flickerWindow = Math.max(1, Math.round(0.6 * fps)); // The window in which flickers happen

  return chars.map((char, idx) => {
    // Deterministic flicker moment for this character
    const flickerFrame = Math.floor((idx * 7 + 13) % flickerWindow);
    
    // Once we pass the flickerFrame, char becomes filled. Before that it is outlined.
    // Let's add a couple of flickers before settling if we want it to be more kinetic, 
    // but the spec just says "rapidly switches to filled at a flicker moment".
    const isFilled = localFrame >= flickerFrame;

    // Optional shake: small translateX oscillation
    // Only shake if it's currently flickering (e.g. within a few frames of flickerFrame)
    let shakeX = 0;
    if (localFrame >= flickerFrame && localFrame < flickerFrame + 6) {
      const shakeProgress = localFrame % 6;
      shakeX = interpolate(shakeProgress, [0, 1, 2, 3, 4, 5, 6], [0, -1, 1, -0.5, 0.5, -1, 0]);
    }

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color: isFilled ? color : "transparent",
      WebkitTextStroke: isFilled ? "none" : `1px ${color}`,
      transform: `translateX(${shakeX}px)`,
      willChange: "transform, color",
      ...wordPaintStyle,
      // If filled and wordPaintStyle has background clip for text, we retain it.
      // If outlined, we must disable background clip otherwise it might fill the stroke.
      ...((wordPaintStyle as any).backgroundImage && !isFilled
        ? { backgroundImage: "none", WebkitBackgroundClip: "border-box", WebkitTextFillColor: "transparent" }
        : {}),
    };

    return (
      <span key={`ooff-char-${idx}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
