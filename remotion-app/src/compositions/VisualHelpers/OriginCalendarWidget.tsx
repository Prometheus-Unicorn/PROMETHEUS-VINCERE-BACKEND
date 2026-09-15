import React from "react";
import { interpolate, spring } from "remotion";
import { VisualHelperComponentProps } from "./types";

const DAYS_HEADER = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];

// Authentic Origin UI / 21st.dev DayPicker Grid
const CALENDAR_DAYS = [
  { day: 1, inMonth: true },
  { day: 2, inMonth: true },
  { day: 3, inMonth: true },
  { day: 4, inMonth: true },
  { day: 5, inMonth: true },
  { day: 6, inMonth: true },
  { day: 7, inMonth: true },
  { day: 8, inMonth: true },
  { day: 9, inMonth: true },
  { day: 10, inMonth: true },
  { day: 11, inMonth: true },
  { day: 12, inMonth: true, inRange: true, isRangeStart: true },
  { day: 13, inMonth: true, inRange: true },
  { day: 14, inMonth: true, inRange: true, isSelected: true },
  { day: 15, inMonth: true, inRange: true, isRangeEnd: true, isToday: true },
  { day: 16, inMonth: true },
  { day: 17, inMonth: true },
  { day: 18, inMonth: true },
  { day: 19, inMonth: true },
  { day: 20, inMonth: true },
  { day: 21, inMonth: true },
  { day: 22, inMonth: true },
  { day: 23, inMonth: true },
  { day: 24, inMonth: true },
  { day: 25, inMonth: true },
  { day: 26, inMonth: true },
  { day: 27, inMonth: true },
  { day: 28, inMonth: true },
  { day: 29, inMonth: true },
  { day: 30, inMonth: true },
  { day: 31, inMonth: true },
];

/**
 * Authentic Origin UI / 21st.dev Calendar Component.
 * Pure DayPicker architecture: minimalist zinc backplate, month chevron navigation,
 * weekday row, connected date range pills, spring selection pulse, today indicator.
 * Zero macOS traffic dots, zero tacky AI badges.
 */
export const OriginCalendarWidget: React.FC<VisualHelperComponentProps> = ({
  frame,
  fps,
}) => {
  const brandPrimary = "#38BDF8";

  // Card spring entry
  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Micro-interaction: animated date selection pulse
  const selectionProgress = spring({
    frame: Math.max(0, frame - 12),
    fps,
    config: { damping: 12, stiffness: 160 },
  });

  return (
    <div
      style={{
        width: "300px",
        maxWidth: "85vw",
        transform: `scale(${interpolate(entrance, [0, 1], [0.88, 1.0])}) translateY(${interpolate(entrance, [0, 1], [24, 0])}px)`,
        opacity: entrance,
        pointerEvents: "none",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      }}
    >
      {/* Pristine Origin UI Floating Surface */}
      <div
        style={{
          background: "rgba(15, 23, 42, 0.82)",
          backdropFilter: "blur(20px) saturate(180%)",
          WebkitBackdropFilter: "blur(20px) saturate(180%)",
          borderRadius: "16px",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          padding: "16px 18px",
          boxShadow:
            "0 20px 40px -8px rgba(0, 0, 0, 0.65), " +
            "0 0 0 1px rgba(255, 255, 255, 0.05), " +
            "inset 0 1px 1px rgba(255, 255, 255, 0.15)",
        }}
      >
        {/* Month Navigation Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "12px",
          }}
        >
          <span
            style={{
              fontSize: "14px",
              fontWeight: 600,
              color: "#F8FAFC",
              letterSpacing: "-0.01em",
            }}
          >
            October 2026
          </span>
          <div style={{ display: "flex", gap: "4px" }}>
            <div
              style={{
                width: "24px",
                height: "24px",
                borderRadius: "6px",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                background: "rgba(255, 255, 255, 0.04)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#94A3B8",
                fontSize: "11px",
              }}
            >
              ‹
            </div>
            <div
              style={{
                width: "24px",
                height: "24px",
                borderRadius: "6px",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                background: "rgba(255, 255, 255, 0.04)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#94A3B8",
                fontSize: "11px",
              }}
            >
              ›
            </div>
          </div>
        </div>

        {/* Weekday Row */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            textAlign: "center",
            marginBottom: "6px",
          }}
        >
          {DAYS_HEADER.map((d) => (
            <span
              key={d}
              style={{
                fontSize: "11px",
                fontWeight: 500,
                color: "#64748B",
                height: "24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {d}
            </span>
          ))}
        </div>

        {/* 31-Day Date Grid with Range Highlight */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            rowGap: "2px",
          }}
        >
          {CALENDAR_DAYS.map((cell) => {
            const isSelected = cell.isSelected;
            const inRange = cell.inRange;
            const isRangeStart = cell.isRangeStart;
            const isRangeEnd = cell.isRangeEnd;
            const isToday = cell.isToday;

            // Range background pill styling
            let background = "transparent";
            let borderRadius = "6px";
            let color = "#E2E8F0";

            if (inRange) {
              background = "rgba(56, 189, 248, 0.14)";
              borderRadius = "0px";
              color = "#BAE6FD";
            }
            if (isRangeStart) {
              borderRadius = "6px 0 0 6px";
            }
            if (isRangeEnd) {
              borderRadius = "0 6px 6px 0";
            }
            if (isSelected) {
              background = brandPrimary;
              color = "#0F172A";
              borderRadius = "6px";
            }

            const scale = isSelected
              ? interpolate(selectionProgress, [0, 1], [0.85, 1.05])
              : 1;

            return (
              <div
                key={cell.day}
                style={{
                  height: "30px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative",
                  background,
                  borderRadius,
                }}
              >
                <span
                  style={{
                    fontSize: "12px",
                    fontWeight: isSelected ? 700 : inRange ? 600 : 400,
                    color,
                    transform: `scale(${scale})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {cell.day}
                </span>

                {/* Today Indicator Dot */}
                {isToday && !isSelected && (
                  <div
                    style={{
                      position: "absolute",
                      bottom: "2px",
                      width: "3px",
                      height: "3px",
                      borderRadius: "50%",
                      background: brandPrimary,
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
