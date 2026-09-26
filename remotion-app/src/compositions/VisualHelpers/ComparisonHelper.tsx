import React from "react";
import { interpolate, spring } from "remotion";
import { VisualHelperComponentProps } from "./types";
import { LiquidGlassCard } from "./LiquidGlassCard";
import { LiquidImageRipple } from "./LiquidImageRipple";

export const ComparisonHelper: React.FC<VisualHelperComponentProps> = ({
  helper,
  frame,
  fps,
  palette,
}) => {
  const brandPrimary = palette?.hero_color || helper.primaryColor || "#A855F7";
  const brandAccent = palette?.accent_border || helper.accentColor || "#38BDF8";

  // Spring entrance for the entire comparison card
  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 120 },
  });

  // Animated divider progress (slides smoothly from 20% to 50% or explicit splitRatio)
  const targetSplit = (helper.splitRatio ?? 0.5) * 100;
  const dividerSpring = spring({
    frame: Math.max(0, frame - 5),
    fps,
    config: { damping: 18, stiffness: 90 },
  });
  const splitPercent = interpolate(dividerSpring, [0, 1], [15, targetSplit]);

  const beforeLabel = helper.beforeLabel || "BEFORE";
  const beforeValue = helper.beforeValue || "Previous Baseline";
  const afterLabel = helper.afterLabel || "AFTER";
  const afterValue = helper.afterValue || "High-Impact System";

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "680px",
        transform: `scale(${interpolate(entrance, [0, 1], [0.9, 1.0])}) translateY(${interpolate(entrance, [0, 1], [25, 0])}px)`,
        opacity: entrance,
      }}
    >
      <LiquidGlassCard
        frame={frame}
        fps={fps}
        borderRadius="24px"
        glowColor="rgba(168, 85, 247, 0.3)"
        borderColor="rgba(255, 255, 255, 0.2)"
        style={{ padding: "20px 24px" }}
      >
        {/* Header Title / Badge */}
        {helper.title && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "16px",
            }}
          >
            <span
              style={{
                fontFamily: '"Montserrat", sans-serif',
                fontSize: "14px",
                fontWeight: 900,
                letterSpacing: "0.2em",
                textTransform: "uppercase",
                color: brandAccent,
                textShadow: `0 0 12px ${brandAccent}66`,
              }}
            >
              {helper.title}
            </span>
            <span
              style={{
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                padding: "3px 8px",
                borderRadius: "4px",
                background: "rgba(255, 255, 255, 0.06)",
                color: "#94A3B8",
                border: "1px solid rgba(255, 255, 255, 0.1)",
              }}
            >
              CONTRAST
            </span>
          </div>
        )}

        {/* Split Comparison Window */}
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "140px",
            borderRadius: "16px",
            overflow: "hidden",
            backgroundColor: "rgba(10, 15, 26, 0.85)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
          }}
        >
          {/* Layer A: Before Pane (Left Side) */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              padding: "0 24px",
              backgroundColor: "rgba(15, 23, 42, 0.75)",
            }}
          >
            <span
              style={{
                fontFamily: '"Montserrat", "Inter", sans-serif',
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.14em",
                color: "#64748B",
                marginBottom: "6px",
                textTransform: "uppercase",
              }}
            >
              {beforeLabel}
            </span>
            <span
              style={{
                fontFamily: '"Montserrat", "Inter", sans-serif',
                fontSize: "22px",
                fontWeight: 700,
                color: "#94A3B8",
                letterSpacing: "-0.01em",
              }}
            >
              {beforeValue}
            </span>
          </div>

          {/* Layer B: After Pane (Right Side Revealed by Clip Path) */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              clipPath: `polygon(${splitPercent}% 0, 100% 0, 100% 100%, ${splitPercent}% 100%)`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "flex-end",
              padding: "0 24px",
              background: `linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(${brandPrimary}, 0.2) 100%)`,
            }}
          >
            <span
              style={{
                fontFamily: '"Montserrat", "Inter", sans-serif',
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.14em",
                color: brandAccent,
                marginBottom: "6px",
                textTransform: "uppercase",
              }}
            >
              {afterLabel}
            </span>
            <span
              style={{
                fontFamily: '"Montserrat", "Inter", sans-serif',
                fontSize: "24px",
                fontWeight: 800,
                color: "#FFFFFF",
                letterSpacing: "-0.01em",
                textShadow: `0 0 16px ${brandAccent}66`,
              }}
            >
              {afterValue}
            </span>
          </div>

          {/* Sleek Hairline Split Divider Line */}
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: `${splitPercent}%`,
              width: "1.5px",
              transform: "translateX(-50%)",
              background: "linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.9) 50%, rgba(255, 255, 255, 0.1) 100%)",
              boxShadow: `0 0 8px ${brandAccent}88`,
              zIndex: 10,
            }}
          >
            {/* Minimal Center Pill Indicator */}
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: "18px",
                height: "18px",
                borderRadius: "4px",
                backgroundColor: "#0F172A",
                border: "1px solid rgba(255, 255, 255, 0.3)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#94A3B8",
                fontSize: "9px",
                letterSpacing: "-0.05em",
              }}
            >
              ||
            </div>
          </div>
        </div>
      </LiquidGlassCard>
    </div>
  );
};
