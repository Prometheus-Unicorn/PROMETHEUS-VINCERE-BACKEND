import React from "react";
import { VisualHelper, VisualHelperPosition } from "./types";
import { ComparisonHelper } from "./ComparisonHelper";
import { ListicleHelper } from "./ListicleHelper";
import { MotionNumberHelper } from "./MotionNumberHelper";
import { CalloutBadgeHelper } from "./CalloutBadgeHelper";
import { OriginCalendarWidget } from "./OriginCalendarWidget";
import { OriginTimeWidget } from "./OriginTimeWidget";
import { BlurVignette } from "./BlurVignette";
import { LiquidImageRipple } from "./LiquidImageRipple";
import { OpticalRackFocusStage } from "./OpticalRackFocusStage";

export interface VisualHelperStageProps {
  visualHelper?: VisualHelper;
  frame: number;
  fps: number;
  palette?: {
    hero_color?: string;
    companion_color?: string;
    accent_border?: string;
    glow?: string;
    shadow?: string;
  };
}

const resolvePositionStyles = (
  position: VisualHelperPosition = "lower_deck"
): React.CSSProperties => {
  switch (position) {
    case "flank_left":
      return {
        position: "absolute",
        left: "24px",
        top: "26%",
        transform: "translateY(-50%)",
        width: "min(390px, 38%)",
        zIndex: 90,
      };
    case "flank_right":
      return {
        position: "absolute",
        right: "24px",
        top: "26%",
        transform: "translateY(-50%)",
        width: "min(390px, 38%)",
        zIndex: 90,
      };
    case "cranial_top":
      return {
        position: "absolute",
        top: "140px",
        left: "50%",
        transform: "translateX(-50%)",
        width: "min(680px, 85%)",
        zIndex: 90,
      };
    case "center":
      return {
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "min(680px, 85%)",
        zIndex: 90,
      };
    case "fullscreen":
      return {
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        zIndex: 90,
      };
    case "lower_deck":
    default:
      return {
        position: "absolute",
        bottom: "160px",
        left: "50%",
        transform: "translateX(-50%)",
        width: "min(680px, 85%)",
        zIndex: 90,
      };
  }
};

export const VisualHelperStage: React.FC<VisualHelperStageProps> = ({
  visualHelper,
  frame,
  fps,
  palette,
}) => {
  if (!visualHelper || !visualHelper.type) {
    return null;
  }

  const defaultPosition = visualHelper.type === "optical_rack_focus" ? "fullscreen" : "lower_deck";
  const positionStyle = resolvePositionStyles(visualHelper.position || defaultPosition);

  const renderActiveHelper = () => {
    switch (visualHelper.type) {
      case "optical_rack_focus":
        return (
          <OpticalRackFocusStage
            frame={frame}
            fps={fps}
            headlineText={visualHelper.headlineText || visualHelper.title}
            subtitleText={visualHelper.subtitleText || visualHelper.subtitle}
            bloomColor={visualHelper.bloomColor || palette?.glow}
            enableBloom={visualHelper.enableBloom ?? true}
            enableVignette={visualHelper.enableVignette ?? false}
            enableLetterbox={visualHelper.enableLetterbox ?? false}
            enableFilmGrain={visualHelper.enableFilmGrain ?? false}
            enableFloorShadow={visualHelper.enableFloorShadow ?? false}
            focalPlaneRole={visualHelper.focalPlaneRole || "primary"}
            staggerDelayFrames={visualHelper.staggerDelayFrames || 0}
            metalGradeStyle={visualHelper.metalGradeStyle || "desaturated_brass"}
            enableTactileShadow={visualHelper.enableTactileShadow ?? false}
            enableHalftoneRaster={visualHelper.enableHalftoneRaster ?? false}
            assetEntranceDirection={visualHelper.assetEntranceDirection || "up"}
            canvasColor={visualHelper.canvasColor || "transparent"}
          />
        );
      case "before_after_comparison":
        return (
          <ComparisonHelper
            helper={visualHelper}
            frame={frame}
            fps={fps}
            palette={palette}
          />
        );
      case "listicle":
        return (
          <ListicleHelper
            helper={visualHelper}
            frame={frame}
            fps={fps}
            palette={palette}
          />
        );
      case "motion_number":
        return (
          <MotionNumberHelper
            helper={visualHelper}
            frame={frame}
            fps={fps}
            palette={palette}
          />
        );
      case "callout_badge":
        return (
          <CalloutBadgeHelper
            helper={visualHelper}
            frame={frame}
            fps={fps}
            palette={palette}
          />
        );
      case "calendar_widget":
      case "animated_calendar":
        return (
          <OriginCalendarWidget
            helper={visualHelper}
            frame={frame}
            fps={fps}
            palette={palette}
          />
        );
      case "time_widget":
      case "hourglass_widget":
        return (
          <OriginTimeWidget
            helper={visualHelper}
            frame={frame}
            fps={fps}
            palette={palette}
          />
        );
      default:
        return null;
    }
  };

  let content = renderActiveHelper();
  if (!content) return null;

  if (visualHelper.rippleEffect) {
    content = (
      <LiquidImageRipple frame={frame} fps={fps}>
        {content}
      </LiquidImageRipple>
    );
  }

  if (visualHelper.texture === "blur_vignette") {
    content = <BlurVignette>{content}</BlurVignette>;
  }

  return (
    <div
      style={{
        ...positionStyle,
        pointerEvents: "none",
        display: "flex",
        justifyContent: "center",
      }}
    >
      {content}
    </div>
  );
};
