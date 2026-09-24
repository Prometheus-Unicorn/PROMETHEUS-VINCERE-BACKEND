import React from "react";
import { Img, staticFile } from "remotion";
import gsap from "gsap";
import { VisualHelperComponentProps } from "./types";

/**
 * GSAP-Driven Geometric Photographic Asset Stage (inspired by geometric-art.com/pro).
 *
 * Combines:
 * 1. Literal photographic asset (e.g. photorealistic 3D Hourglass or camera/architecture).
 * 2. GSAP timeline for broadcast-grade 3D perspective orientation, orbital entrance, and living float.
 * 3. Technical Drafting HUD: Corner brackets ⌜⌟, centroid crosshair ＋, telemetry tags (SEC-01, ROT, LUMINANCE).
 * 4. Geometric Contour Atlas: Animated SVG topographic isocontour loops drifting across the asset.
 * 5. Rotating compass calibration ring with cardinal degree ticks.
 * 6. Volumetric lighting: Amber/cyan caustic rim glow and soft physical ambient occlusion.
 */
export const OriginTimeWidget: React.FC<VisualHelperComponentProps> = ({
  helper,
  frame,
  fps,
}) => {
  // Deterministic GSAP timeline scrubbing
  const timeSec = frame / fps;

  // Virtual proxy object driven by GSAP timeline
  const proxy = {
    scale: 0.6,
    rotationX: 12,
    rotationY: -32,
    rotationZ: -16,
    opacity: 0,
    translateY: -50,
    compassRotation: 0,
    contourDrift: 0,
  };

  // Build deterministic GSAP animation timeline
  const tl = gsap.timeline({ paused: true });

  // Phase 1: Dynamic 3D entrance with back-overshoot and rotational snap
  tl.fromTo(
    proxy,
    {
      scale: 0.55,
      rotationX: 18,
      rotationY: -45,
      rotationZ: -24,
      opacity: 0,
      translateY: -70,
      compassRotation: -90,
      contourDrift: 0,
    },
    {
      duration: 1.0,
      scale: 1.0,
      rotationX: 6,
      rotationY: 8,
      rotationZ: -4,
      opacity: 1,
      translateY: 0,
      compassRotation: 45,
      contourDrift: 1.0,
      ease: "back.out(1.5)",
    }
  );

  // Phase 2: Sustained cinematic living sway & orbital breathing
  tl.to(proxy, {
    duration: 5.0,
    rotationX: -4,
    rotationY: -10,
    rotationZ: 5,
    translateY: 10,
    compassRotation: 220,
    contourDrift: 4.5,
    ease: "sine.inOut",
  });

  // Scrub timeline to current exact frame
  tl.seek(timeSec);

  const imageSrc = helper.imageSrc && !helper.imageSrc.includes("hourglass")
    ? staticFile(helper.imageSrc.replace(/^(\/|public\/)/, ""))
    : null;

  const accentColor = helper.accentColor || "#FBBF24"; // warm gold / amber
  const cyanAccent = "#38BDF8";

  // Pseudo-random deterministic contour generation from frame
  const contourPhase = proxy.contourDrift * 0.9;
  const numContours = 6;
  const contourPaths = Array.from({ length: numContours }).map((_, i) => {
    const ratio = (i + 1) / (numContours + 1);
    const rx = 100 * ratio + Math.sin(contourPhase + i) * 6;
    const ry = 115 * ratio + Math.cos(contourPhase + i * 0.8) * 8;
    return `M ${120 - rx} 120 A ${rx} ${ry} 0 1 0 ${120 + rx} 120 A ${rx} ${ry} 0 1 0 ${120 - rx} 120`;
  });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        perspective: "1000px",
        pointerEvents: "none",
        width: "100%",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "240px",
          height: "240px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `translateY(${proxy.translateY}px) scale(${proxy.scale})`,
          opacity: proxy.opacity,
          transformStyle: "preserve-3d",
          willChange: "transform, opacity",
        }}
      >
        {/* 1. Geometric Compass Calibration Ring (geometric-art.com/pro) */}
        <svg
          width="260"
          height="260"
          viewBox="0 0 260 260"
          style={{
            position: "absolute",
            inset: "-10px",
            pointerEvents: "none",
            transform: `rotate(${proxy.compassRotation}deg)`,
            opacity: 0.45,
          }}
        >
          {/* Circular orbit frame */}
          <circle
            cx="130"
            cy="130"
            r="118"
            fill="none"
            stroke={cyanAccent}
            strokeWidth="1"
            strokeDasharray="4 8"
          />
          <circle
            cx="130"
            cy="130"
            r="126"
            fill="none"
            stroke="rgba(255, 255, 255, 0.25)"
            strokeWidth="0.75"
          />

          {/* Cardinal degree ticks */}
          <line x1="130" y1="4" x2="130" y2="14" stroke={accentColor} strokeWidth="2" />
          <line x1="130" y1="246" x2="130" y2="256" stroke={accentColor} strokeWidth="2" />
          <line x1="4" y1="130" x2="14" y2="130" stroke={accentColor} strokeWidth="2" />
          <line x1="246" y1="130" x2="256" y2="130" stroke={accentColor} strokeWidth="2" />

          {/* 45-degree sub-ticks */}
          <line x1="41" y1="41" x2="48" y2="48" stroke="rgba(255,255,255,0.4)" strokeWidth="1" />
          <line x1="219" y1="41" x2="212" y2="48" stroke="rgba(255,255,255,0.4)" strokeWidth="1" />
          <line x1="41" y1="219" x2="48" y2="212" stroke="rgba(255,255,255,0.4)" strokeWidth="1" />
          <line x1="219" y1="219" x2="212" y2="212" stroke="rgba(255,255,255,0.4)" strokeWidth="1" />
        </svg>

        {/* 2. Topographic Contour Atlas Elevation Rings */}
        <svg
          width="240"
          height="240"
          viewBox="0 0 240 240"
          style={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            opacity: 0.35,
          }}
        >
          {contourPaths.map((d, i) => (
            <path
              key={`contour-${i}`}
              d={d}
              fill="none"
              stroke={i % 2 === 0 ? accentColor : cyanAccent}
              strokeWidth="0.8"
              strokeDasharray={i % 3 === 0 ? "3 3" : undefined}
            />
          ))}
        </svg>

        {/* 3. Technical Drafting Corner Brackets ⌜⌟ */}
        <div
          style={{
            position: "absolute",
            inset: "12px",
            pointerEvents: "none",
          }}
        >
          {/* Top-left bracket ⌜ */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "16px",
              height: "16px",
              borderTop: `2px solid ${cyanAccent}`,
              borderLeft: `2px solid ${cyanAccent}`,
            }}
          />
          {/* Top-right bracket ⌝ */}
          <div
            style={{
              position: "absolute",
              top: 0,
              right: 0,
              width: "16px",
              height: "16px",
              borderTop: `2px solid ${cyanAccent}`,
              borderRight: `2px solid ${cyanAccent}`,
            }}
          />
          {/* Bottom-left bracket ⌞ */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              width: "16px",
              height: "16px",
              borderBottom: `2px solid ${cyanAccent}`,
              borderLeft: `2px solid ${cyanAccent}`,
            }}
          />
          {/* Bottom-right bracket ⌟ */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              right: 0,
              width: "16px",
              height: "16px",
              borderBottom: `2px solid ${cyanAccent}`,
              borderRight: `2px solid ${cyanAccent}`,
            }}
          />
        </div>

        {/* 4. Precision Centroid Crosshair ＋ */}
        <div
          style={{
            position: "absolute",
            top: "8px",
            right: "24px",
            fontFamily: "monospace",
            fontSize: "10px",
            color: cyanAccent,
            letterSpacing: "0.15em",
            opacity: 0.8,
            textShadow: `0 0 8px ${cyanAccent}`,
          }}
        >
          ＋ 810×1440
        </div>

        {/* 5. Photographic Physical Asset or Dynamic 21st.dev Chronometer Dial */}
        <div
          style={{
            position: "relative",
            zIndex: 10,
            transform: `rotateX(${proxy.rotationX}deg) rotateY(${proxy.rotationY}deg) rotateZ(${proxy.rotationZ}deg)`,
            transformStyle: "preserve-3d",
            filter:
              "drop-shadow(0 25px 40px rgba(0, 0, 0, 0.90)) " +
              `drop-shadow(0 0 35px ${accentColor}55) ` +
              `drop-shadow(0 0 15px ${cyanAccent}40)`,
            willChange: "transform, filter",
          }}
        >
          {imageSrc ? (
            <Img
              src={imageSrc}
              style={{
                width: "165px",
                height: "165px",
                objectFit: "contain",
                display: "block",
              }}
            />
          ) : (
            <div
              style={{
                width: "154px",
                height: "154px",
                borderRadius: "50%",
                background: "radial-gradient(circle at 35% 35%, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98))",
                border: `2px solid ${cyanAccent}55`,
                boxShadow: `0 20px 40px rgba(0,0,0,0.8), 0 0 25px ${cyanAccent}33, inset 0 2px 6px rgba(255,255,255,0.2)`,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
              }}
            >
              {/* Chronometer ticks & hand */}
              <svg width="144" height="144" viewBox="0 0 144 144" style={{ position: "absolute", inset: "5px" }}>
                <circle cx="72" cy="72" r="64" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" strokeDasharray="2 4" />
                <circle
                  cx="72"
                  cy="72"
                  r="56"
                  fill="none"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  strokeDasharray="351"
                  strokeDashoffset={`${351 - (timeSec % 60) * (351 / 60)}`}
                  strokeLinecap="round"
                  style={{ transform: "rotate(-90deg)", transformOrigin: "72px 72px" }}
                />
                <line
                  x1="72"
                  y1="72"
                  x2={`${72 + 44 * Math.cos(((timeSec * 6) - 90) * Math.PI / 180)}`}
                  y2={`${72 + 44 * Math.sin(((timeSec * 6) - 90) * Math.PI / 180)}`}
                  stroke={accentColor}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <circle cx="72" cy="72" r="4" fill="#FFFFFF" />
              </svg>
              <div style={{ zIndex: 5, marginTop: "42px", fontFamily: "ui-monospace, monospace", fontSize: "14px", fontWeight: 700, color: "#FFFFFF", letterSpacing: "0.08em" }}>
                {`00:${Math.floor(timeSec % 60).toString().padStart(2, "0")}`}
              </div>
              <div style={{ zIndex: 5, fontFamily: "sans-serif", fontSize: "8px", fontWeight: 600, color: cyanAccent, letterSpacing: "0.2em", textTransform: "uppercase" }}>
                PRECISION
              </div>
            </div>
          )}
        </div>

        {/* 6. Technical Telemetry Tag (geometric-art.com/pro) */}
        <div
          style={{
            position: "absolute",
            bottom: "-18px",
            left: "50%",
            transform: "translateX(-50%)",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "3px 10px",
            borderRadius: "4px",
            background: "rgba(10, 15, 29, 0.85)",
            border: `1px solid rgba(56, 189, 248, 0.4)`,
            boxShadow: `0 0 12px rgba(56, 189, 248, 0.25)`,
            whiteSpace: "nowrap",
            zIndex: 20,
          }}
        >
          <span
            style={{
              width: "5px",
              height: "5px",
              borderRadius: "50%",
              background: accentColor,
              boxShadow: `0 0 6px ${accentColor}`,
            }}
          />
          <span
            style={{
              fontFamily: '"Montserrat", monospace, sans-serif',
              fontSize: "9px",
              fontWeight: 800,
              letterSpacing: "0.18em",
              color: "#E2E8F0",
              textTransform: "uppercase",
            }}
          >
            SEC-01 // {helper.badge || "CHRONO NODES"}
          </span>
        </div>
      </div>
    </div>
  );
};
