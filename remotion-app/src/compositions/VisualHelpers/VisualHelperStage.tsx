import React from "react";
import { VisualHelper, VisualHelperPosition } from "./types";
import { ComparisonHelper } from "./ComparisonHelper";
import { ListicleHelper } from "./ListicleHelper";
import { MotionNumberHelper } from "./MotionNumberHelper";
import { CalloutBadgeHelper } from "./CalloutBadgeHelper";
import { BlurVignette } from "./BlurVignette";
import { LiquidImageRipple } from "./LiquidImageRipple";

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
        left: "40px",
        top: "42%",
        transform: "translateY(-50%)",
        width: "min(460px, 45%)",
        zIndex: 90,
      };
    case "flank_right":
      return {
        position: "absolute",
        right: "40px",
        top: "42%",
        transform: "translateY(-50%)",
        width: "min(460px, 45%)",
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

  const positionStyle = resolvePositionStyles(visualHelper.position);

  const renderActiveHelper = () => {
    switch (visualHelper.type) {
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
