import React from "react";
import { interpolate, spring } from "remotion";
import { VisualHelperComponentProps } from "./types";
import { LiquidGlassCard } from "./LiquidGlassCard";

const DIGIT_HEIGHT = 76; // Height of each digit roll box in px

const DigitColumn: React.FC<{
  targetDigit: number;
  progress: number;
  color: string;
}> = ({ targetDigit, progress, color }) => {
  // Animate from 0 to targetDigit with smooth easing
  const animatedDigit = targetDigit * progress;
  const translateY = -animatedDigit * DIGIT_HEIGHT;

  return (
    <div
      style={{
        position: "relative",
        height: `${DIGIT_HEIGHT}px`,
        width: "42px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          transform: `translateY(${translateY}px)`,
          willChange: "transform",
        }}
      >
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((digit) => (
          <div
            key={digit}
            style={{
              height: `${DIGIT_HEIGHT}px`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: '"Anton", "Montserrat", sans-serif',
              fontSize: "64px",
              fontWeight: 900,
              lineHeight: `${DIGIT_HEIGHT}px`,
              color,
              userSelect: "none",
            }}
          >
            {digit}
          </div>
        ))}
      </div>
    </div>
  );
};

export const MotionNumberHelper: React.FC<VisualHelperComponentProps> = ({
  helper,
  frame,
  fps,
  palette,
}) => {
  const brandPrimary = palette?.hero_color || helper.primaryColor || "#A855F7";
  const brandAccent = palette?.accent_border || helper.accentColor || "#38BDF8";

  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 130 },
  });

  const targetValue = helper.targetValue ?? helper.value ?? 100;
  const countSpring = spring({
    frame: Math.max(0, frame - 3),
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  // Format the target value string to determine layout structure
  const decimals = helper.decimals ?? (targetValue % 1 !== 0 ? 1 : 0);
  const formattedTarget = targetValue.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  const prefix = helper.prefix || "";
  const suffix = helper.suffix || "";

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "600px",
        transform: `scale(${interpolate(entrance, [0, 1], [0.88, 1.0])}) translateY(${interpolate(entrance, [0, 1], [25, 0])}px)`,
        opacity: entrance,
      }}
    >
      <LiquidGlassCard
        frame={frame}
        fps={fps}
        borderRadius="28px"
        glowColor="rgba(56, 189, 248, 0.3)"
        borderColor="rgba(255, 255, 255, 0.22)"
        style={{ padding: "20px 28px" }}
      >
        {/* Title Label */}
        {helper.title && (
          <div
            style={{
              fontFamily: '"Montserrat", sans-serif',
              fontSize: "13px",
              fontWeight: 900,
              letterSpacing: "0.22em",
              textTransform: "uppercase",
              color: brandAccent,
              marginBottom: "8px",
              textShadow: `0 0 12px ${brandAccent}88`,
              textAlign: "center",
            }}
          >
            {helper.title}
          </div>
        )}

        {/* Rolling Odometer Display */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "2px",
          }}
        >
          {/* Prefix (e.g. $, +) */}
          {prefix && (
            <span
              style={{
                fontFamily: '"Anton", sans-serif',
                fontSize: "56px",
                fontWeight: 900,
                color: brandAccent,
                marginRight: "4px",
                textShadow: `0 0 16px ${brandAccent}66`,
              }}
            >
              {prefix}
            </span>
          )}

          {/* Digits and punctuation */}
          {formattedTarget.split("").map((char, idx) => {
            const isDigit = /\d/.test(char);
            if (!isDigit) {
              return (
                <span
                  key={`punct-${idx}`}
                  style={{
                    fontFamily: '"Anton", sans-serif',
                    fontSize: "56px",
                    fontWeight: 900,
                    color: "#FFFFFF",
                    lineHeight: `${DIGIT_HEIGHT}px`,
                    padding: "0 2px",
                  }}
                >
                  {char}
                </span>
              );
            }

            const targetDigit = parseInt(char, 10);
            return (
              <DigitColumn
                key={`digit-${idx}`}
                targetDigit={targetDigit}
                progress={countSpring}
                color="#FFFFFF"
              />
            );
          })}

          {/* Suffix (e.g. %, X, users) */}
          {suffix && (
            <span
              style={{
                fontFamily: '"Anton", "Montserrat", sans-serif',
                fontSize: "44px",
                fontWeight: 900,
                color: brandPrimary,
                marginLeft: "6px",
                textShadow: `0 0 16px ${brandPrimary}66`,
              }}
            >
              {suffix}
            </span>
          )}
        </div>

        {/* Subtitle description */}
        {helper.subtitle && (
          <div
            style={{
              fontFamily: '"Montserrat", sans-serif',
              fontSize: "14px",
              fontWeight: 700,
              color: "#94A3B8",
              textAlign: "center",
              marginTop: "8px",
            }}
          >
            {helper.subtitle}
          </div>
        )}
      </LiquidGlassCard>
    </div>
  );
};
