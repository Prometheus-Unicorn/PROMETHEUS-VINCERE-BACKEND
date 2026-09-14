import React from "react";
import { interpolate, spring } from "remotion";
import { VisualHelperComponentProps } from "./types";
import { LiquidGlassCard } from "./LiquidGlassCard";

export const ListicleHelper: React.FC<VisualHelperComponentProps> = ({
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
    config: { damping: 16, stiffness: 120 },
  });

  const items = helper.items || [
    { id: "1", text: "First Key Principle", label: "01", highlight: true },
    { id: "2", text: "Second Strategic Step", label: "02" },
    { id: "3", text: "Compound Growth Outcome", label: "03" },
  ];

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "680px",
        transform: `scale(${interpolate(entrance, [0, 1], [0.92, 1.0])}) translateY(${interpolate(entrance, [0, 1], [20, 0])}px)`,
        opacity: entrance,
      }}
    >
      <LiquidGlassCard
        frame={frame}
        fps={fps}
        borderRadius="24px"
        glowColor="rgba(168, 85, 247, 0.25)"
        borderColor="rgba(255, 255, 255, 0.18)"
        style={{ padding: "20px 22px" }}
      >
        {/* Header Title */}
        {helper.title && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "14px",
            }}
          >
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "999px",
                backgroundColor: brandAccent,
                boxShadow: `0 0 10px ${brandAccent}`,
              }}
            />
            <span
              style={{
                fontFamily: '"Montserrat", sans-serif',
                fontSize: "13px",
                fontWeight: 900,
                letterSpacing: "0.2em",
                textTransform: "uppercase",
                color: "#F8FAFC",
              }}
            >
              {helper.title}
            </span>
          </div>
        )}

        {/* Staggered Item List */}
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {items.map((item, idx) => {
            const itemSpring = spring({
              frame: Math.max(0, frame - idx * 4),
              fps,
              config: { damping: 14, stiffness: 140 },
            });
            const isHighlighted = item.highlight || idx === (helper.activeIndex ?? 0);

            return (
              <div
                key={item.id || `item-${idx}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "14px",
                  padding: "10px 16px",
                  borderRadius: "14px",
                  backgroundColor: isHighlighted
                    ? "rgba(255, 255, 255, 0.12)"
                    : "rgba(15, 23, 42, 0.45)",
                  border: isHighlighted
                    ? `1.5px solid ${brandAccent}`
                    : "1px solid rgba(255, 255, 255, 0.08)",
                  boxShadow: isHighlighted ? `0 0 16px ${brandAccent}44` : "none",
                  transform: `translateX(${interpolate(itemSpring, [0, 1], [-20, 0])}px)`,
                  opacity: itemSpring,
                }}
              >
                {/* Index / Label Pill */}
                <span
                  style={{
                    fontFamily: '"Anton", "Montserrat", sans-serif',
                    fontSize: "22px",
                    fontWeight: 900,
                    color: isHighlighted ? brandAccent : "#94A3B8",
                    minWidth: "28px",
                  }}
                >
                  {item.label || `${idx + 1 < 10 ? `0${idx + 1}` : idx + 1}`}
                </span>

                {/* Item Text */}
                <span
                  style={{
                    fontFamily: '"Montserrat", sans-serif',
                    fontSize: "18px",
                    fontWeight: isHighlighted ? 800 : 600,
                    color: isHighlighted ? "#FFFFFF" : "#CBD5E1",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {item.text}
                </span>
              </div>
            );
          })}
        </div>
      </LiquidGlassCard>
    </div>
  );
};
