import React from "react";
import { interpolate, spring } from "remotion";
import { VisualHelperComponentProps } from "./types";
import {
  SPRING_ORGANIC,
  SPRING_TACTILE,
  GLASS_SURFACE_TOKENS,
  ASSET_TYPOGRAPHY_TOKENS,
} from "./tokens";

const DAYS_HEADER = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];

export interface CalendarDayCell {
  day: number;
  inMonth: boolean;
  inRange?: boolean;
  isRangeStart?: boolean;
  isRangeEnd?: boolean;
  isSelected?: boolean;
  isToday?: boolean;
}

/**
 * Dynamic Month Grid Generator.
 * Generates dates algorithmically based on month parameters without hardcoded mock arrays.
 */
export const generateDynamicMonthGrid = (
  year?: number,
  month?: number, // 1-indexed (1 = Jan, 12 = Dec)
  selectedDay?: number,
  rangeStart?: number,
  rangeEnd?: number,
  todayDay?: number
): CalendarDayCell[] => {
  const now = new Date();
  const y = year ?? now.getFullYear();
  const m = month ?? (now.getMonth() + 1);
  const daysInMonth = new Date(y, m, 0).getDate();
  const firstDayOfWeek = (new Date(y, m - 1, 1).getDay() + 6) % 7; // Monday = 0

  const sDay = selectedDay ?? Math.min(daysInMonth, now.getDate());
  const rStart = rangeStart ?? Math.max(1, sDay - 2);
  const rEnd = rangeEnd ?? Math.min(daysInMonth, sDay + 1);
  const tDay = todayDay ?? Math.min(daysInMonth, now.getDate());

  const cells: CalendarDayCell[] = [];

  // Padding cells before first day of month
  for (let i = 0; i < firstDayOfWeek; i++) {
    cells.push({ day: 0, inMonth: false });
  }

  // Active month days
  for (let d = 1; d <= daysInMonth; d++) {
    const isSelected = d === sDay;
    const inRange = d >= rStart && d <= rEnd;
    const isRangeStart = d === rStart;
    const isRangeEnd = d === rEnd;
    const isToday = d === tDay;

    cells.push({
      day: d,
      inMonth: true,
      inRange,
      isRangeStart,
      isRangeEnd,
      isSelected,
      isToday,
    });
  }

  return cells;
};

/**
 * Governed Origin UI / 21st.dev Calendar Component.
 * Pure DayPicker architecture: minimalist zinc backplate, dynamic algorithmic date generation,
 * weekday row, connected date range pills, spring selection pulse, today indicator.
 * Governed by design tokens: zero hardcoded mock arrays, zero ad-hoc CSS backplates.
 */
export const OriginCalendarWidget: React.FC<VisualHelperComponentProps> = ({
  helper,
  frame,
  fps,
  palette,
}) => {
  const brandPrimary = palette?.hero_color || helper.primaryColor || "#38BDF8";

  // Parse or dynamically assign month & active range from helper properties
  const now = React.useMemo(() => new Date(), []);
  const targetYear = (helper as any).year ?? now.getFullYear();
  const targetMonth = (helper as any).month ?? (now.getMonth() + 1);
  const selectedDay = (helper as any).selectedDay ?? now.getDate();
  const rangeStart = (helper as any).rangeStart ?? Math.max(1, selectedDay - 2);
  const rangeEnd = (helper as any).rangeEnd ?? Math.min(28, selectedDay + 1);
  const defaultMonthName = now.toLocaleString("default", { month: "long" });
  const displayTitle = helper.title || `${defaultMonthName} ${targetYear}`;

  const calendarDays = React.useMemo(() => {
    return generateDynamicMonthGrid(targetYear, targetMonth, selectedDay, rangeStart, rangeEnd, selectedDay);
  }, [targetYear, targetMonth, selectedDay, rangeStart, rangeEnd]);

  // Card spring entry governed by SPRING_ORGANIC token
  const entrance = spring({
    frame,
    fps,
    config: SPRING_ORGANIC,
  });

  // Micro-interaction: animated date selection pulse governed by SPRING_TACTILE token
  const selectionProgress = spring({
    frame: Math.max(0, frame - 12),
    fps,
    config: SPRING_TACTILE,
  });

  return (
    <div
      style={{
        width: "320px",
        maxWidth: "85vw",
        transform: `scale(${interpolate(entrance, [0, 1], [0.90, 1.0])}) translateY(${interpolate(
          entrance,
          [0, 1],
          [24, 0]
        )}px)`,
        opacity: entrance,
        pointerEvents: "none",
        fontFamily: ASSET_TYPOGRAPHY_TOKENS.dateGrid.fontFamily,
      }}
    >
      {/* Governed High-End Glass Surface Backplate */}
      <div
        style={{
          background: GLASS_SURFACE_TOKENS.background,
          backdropFilter: GLASS_SURFACE_TOKENS.backdropFilter,
          WebkitBackdropFilter: GLASS_SURFACE_TOKENS.WebkitBackdropFilter,
          borderRadius: GLASS_SURFACE_TOKENS.borderRadius,
          border: GLASS_SURFACE_TOKENS.border,
          boxShadow: GLASS_SURFACE_TOKENS.boxShadow,
          padding: "18px 20px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Specular sheen gradient overlay */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: GLASS_SURFACE_TOKENS.specularSheenGradient,
            pointerEvents: "none",
            borderRadius: GLASS_SURFACE_TOKENS.borderRadius,
          }}
        />

        {/* Month Navigation Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "14px",
            position: "relative",
            zIndex: 2,
          }}
        >
          <span
            style={{
              fontFamily: ASSET_TYPOGRAPHY_TOKENS.title.fontFamily,
              fontSize: "15px",
              fontWeight: 700,
              color: "#F8FAFC",
              letterSpacing: "-0.01em",
            }}
          >
            {displayTitle}
          </span>
          <div style={{ display: "flex", gap: "6px" }}>
            <div
              style={{
                width: "24px",
                height: "24px",
                borderRadius: "6px",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                background: "rgba(255, 255, 255, 0.05)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#94A3B8",
                fontSize: "12px",
              }}
            >
              ‹
            </div>
            <div
              style={{
                width: "24px",
                height: "24px",
                borderRadius: "6px",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                background: "rgba(255, 255, 255, 0.05)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#94A3B8",
                fontSize: "12px",
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
            marginBottom: "8px",
            position: "relative",
            zIndex: 2,
          }}
        >
          {DAYS_HEADER.map((d) => (
            <span
              key={d}
              style={{
                fontSize: "11px",
                fontWeight: 600,
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

        {/* Algorithmic Day Grid with Dynamic Range Highlighting */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            rowGap: "3px",
            position: "relative",
            zIndex: 2,
          }}
        >
          {calendarDays.map((cell, idx) => {
            if (!cell.inMonth) {
              return <div key={`empty-${idx}`} style={{ height: "30px" }} />;
            }

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
              background = "rgba(56, 189, 248, 0.16)";
              borderRadius = "0px";
              color = "#BAE6FD";
            }
            if (isRangeStart) {
              borderRadius = "8px 0 0 8px";
            }
            if (isRangeEnd) {
              borderRadius = "0 8px 8px 0";
            }
            if (isSelected) {
              background = brandPrimary;
              color = "#0F172A";
              borderRadius = "8px";
            }

            const scale = isSelected
              ? interpolate(selectionProgress, [0, 1], [0.88, 1.04])
              : 1;

            return (
              <div
                key={`day-${cell.day}`}
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
                      width: "4px",
                      height: "4px",
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
