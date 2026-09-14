import React from "react";
import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import {
  GeometricDraftingOverlay,
  DitherPrintEffect,
  ContourAtlasEffect,
  SpectralCurtain,
  MultiImageStrobeTransition,
  GeometricContactSheet,
  GeometricArtStage,
} from "../GeometricArt";

describe("Geometric Art & Photo Treatment Engine", () => {
  it("renders GeometricDraftingOverlay with brackets, crosshairs, and coordinates", () => {
    const html = renderToStaticMarkup(
      <GeometricDraftingOverlay
        frame={10}
        fps={30}
        width={1080}
        height={1920}
        accentColor="#00F0FF"
        showBrackets={true}
        showCrosshairs={true}
        showCoordinates={true}
      />
    );

    expect(html).toContain("<svg");
    expect(html).toContain("stroke=\"#00F0FF\"");
    // Check for corner bracket path
    expect(html).toContain("M 32 70 L 32 32 L 70 32");
    // Check for coordinate metadata
    expect(html).toContain("LAT 35.");
    expect(html).toContain("LONG 118.");
    expect(html).toContain("SCALE 1:1.000");
  });

  it("renders DitherPrintEffect with Bayer matrix pattern and duotone wash", () => {
    const html = renderToStaticMarkup(
      <DitherPrintEffect
        palette="cobalt"
        algorithm="bayer4"
        cellSize={8}
        contrast={1.5}
      >
        <div id="test-photo">Photo Content</div>
      </DitherPrintEffect>
    );

    expect(html).toContain("Photo Content");
    expect(html).toContain("feColorMatrix");
    expect(html).toContain("bayer-pat-8");
    expect(html).toContain("#2446E8");
  });

  it("renders ContourAtlasEffect with topographic elevation isocontours", () => {
    const html = renderToStaticMarkup(
      <ContourAtlasEffect
        frame={15}
        fps={30}
        levels={8}
        opacity={0.7}
        strokeColor="rgba(0, 240, 255, 0.5)"
        seed={42}
      />
    );

    expect(html).toContain("<svg");
    expect(html).toContain("ISO +");
    expect(html).toContain("stroke=\"rgba(0, 240, 255, 0.5)\"");
  });

  it("renders SpectralCurtain with chromatic slit ribbons", () => {
    const html = renderToStaticMarkup(
      <SpectralCurtain
        frame={20}
        fps={30}
        curtainDensity={24}
        curtainOpacity={0.6}
        chromaticShift={5}
      />
    );

    expect(html).toContain("<svg");
    expect(html).toContain("curtain-grad-down");
    expect(html).toContain("#EF3D2F");
    expect(html).toContain("#00F0FF");
  });

  it("renders MultiImageStrobeTransition cycling slices with shutter telemetry and lens flash", () => {
    const sampleImages = [
      "/images/shot_01.jpg",
      "/images/shot_02.jpg",
      "/images/shot_03.jpg",
    ];

    // Frame 0: First image, high lens flash
    const htmlFrame0 = renderToStaticMarkup(
      <MultiImageStrobeTransition
        images={sampleImages}
        frame={0}
        fps={30}
        durationInFrames={10}
        strobeInterval={1}
        enableLensFlash={true}
        enableChromaticAberration={true}
        enableDraftingHUD={true}
      />
    );

    expect(htmlFrame0).toContain("shot_01.jpg");
    expect(htmlFrame0).toContain("BURST 01/03");
    expect(htmlFrame0).toContain("SHUTTER");

    // Frame 1: Second image
    const htmlFrame1 = renderToStaticMarkup(
      <MultiImageStrobeTransition
        images={sampleImages}
        frame={1}
        fps={30}
        durationInFrames={10}
        strobeInterval={1}
      />
    );

    expect(htmlFrame1).toContain("shot_02.jpg");
    expect(htmlFrame1).toContain("BURST 02/03");

    // Frame 2: Third image
    const htmlFrame2 = renderToStaticMarkup(
      <MultiImageStrobeTransition
        images={sampleImages}
        frame={2}
        fps={30}
        durationInFrames={10}
        strobeInterval={1}
      />
    );

    expect(htmlFrame2).toContain("shot_03.jpg");
    expect(htmlFrame2).toContain("BURST 03/03");
  });

  it("renders GeometricContactSheet in asymmetric_hero, split_duo, and quad_grid layouts", () => {
    const images = [
      "/img/1.jpg",
      "/img/2.jpg",
      "/img/3.jpg",
      "/img/4.jpg",
    ];

    // Asymmetric hero layout
    const htmlHero = renderToStaticMarkup(
      <GeometricContactSheet
        images={images}
        layout="asymmetric_hero"
        frame={12}
        fps={30}
        durationInFrames={30}
      />
    );
    expect(htmlHero).toContain("PRIMARY MASTER");
    expect(htmlHero).toContain("img/1.jpg");
    expect(htmlHero).toContain("img/2.jpg");

    // Split duo layout
    const htmlDuo = renderToStaticMarkup(
      <GeometricContactSheet
        images={images.slice(0, 2)}
        layout="split_duo"
        coordinates={["PANE-01", "PANE-02"]}
        frame={12}
        fps={30}
        durationInFrames={30}
      />
    );
    expect(htmlDuo).toContain("PANE-01");
    expect(htmlDuo).toContain("PANE-02");

    // Quad grid layout
    const htmlQuad = renderToStaticMarkup(
      <GeometricContactSheet
        images={images}
        layout="quad_grid"
        frame={12}
        fps={30}
        durationInFrames={30}
      />
    );
    expect(htmlQuad).toContain("QUAD-01");
    expect(htmlQuad).toContain("QUAD-04");
  });

  it("renders GeometricArtStage wrapping an asset photo", () => {
    const html = renderToStaticMarkup(
      <GeometricArtStage
        treatment={{
          type: "geometric_drafting",
          drafting: {
            accentColor: "#EF3D2F",
            showBrackets: true,
          },
        }}
        frame={5}
        fps={30}
      >
        <img src="/asset/portrait.jpg" alt="Subject" />
      </GeometricArtStage>
    );

    expect(html).toContain("portrait.jpg");
    expect(html).toContain("stroke=\"#EF3D2F\"");
  });
});
