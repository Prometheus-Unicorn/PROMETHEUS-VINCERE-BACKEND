/**
 * OriginMatrixLetterRain
 *
 * Source: S1:2044-2205
 *
 * Kinematics: Column decode rain. Cycles through ASCII chars before landing on the correct char.
 *
 * Remotion compliance:
 * - Pure function returning elements.
 * - Zero browser APIs.
 */

import React from "react";

export interface MatrixLetterRainProps {
  color: string;
  text: string;
  localFrame: number;
  fps: number;
  totalFrames: number;
  wordPaintStyle: React.CSSProperties;
}

const DECODE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&';

export function renderOriginMatrixLetterRain({
  color,
  text,
  localFrame,
  fps,
  totalFrames,
  wordPaintStyle,
}: MatrixLetterRainProps): React.ReactElement[] {
  const chars = Array.from(text);
  const total = chars.length;
  if (total === 0) return [];

  // Duration for the decode phase based on the spec
  // Intrinsic duration is 1.2s, let's use fps to calculate durationFrames
  const durationFrames = Math.round(1.2 * fps);

  return chars.map((char, idx) => {
    // Math.floor((i / total) * durationFrames * 0.85)
    const decodeFrame = Math.floor((idx / total) * durationFrames * 0.85);
    const isDecoded = localFrame >= decodeFrame;

    let displayChar = char;
    let charColor = color;

    if (!isDecoded && char !== ' ') {
      // cycle through random ASCII chars
      displayChar = DECODE_CHARS[(idx * 17 + localFrame * 3) % DECODE_CHARS.length];
      // Green tint during decode phase
      charColor = '#00FF41'; // classic matrix green
    }

    const style: React.CSSProperties = {
      display: "inline-block",
      whiteSpace: "pre",
      color: charColor,
      willChange: "color",
      ...wordPaintStyle,
      // Suppress gradient during decode phase if we want it to be green
      ...((wordPaintStyle as any).backgroundImage && !isDecoded
        ? { backgroundImage: "none", WebkitTextFillColor: charColor, WebkitBackgroundClip: "border-box" }
        : {}),
    };

    return (
      <span key={`omlr-char-${idx}`} style={style}>
        {displayChar === " " ? "\u00A0" : displayChar}
      </span>
    );
  });
}
