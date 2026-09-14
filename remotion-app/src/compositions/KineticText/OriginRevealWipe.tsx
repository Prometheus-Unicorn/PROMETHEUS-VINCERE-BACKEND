/**
 * OriginRevealWipe
 *
 * Source: Expansion Plan #6
 *
 * Kinematics: Directional wipe with a soft feathered edge (CSS gradient mask fade).
 *
 * Remotion compliance:
 * - Pure function returning an element (wrapper div).
 * - Zero browser APIs.
 */

import React from "react";
import { interpolate, Easing } from "remotion";

export interface RevealWipeProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
  children?: React.ReactNode;
}

export function renderOriginRevealWipe({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
  children,
}: RevealWipeProps): React.ReactElement {
  const durationFrames = Math.max(1, Math.round(0.85 * fps)); // 850ms

  const wipeProgress = interpolate(localFrame, [0, durationFrames], [0, 1.1], {
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const style: React.CSSProperties = {
    display: "inline-block",
    color,
    WebkitMaskImage: `linear-gradient(to right, transparent 0%, black ${wipeProgress * 100}%, black 100%)`,
    maskImage: `linear-gradient(to right, transparent 0%, black ${wipeProgress * 100}%, black 100%)`,
    willChange: "mask-image, -webkit-mask-image",
    ...wordPaintStyle,
  };

  return (
    <div style={style}>
      {children || text}
    </div>
  );
}
