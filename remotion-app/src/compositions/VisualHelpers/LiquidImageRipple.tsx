import React from "react";

export interface LiquidImageRippleProps {
  children: React.ReactNode;
  frame?: number;
  fps?: number;
  amplitude?: number;
  frequency?: number;
  borderRadius?: string;
  style?: React.CSSProperties;
}

export const LiquidImageRipple: React.FC<LiquidImageRippleProps> = ({
  children,
  frame = 0,
  fps = 30,
  amplitude = 12,
  frequency = 0.02,
  borderRadius = "20px",
  style = {},
}) => {
  const time = frame / fps;
  const filterId = `liquid-ripple-${frame % 30}`;

  // Sinusoidal wave ripple modulation
  const scale = amplitude * (1 + 0.3 * Math.sin(time * 3));
  const baseFreq = frequency * (1 + 0.15 * Math.cos(time * 2.2));

  return (
    <div
      style={{
        position: "relative",
        borderRadius,
        overflow: "hidden",
        ...style,
      }}
    >
      <svg
        style={{
          position: "absolute",
          width: 0,
          height: 0,
          pointerEvents: "none",
        }}
      >
        <defs>
          <filter
            id={filterId}
            x="-10%"
            y="-10%"
            width="120%"
            height="120%"
            filterUnits="objectBoundingBox"
          >
            <feTurbulence
              type="fractalNoise"
              baseFrequency={`${baseFreq.toFixed(4)} ${(baseFreq * 1.5).toFixed(4)}`}
              numOctaves="2"
              result="ripple"
            />
            <feDisplacementMap
              in="SourceGraphic"
              in2="ripple"
              scale={scale.toFixed(1)}
              xChannelSelector="R"
              yChannelSelector="G"
            />
          </filter>
        </defs>
      </svg>

      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius,
          filter: `url(#${filterId})`,
        }}
      >
        {children}
      </div>
    </div>
  );
};
