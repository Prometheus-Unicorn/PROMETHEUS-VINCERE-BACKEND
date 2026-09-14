import React from "react";
import { interpolate, spring } from "remotion";
import type { GeometricContactSheetProps } from "./types";

export const GeometricContactSheet: React.FC<GeometricContactSheetProps> = ({
  images,
  layout = "asymmetric_hero",
  frame,
  fps,
  durationInFrames,
  accentColor = "#00F0FF",
  coordinates,
  showDraftingMarks = true,
}) => {
  const safeImages = images.length > 0 ? images : ["/fallback-1.jpg", "/fallback-2.jpg"];
  const safeCoords = coordinates || [];

  // Entrance spring animation
  const progress = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 120 },
  });

  const gap = 12;
  const padding = 24;

  // Determine sub-panes based on layout and image count
  const renderPanes = () => {
    if (layout === "split_duo" || (!layout && safeImages.length === 2)) {
      return (
        <div
          style={{
            display: "grid",
            gridTemplateRows: "1fr 1fr",
            gap: `${gap}px`,
            width: "100%",
            height: "100%",
          }}
        >
          {safeImages.slice(0, 2).map((img, idx) => (
            <div
              key={`pane-${idx}`}
              style={{
                position: "relative",
                width: "100%",
                height: "100%",
                overflow: "hidden",
                border: `1px solid ${accentColor}44`,
                transform: `scale(${interpolate(progress, [0, 1], [0.96, 1])})`,
              }}
            >
              <img src={img} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              {showDraftingMarks && (
                <div
                  style={{
                    position: "absolute",
                    top: 8,
                    left: 10,
                    fontFamily: "var(--font-mono, monospace)",
                    fontSize: "10px",
                    color: accentColor,
                    backgroundColor: "rgba(0, 0, 0, 0.6)",
                    padding: "2px 6px",
                    letterSpacing: "0.1em",
                  }}
                >
                  ⌜ {safeCoords[idx] || `PANE-0${idx + 1}`} ⌟
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }

    if (layout === "quad_grid" || (!layout && safeImages.length >= 4)) {
      return (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gridTemplateRows: "1fr 1fr",
            gap: `${gap}px`,
            width: "100%",
            height: "100%",
          }}
        >
          {safeImages.slice(0, 4).map((img, idx) => (
            <div
              key={`pane-${idx}`}
              style={{
                position: "relative",
                width: "100%",
                height: "100%",
                overflow: "hidden",
                border: `1px solid ${accentColor}44`,
                transform: `scale(${interpolate(progress, [0, 1], [0.94, 1])})`,
              }}
            >
              <img src={img} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              {showDraftingMarks && (
                <div
                  style={{
                    position: "absolute",
                    bottom: 8,
                    right: 10,
                    fontFamily: "var(--font-mono, monospace)",
                    fontSize: "9px",
                    color: "#FFFFFF",
                    backgroundColor: "rgba(0, 0, 0, 0.7)",
                    padding: "2px 6px",
                    letterSpacing: "0.12em",
                  }}
                >
                  {safeCoords[idx] || `QUAD-0${idx + 1}`}
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }

    // Default: Asymmetric Hero (Top Hero 65%, Bottom thumbnails 35%)
    const secondaryImages = safeImages.length > 1 ? safeImages.slice(1, 3) : [safeImages[0], safeImages[0]];
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: `${gap}px`,
          width: "100%",
          height: "100%",
        }}
      >
        {/* Hero Top Pane */}
        <div
          style={{
            position: "relative",
            flex: "1 1 65%",
            width: "100%",
            overflow: "hidden",
            border: `1px solid ${accentColor}55`,
            transform: `scale(${interpolate(progress, [0, 1], [0.96, 1])})`,
          }}
        >
          <img src={safeImages[0]} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          {showDraftingMarks && (
            <div
              style={{
                position: "absolute",
                top: 10,
                left: 12,
                fontFamily: "var(--font-mono, monospace)",
                fontSize: "11px",
                color: accentColor,
                backgroundColor: "rgba(0, 0, 0, 0.7)",
                padding: "3px 8px",
                letterSpacing: "0.14em",
              }}
            >
              ⌜ PRIMARY MASTER · {safeCoords[0] || "SEC-A1"} ⌟
            </div>
          )}
        </div>

        {/* Bottom Split Panes */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${secondaryImages.length}, 1fr)`,
            gap: `${gap}px`,
            flex: "1 1 35%",
            width: "100%",
          }}
        >
          {secondaryImages.map((img, idx) => (
            <div
              key={`pane-sub-${idx}`}
              style={{
                position: "relative",
                width: "100%",
                height: "100%",
                overflow: "hidden",
                border: `1px solid ${accentColor}33`,
                transform: `scale(${interpolate(progress, [0, 1], [0.94, 1])})`,
              }}
            >
              <img src={img} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              {showDraftingMarks && (
                <div
                  style={{
                    position: "absolute",
                    bottom: 6,
                    left: 8,
                    fontFamily: "var(--font-mono, monospace)",
                    fontSize: "9px",
                    color: "rgba(255, 255, 255, 0.8)",
                    backgroundColor: "rgba(0, 0, 0, 0.65)",
                    padding: "2px 5px",
                    letterSpacing: "0.1em",
                  }}
                >
                  {safeCoords[idx + 1] || `SUB-0${idx + 1}`}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        backgroundColor: "#080A0F",
        padding: `${padding}px`,
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      {renderPanes()}
    </div>
  );
};
