import React from "react";
import type { PhotoTreatmentConfig } from "./types";
import { GeometricDraftingOverlay } from "./GeometricDraftingOverlay";
import { DitherPrintEffect } from "./DitherPrintEffect";
import { ContourAtlasEffect } from "./ContourAtlasEffect";
import { SpectralCurtain } from "./SpectralCurtain";

interface GeometricArtStageProps {
  treatment?: PhotoTreatmentConfig;
  frame: number;
  fps: number;
  width?: number;
  height?: number;
  children: React.ReactNode;
}

export const GeometricArtStage: React.FC<GeometricArtStageProps> = ({
  treatment,
  frame,
  fps,
  width = 1080,
  height = 1920,
  children,
}) => {
  if (!treatment || treatment.type === "none") {
    return <>{children}</>;
  }

  const { type, drafting, dither, contour, curtain } = treatment;

  let content = children;

  // 1. Dither Print Shader
  if (type === "dither_print" || dither) {
    content = (
      <DitherPrintEffect
        algorithm={dither?.algorithm}
        palette={dither?.palette}
        cellSize={dither?.cellSize}
        contrast={dither?.contrast}
        invert={dither?.invert}
        blendMode={dither?.blendMode}
        opacity={dither?.opacity}
        width={width}
        height={height}
      >
        {content}
      </DitherPrintEffect>
    );
  }

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
      }}
    >
      {content}

      {/* 2. Topographic Contour Atlas Overlay */}
      {(type === "contour_atlas" || contour) && (
        <ContourAtlasEffect
          frame={frame}
          fps={fps}
          width={width}
          height={height}
          levels={contour?.levels}
          opacity={contour?.opacity}
          drift={contour?.drift}
          style={contour?.style}
          strokeColor={contour?.strokeColor}
          seed={contour?.seed}
        />
      )}

      {/* 3. Spectral Curtain Extrusion */}
      {(type === "spectral_curtain" || curtain) && (
        <SpectralCurtain
          frame={frame}
          fps={fps}
          width={width}
          height={height}
          curtainDensity={curtain?.curtainDensity}
          curtainLength={curtain?.curtainLength}
          curtainOpacity={curtain?.curtainOpacity}
          direction={curtain?.direction}
          chromaticShift={curtain?.chromaticShift}
        />
      )}

      {/* 4. Geometric Drafting Overlay */}
      {(type === "geometric_drafting" || drafting) && (
        <GeometricDraftingOverlay
          frame={frame}
          fps={fps}
          width={width}
          height={height}
          gridModules={drafting?.gridModules}
          showCoordinates={drafting?.showCoordinates}
          showBrackets={drafting?.showBrackets}
          showCrosshairs={drafting?.showCrosshairs}
          accentColor={drafting?.accentColor}
          textColor={drafting?.textColor}
          seed={drafting?.seed}
          metadataLabels={drafting?.metadataLabels}
        />
      )}
    </div>
  );
};
