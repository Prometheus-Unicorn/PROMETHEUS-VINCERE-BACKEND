import React from "react";
import {
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface OpticalRackFocusStageProps {
  children?: React.ReactNode;
  frame?: number;
  fps?: number;
  durationFrames?: number;
  headlineText?: string;
  subtitleText?: string;
  bloomColor?: string;
  enableBloom?: boolean;
  enableVignette?: boolean;
  enableLetterbox?: boolean;
  enableFilmGrain?: boolean;
  enableFloorShadow?: boolean;
  focalPlaneRole?: "primary" | "secondary";
  staggerDelayFrames?: number;
  metalGradeStyle?: "desaturated_brass" | "monochrome_crushed" | "raw";
  enableTactileShadow?: boolean;
  enableHalftoneRaster?: boolean;
  assetEntranceDirection?: "up" | "down" | "none";
  canvasColor?: string;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Optical Rack Focus & Lens Breathing Cinematic Stage for Remotion.
 *
 * Implements the 5 Foundational Physical Principles of Cinema Glass:
 * 1. Optical Rack Focus & Lens Breathing:
 *    - Deep circle-of-confusion defocus (36px blur, 1.6x overexposure bloom).
 *    - Lens breathing: barrel expansion magnification shift (scale 1.15 -> 1.02 -> 0.98).
 *    - Asymmetric S-curve deblurring into pin-sharp focus (36px -> 0px, brightness 1.6 -> 1.0).
 * 2. Kinetic Tracking Compression:
 *    - Typographic letter-spacing compressing from 0.4em down to -0.02em under a steep
 *      asymptotic curve (cubic-bezier 0.16, 1, 0.3, 1), where 80% of travel occurs in first 20% of time.
 *    - Synchronous rapid deblur (14px -> 0px) terminating against a rigid kinematic stop.
 * 3. Multiplane Inertial Parallax:
 *    - Decoupled focal depth planes where primary hero elements snap into focus first,
 *      while secondary/background elements resolve with staggered delay.
 *    - Clamped 3D angular perspective tilt (transformPerspective: 1200px, rotationX/Y within +/-4 deg).
 * 4. Damped Spring 3D Assembly & Floating Breathing Hold:
 *    - Low-frequency sinusoidal damping (sine.inOut) maintaining continuous organic micro-drift.
 *    - Calibrated underdamped harmonic settle preventing static digital freeze.
 * 5. Cinematic Defocus Outro (Racking Past Focal Plane):
 *    - Optical focus pull shifting past the focal plane into deep bokeh (scale 0.92, blur 40px, brightness 0.7)
 *      rather than an artificial opacity fade.
 */
const useRemotionContextSafe = () => {
  try {
    const frame = useCurrentFrame();
    const config = useVideoConfig();
    return { frame, fps: config?.fps ?? 30, durationInFrames: config?.durationInFrames ?? 90 };
  } catch {
    return { frame: 0, fps: 30, durationInFrames: 90 };
  }
};

export const OpticalRackFocusStage: React.FC<OpticalRackFocusStageProps> = ({
  children,
  frame: propFrame,
  fps: propFps,
  durationFrames: propDurationFrames,
  headlineText,
  subtitleText,
  bloomColor = "rgba(56, 140, 255, 0.28)",
  enableBloom = true,
  enableVignette = true,
  enableLetterbox = false,
  enableFilmGrain = true,
  enableFloorShadow = true,
  focalPlaneRole = "primary",
  staggerDelayFrames = 0,
  metalGradeStyle = "desaturated_brass",
  enableTactileShadow = true,
  enableHalftoneRaster = true,
  assetEntranceDirection = "up",
  canvasColor = "#F4F4F4",
  className,
  style,
}) => {
  const remotionContext = useRemotionContextSafe();
  const currentFrame = propFrame ?? remotionContext.frame;
  const fps = propFps ?? remotionContext.fps;
  const durationFrames = propDurationFrames ?? remotionContext.durationInFrames;

  // Clamped relative frame progression [0..durationFrames]
  const rawProgress = Math.max(0, Math.min(currentFrame, durationFrames));
  const normalizedTime = rawProgress / Math.max(1, durationFrames);

  // Timing partitions:
  // Phase 1 (Rack Focus In): 0% -> 35% of duration
  // Phase 2 (Floating Breathing Hold): 35% -> 75% of duration
  // Phase 3 (Rack Past Defocus Outro): 75% -> 100% of duration
  const inEndFrame = Math.round(durationFrames * 0.35);
  const holdEndFrame = Math.round(durationFrames * 0.75);
  const outroDuration = durationFrames - holdEndFrame;

  // Stagger calculation for secondary planes
  const effectiveInFrame = Math.max(0, rawProgress - (focalPlaneRole === "secondary" ? Math.max(8, staggerDelayFrames) : 0));

  // =========================================================================
  // 1. CAMERA RIG: LENS BREATHING, OPTICAL BLUR & EXPOSURE
  // =========================================================================
  let cameraScale = 1.0;
  let cameraBlurPx = 0.0;
  let cameraBrightness = 1.0;
  let cameraY = 0.0;

  if (rawProgress < inEndFrame) {
    // RACK FOCUS IN: Barrel expansion (scale 1.15 -> 1.02) + deblur (36px -> 0px)
    const inT = Math.min(1, rawProgress / inEndFrame);
    cameraScale = interpolate(inT, [0, 1], [1.15, 1.02], {
      easing: Easing.bezier(0.65, 0, 0.35, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraBlurPx = interpolate(inT, [0, 1], [36, 0], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraBrightness = interpolate(inT, [0, 1], [1.6, 1.0], {
      easing: Easing.out(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraY = interpolate(inT, [0, 1], [18, 0], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  } else if (rawProgress < holdEndFrame) {
    // FLOATING BREATHING HOLD: Low-frequency sinusoidal drift (scale 1.02 -> 0.98)
    const holdProgress = (rawProgress - inEndFrame) / Math.max(1, holdEndFrame - inEndFrame);
    cameraScale = interpolate(holdProgress, [0, 1], [1.02, 0.98], {
      easing: Easing.inOut(Easing.sin),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraBlurPx = 0;
    cameraBrightness = 1.0;
    cameraY = Math.sin(holdProgress * Math.PI) * -3;
  } else {
    // CINEMATIC DEFOCUS OUTRO: Racking past focal plane (blur 0 -> 40px, brightness 1.0 -> 0.7)
    const outroT = Math.min(1, (rawProgress - holdEndFrame) / Math.max(1, outroDuration));
    cameraScale = interpolate(outroT, [0, 1], [0.98, 0.92], {
      easing: Easing.inOut(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraBlurPx = interpolate(outroT, [0, 1], [0, 40], {
      easing: Easing.in(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraBrightness = interpolate(outroT, [0, 1], [1.0, 0.7], {
      easing: Easing.in(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    cameraY = interpolate(outroT, [0, 1], [0, -15], {
      easing: Easing.in(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  // =========================================================================
  // 2. HERO FOCAL PLANE ASSET DISPLACEMENT & DECOUPLING
  // =========================================================================
  let assetOpacity = 1.0;
  let assetBlurPx = 0.0;
  let assetY = 0.0;
  let assetScale = 1.0;

  if (effectiveInFrame < inEndFrame) {
    const assetT = Math.min(1, effectiveInFrame / inEndFrame);
    assetOpacity = interpolate(assetT, [0, 0.8], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    assetBlurPx = interpolate(assetT, [0, 1], [30, 0], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    const startEntranceY = assetEntranceDirection === "down" ? -120 : (assetEntranceDirection === "up" ? 120 : 0);
    assetY = interpolate(assetT, [0, 1], [startEntranceY, 0], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    assetScale = interpolate(assetT, [0, 1], [0.92, 1.0], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  } else if (rawProgress >= holdEndFrame) {
    const outroT = Math.min(1, (rawProgress - holdEndFrame) / Math.max(1, outroDuration));
    assetOpacity = interpolate(outroT, [0.2, 1], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    assetBlurPx = interpolate(outroT, [0, 1], [0, 24], {
      easing: Easing.in(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    assetY = interpolate(outroT, [0, 1], [0, -10], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  // =========================================================================
  // 3. VOLUMETRIC OPTICAL BLOOM & DYNAMIC FLOOR SHADOW
  // =========================================================================
  let bloomScale = 1.0;
  let bloomOpacity = 0.4;
  let floorShadowScale = 1.0;
  let floorShadowBlur = 0.0;
  let floorShadowOpacity = 1.0;

  if (rawProgress < inEndFrame) {
    const inT = Math.min(1, rawProgress / inEndFrame);
    bloomScale = interpolate(inT, [0, 1], [1.4, 1.0], { easing: Easing.out(Easing.quad) });
    bloomOpacity = interpolate(inT, [0, 1], [0.8, 0.4], { easing: Easing.out(Easing.quad) });
    floorShadowScale = interpolate(inT, [0, 1], [0.4, 1.0], { easing: Easing.out(Easing.cubic) });
    floorShadowBlur = interpolate(inT, [0, 1], [18, 0], { easing: Easing.out(Easing.cubic) });
    floorShadowOpacity = interpolate(inT, [0, 0.8], [0, 1]);
  } else if (rawProgress >= holdEndFrame) {
    const outroT = Math.min(1, (rawProgress - holdEndFrame) / Math.max(1, outroDuration));
    bloomScale = interpolate(outroT, [0, 1], [1.0, 1.6]);
    bloomOpacity = interpolate(outroT, [0, 1], [0.4, 0]);
    floorShadowScale = interpolate(outroT, [0, 1], [1.0, 0.5]);
    floorShadowBlur = interpolate(outroT, [0, 1], [0, 20]);
    floorShadowOpacity = interpolate(outroT, [0.3, 1], [1, 0]);
  }

  // =========================================================================
  // 4. KINETIC TRACKING COMPRESSION (TYPOGRAPHIC SNAP DE-BLUR)
  // =========================================================================
  const trackingCompressionProgress = Math.min(1, rawProgress / Math.max(1, inEndFrame));
  // Asymmetric steep deceleration: 80% displacement in first 20%
  const trackingEased = Easing.bezier(0.16, 1, 0.3, 1)(trackingCompressionProgress);
  const letterSpacingEm = interpolate(trackingEased, [0, 1], [0.4, -0.02]);
  const textDeblurPx = interpolate(trackingEased, [0, 1], [14, 0]);

  // =========================================================================
  // 5. CLAMPED 3D ANGULAR PERSPECTIVE TILT
  // =========================================================================
  const perspectiveProgress = Math.sin(normalizedTime * Math.PI * 2);
  const tiltX = Math.max(-4, Math.min(4, perspectiveProgress * 2.8));
  const tiltY = Math.max(-4, Math.min(4, Math.cos(normalizedTime * Math.PI * 2) * 2.5));

  // Mixed-Media Editorial Grading (High-Contrast Monochrome / Desaturated Brass)
  let metalGradeFilter = "";
  if (metalGradeStyle === "desaturated_brass") {
    metalGradeFilter = "grayscale(0.65) contrast(1.45) brightness(1.02)";
  } else if (metalGradeStyle === "monochrome_crushed") {
    metalGradeFilter = "grayscale(1.0) contrast(1.65) brightness(0.96)";
  }

  // Two-Tier Tactile Floating Drop Shadow (Contact + Ambient Diffuse)
  const tactileShadowFilter = enableTactileShadow
    ? "drop-shadow(0px 14px 18px rgba(0, 0, 0, 0.35)) drop-shadow(0px 48px 80px rgba(0, 0, 0, 0.16))"
    : "";

  return (
    <div
      className={className}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        perspective: 1200,
        backgroundColor: canvasColor,
        ...style,
      }}
    >
      {/* Halftone Dot Raster Screen */}
      {enableHalftoneRaster && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: "radial-gradient(circle, rgba(0, 0, 0, 0.08) 1.2px, transparent 1.2px)",
            backgroundSize: "14px 14px",
            pointerEvents: "none",
            zIndex: 4,
            opacity: 0.85,
          }}
        />
      )}
      {/* Letterbox Bars */}
      {enableLetterbox && (
        <>
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "7vh",
              backgroundColor: "#000000",
              zIndex: 50,
              pointerEvents: "none",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              width: "100%",
              height: "7vh",
              backgroundColor: "#000000",
              zIndex: 50,
              pointerEvents: "none",
            }}
          />
        </>
      )}

      {/* Atmospheric Vignette */}
      {enableVignette && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            boxShadow: "inset 0 0 140px rgba(0, 0, 0, 0.85)",
            pointerEvents: "none",
            zIndex: 40,
          }}
        />
      )}

      {/* Film Grain with multiply blend mode */}
      {enableFilmGrain && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: 0.055,
            mixBlendMode: "multiply",
            pointerEvents: "none",
            zIndex: 45,
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          }}
        />
      )}

      {/* Volumetric Optical Bloom */}
      {enableBloom && (
        <div
          style={{
            position: "absolute",
            width: "520px",
            height: "520px",
            borderRadius: "50%",
            background: `radial-gradient(circle, ${bloomColor} 0%, rgba(20, 80, 200, 0.08) 50%, transparent 75%)`,
            filter: "blur(50px)",
            pointerEvents: "none",
            zIndex: 1,
            transformOrigin: "center",
            transform: `scale(${bloomScale})`,
            opacity: bloomOpacity,
          }}
        />
      )}

      {/* Camera Rig (Simulating Cinema Barrel Lens Movement) */}
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 10,
          transformStyle: "preserve-3d",
          transform: `translateY(${cameraY}px) scale(${cameraScale}) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`,
          filter: `blur(${cameraBlurPx}px) brightness(${cameraBrightness})`,
          willChange: "transform, filter",
        }}
      >
        {/* Typographic Hero with Kinetic Tracking Compression */}
        {headlineText && (
          <div
            style={{
              marginBottom: "18px",
              textAlign: "center",
              transform: `translateY(${assetY * 0.5}px)`,
              opacity: assetOpacity,
              filter: `blur(${textDeblurPx}px)`,
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-headline, sans-serif)",
                fontSize: "clamp(24px, 4.5vw, 42px)",
                fontWeight: 900,
                color: "#FFFFFF",
                letterSpacing: `${letterSpacingEm}em`,
                textTransform: "uppercase",
                textShadow: "0 4px 24px rgba(56, 189, 248, 0.45)",
                lineHeight: 1.1,
              }}
            >
              {headlineText}
            </div>
            {subtitleText && (
              <div
                style={{
                  fontFamily: "var(--font-serif-italic, serif)",
                  fontStyle: "italic",
                  fontSize: "clamp(14px, 2.5vw, 20px)",
                  color: "rgba(255, 255, 255, 0.75)",
                  marginTop: "6px",
                  letterSpacing: `${letterSpacingEm * 0.5}em`,
                }}
              >
                {subtitleText}
              </div>
            )}
          </div>
        )}

        {/* Dynamic Floor Contact Shadow */}
        {enableFloorShadow && (
          <div
            style={{
              position: "absolute",
              bottom: "12%",
              width: "60%",
              height: "28px",
              borderRadius: "50%",
              background: "radial-gradient(ellipse at center, rgba(2, 8, 23, 0.85) 0%, rgba(2, 8, 23, 0.3) 55%, transparent 75%)",
              transform: `scaleX(${floorShadowScale}) scaleY(${floorShadowScale})`,
              filter: `blur(${floorShadowBlur}px)`,
              opacity: floorShadowOpacity,
              pointerEvents: "none",
              zIndex: 2,
            }}
          />
        )}

        {/* Core Focal Plane Asset Container with Tactile Multi-Tier Shadow & Editorial Grade */}
        <div
          style={{
            position: "relative",
            zIndex: 15,
            transform: `translateY(${assetY}px) scale(${assetScale})`,
            opacity: assetOpacity,
            filter: [assetBlurPx > 0.1 ? `blur(${assetBlurPx}px)` : "", metalGradeFilter, tactileShadowFilter].filter(Boolean).join(" "),
            willChange: "transform, filter, opacity",
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
