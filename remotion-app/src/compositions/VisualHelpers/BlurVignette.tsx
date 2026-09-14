import React from "react";

export interface BlurVignetteProps {
  children: React.ReactNode;
  radius?: string;
  blur?: string;
  inset?: string;
  className?: string;
  style?: React.CSSProperties;
}

export const BlurVignette: React.FC<BlurVignetteProps> = ({
  children,
  radius = "24px",
  blur = "12px",
  inset = "16px",
  style = {},
}) => {
  return (
    <div
      style={{
        position: "relative",
        borderRadius: radius,
        overflow: "hidden",
        ...style,
      }}
    >
      {/* Outer blurred perimeter ring */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          pointerEvents: "none",
          zIndex: 2,
          boxShadow: `inset 0 0 ${blur} ${inset} rgba(0, 0, 0, 0.45)`,
          backdropFilter: `blur(${blur})`,
          WebkitBackdropFilter: `blur(${blur})`,
          maskImage: `radial-gradient(ellipse at center, transparent 55%, black 100%)`,
          WebkitMaskImage: `radial-gradient(ellipse at center, transparent 55%, black 100%)`,
        }}
      />
      {children}
    </div>
  );
};
