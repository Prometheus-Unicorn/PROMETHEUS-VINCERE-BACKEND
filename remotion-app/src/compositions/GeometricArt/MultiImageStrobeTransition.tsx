import React from "react";
import { interpolate, spring } from "remotion";
import type { MultiImageStrobeProps } from "./types";
import { GeometricDraftingOverlay } from "./GeometricDraftingOverlay";

export const MultiImageStrobeTransition: React.FC<MultiImageStrobeProps> = ({
  images,
  frame,
  fps,
  durationInFrames = 10,
  strobeInterval = 1,
  enableLensFlash = true,
  enableChromaticAberration = true,
  enableDraftingHUD = true,
  accentColor = "#00F0FF",
  sfxCue,
}) => {
  // Ensure we have at least one valid image
  const safeImages = images.length > 0 ? images : ["/fallback-asset.jpg"];

  // Frame clamped within transition duration
  const localFrame = Math.max(0, Math.min(frame, durationInFrames));

  // Determine current image slice index
  const sliceIndex = Math.floor(localFrame / Math.max(1, strobeInterval)) % safeImages.length;
  const currentImage = safeImages[sliceIndex];

  // Micro-transform jitter for raw high-energy shutter feel
  const jitterX = Math.sin(localFrame * 14.3) * 5;
  const jitterY = Math.cos(localFrame * 9.7) * 4;
  const punchScale = 1.0 + Math.sin(localFrame * 3.14) * 0.04;

  // Lens flash white-out / shutter burn curve
  const flashOpacity = enableLensFlash
    ? interpolate(localFrame, [0, 1, 3, durationInFrames], [0.95, 0.6, 0.2, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  // Chromatic aberration offset
  const chromaticPx = enableChromaticAberration ? Math.max(2, 6 - (localFrame / durationInFrames) * 5) : 0;

  // Shutter burst technical telemetry
  const shutterSpeed = `1/${Math.round(2000 + (localFrame % 5) * 1500)}s`;
  const isoSpeed = `ISO ${400 + (sliceIndex % 4) * 400}`;
  const burstTag = `BURST ${String(sliceIndex + 1).padStart(2, "0")}/${String(safeImages.length).padStart(2, "0")}`;
  const frameStamp = `FR-${String(localFrame).padStart(2, "0")}`;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#05070A",
      }}
    >
      {/* Container with dynamic scale & jitter punch */}
      <div
        style={{
          width: "100%",
          height: "100%",
          transform: `scale(${punchScale}) translate(${jitterX}px, ${jitterY}px)`,
          transformOrigin: "center center",
          position: "relative",
        }}
      >
        {/* Chromatic Aberration - Red Channel Shift */}
        {enableChromaticAberration && chromaticPx > 0 && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              transform: `translate(${-chromaticPx}px, 0)`,
              mixBlendMode: "screen",
              opacity: 0.65,
              pointerEvents: "none",
            }}
          >
            <img
              src={currentImage}
              alt=""
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "drop-shadow(0 0 0 #EF3D2F)",
              }}
            />
          </div>
        )}

        {/* Chromatic Aberration - Cyan Channel Shift */}
        {enableChromaticAberration && chromaticPx > 0 && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              transform: `translate(${chromaticPx}px, 0)`,
              mixBlendMode: "screen",
              opacity: 0.65,
              pointerEvents: "none",
            }}
          >
            <img
              src={currentImage}
              alt=""
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "drop-shadow(0 0 0 #00F0FF)",
              }}
            />
          </div>
        )}

        {/* Core Primary Active Image */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
          }}
        >
          <img
            src={currentImage}
            alt=""
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      </div>

      {/* Shutter Burn / Lens Flash Overlay */}
      {enableLensFlash && flashOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "#FFFFFF",
            opacity: flashOpacity,
            mixBlendMode: "screen",
            pointerEvents: "none",
            zIndex: 10,
          }}
        />
      )}

      {/* Technical Drafting HUD & Shutter Telemetry */}
      {enableDraftingHUD && (
        <GeometricDraftingOverlay
          frame={localFrame}
          fps={fps}
          accentColor={accentColor}
          metadataLabels={[
            `SHUTTER ${shutterSpeed} · ${isoSpeed}`,
            `${burstTag} · ${frameStamp}`,
            `STROBE TRANSITION // SEED ${safeImages.length}`,
            `EXPOSURE 0.00EV`,
          ]}
        />
      )}

      {/* Vignette Rim Shadow */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          boxShadow: "inset 0 0 120px rgba(0, 0, 0, 0.7)",
          pointerEvents: "none",
          zIndex: 18,
        }}
      />
    </div>
  );
};
