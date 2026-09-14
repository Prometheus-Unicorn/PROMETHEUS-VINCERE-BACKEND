/**
 * OriginShinyPill
 *
 * Source: Expansion Plan #13
 *
 * Kinematics: Pill badge + specular shine sweep.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";
import { spring, interpolate } from "remotion";

export interface ShinyPillProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

export function renderOriginShinyPill({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: ShinyPillProps): React.ReactElement[] {
  if (text.length === 0) return [];

  const entrance = spring({
    frame: localFrame,
    fps,
    config: { stiffness: 150, damping: 18 },
  });

  const scale = interpolate(entrance, [0, 1], [0.8, 1]);
  const opacity = interpolate(entrance, [0, 1], [0, 1]);

  // Sweep from left to right (-100% to 200%)
  const shineProgress = interpolate(localFrame, [10, 50], [-100, 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const pillStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "0.2em 0.8em",
    borderRadius: "999px",
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    border: `2px solid ${color}`,
    opacity,
    transform: `scale(${scale.toFixed(2)})`,
    position: "relative",
    overflow: "hidden",
    color,
    willChange: "transform, opacity",
    ...wordPaintStyle,
  };

  const shineStyle: React.CSSProperties = {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: `linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.6) 50%, transparent)`,
    transform: `translateX(${shineProgress.toFixed(1)}%)`,
    pointerEvents: "none",
  };

  return [
    <div key="osp-pill" style={pillStyle}>
      <div style={shineStyle} />
      <span>{text}</span>
    </div>,
  ];
}
