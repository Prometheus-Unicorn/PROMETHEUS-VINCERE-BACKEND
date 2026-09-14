/**
 * PopcornCharBurst
 *
 * Source: Expansion Plan #15
 *
 * Kinematics: Chars pop from scale 0 with seeded random rotation.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";
import { createSeededRng } from "./origin-helpers";

export interface PopcornCharBurstProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderPopcornCharBurst({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: PopcornCharBurstProps): React.ReactElement[] {
  const chars = Array.from(text);
  if (chars.length === 0) return [];

  const staggerFrames = Math.max(1, Math.round(0.04 * fps));
  const rng = createSeededRng(text);

  return chars.map((char, i) => {
    const p = spring({
      frame: Math.max(0, localFrame - i * staggerFrames),
      fps,
      config: { stiffness: 350, damping: 14, mass: 14 },
    });

    // Seeded random rotation between -180 and 180 degrees
    const maxRot = interpolate(rng(), [0, 1], [-180, 180]);
    // It rotates from maxRot to 0 as it pops in
    const rotateZ = interpolate(p, [0, 1], [maxRot, 0]);
    const scale = interpolate(p, [0, 1], [0, 1]);
    const opacity = interpolate(p, [0, 0.2, 1], [0, 1, 1]);

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color,
      opacity,
      transform: `scale(${scale.toFixed(2)}) rotateZ(${rotateZ.toFixed(1)}deg)`,
      transformOrigin: "center center",
      willChange: "transform, opacity",
      ...wordPaintStyle,
    };

    return (
      <span key={`pcb-char-${i}`} style={style}>
        {char === " " ? "\u00A0" : char}
      </span>
    );
  });
}
