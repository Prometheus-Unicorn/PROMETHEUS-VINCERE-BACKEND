import React from "react";
import { interpolate, spring } from "remotion";
import { VisualHelperComponentProps } from "./types";
import { LiquidGlassCard } from "./LiquidGlassCard";
import { LiquidMeshGradient } from "./LiquidMeshGradient";

const renderHelperIcon = (icon?: string, color: string = "#38BDF8") => {
  switch (icon) {
    case "star":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill={color}>
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      );
    case "zap":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill={color}>
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
      );
    case "check":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      );
    case "alert":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      );
    case "flame":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill={color}>
          <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
        </svg>
      );
    case "shield":
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      );
    case "target":
    default:
      return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="6" />
          <circle cx="12" cy="12" r="2" fill={color} />
        </svg>
      );
  }
};

export const CalloutBadgeHelper: React.FC<VisualHelperComponentProps> = ({
  helper,
  frame,
  fps,
  palette,
}) => {
  const brandPrimary = palette?.hero_color || helper.primaryColor || "#A855F7";
  const brandAccent = palette?.accent_border || helper.accentColor || "#38BDF8";

  // Slide entrance from right with spring bounce
  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 130 },
  });

  const title = helper.title || "KEY TAKEAWAY";
  const subtitle = helper.subtitle;
  const badge = helper.badge || "PROMETHEUS ESSENTIAL";
  const texture = helper.texture || "liquid_glass";

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "600px",
        transform: `translateX(${interpolate(entrance, [0, 1], [60, 0])}px) scale(${interpolate(entrance, [0, 1], [0.92, 1.0])})`,
        opacity: entrance,
      }}
    >
      <LiquidGlassCard
        frame={frame}
        fps={fps}
        borderRadius="24px"
        glowColor="rgba(168, 85, 247, 0.3)"
        borderColor="rgba(255, 255, 255, 0.22)"
        style={{ padding: "18px 24px", position: "relative" }}
      >
        {texture === "mesh_gradient" && (
          <LiquidMeshGradient
            frame={frame}
            fps={fps}
            primaryColor={brandPrimary}
            accentColor={brandAccent}
            opacity={0.35}
          />
        )}

        <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
          {/* Icon Badge */}
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "16px",
              backgroundColor: "rgba(15, 23, 42, 0.8)",
              border: `1.5px solid ${brandAccent}`,
              boxShadow: `0 0 16px ${brandAccent}66`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            {renderHelperIcon(helper.icon, brandAccent)}
          </div>

          {/* Text Content */}
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            {badge && (
              <span
                style={{
                  fontFamily: '"Montserrat", sans-serif',
                  fontSize: "11px",
                  fontWeight: 900,
                  letterSpacing: "0.2em",
                  textTransform: "uppercase",
                  color: brandAccent,
                  textShadow: `0 0 10px ${brandAccent}88`,
                }}
              >
                {badge}
              </span>
            )}

            <span
              style={{
                fontFamily: '"Anton", "Montserrat", sans-serif',
                fontSize: "26px",
                fontWeight: 900,
                color: "#FFFFFF",
                letterSpacing: "-0.01em",
                lineHeight: 1.1,
              }}
            >
              {title}
            </span>

            {subtitle && (
              <span
                style={{
                  fontFamily: '"Montserrat", sans-serif',
                  fontSize: "15px",
                  fontWeight: 600,
                  color: "#CBD5E1",
                  lineHeight: 1.3,
                  marginTop: "2px",
                }}
              >
                {subtitle}
              </span>
            )}
          </div>
        </div>
      </LiquidGlassCard>
    </div>
  );
};
