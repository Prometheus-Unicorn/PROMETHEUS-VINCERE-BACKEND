import React from "react";

export interface NoiseOverlayProps {
  opacity?: number;
  frame?: number;
}

export const NoiseOverlay: React.FC<NoiseOverlayProps> = ({
  opacity = 0.06,
  frame = 0,
}) => {
  // Cycle seed across frames deterministically to simulate film grain jitter
  const seed = (Math.floor(frame / 2) % 10) + 1;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        zIndex: 5,
        opacity,
        mixBlendMode: "overlay",
        overflow: "hidden",
        borderRadius: "inherit",
      }}
    >
      <svg
        width="100%"
        height="100%"
        xmlns="http://www.w3.org/2000/svg"
        style={{ width: "100%", height: "100%" }}
      >
        <filter id={`noise-filter-${seed}`} x="0%" y="0%" width="100%" height="100%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.8"
            numOctaves="3"
            seed={seed}
            result="noisy"
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#noise-filter-${seed})`} />
      </svg>
    </div>
  );
};
