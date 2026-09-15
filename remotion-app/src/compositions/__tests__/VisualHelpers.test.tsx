import React from "react";
import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import {
  VisualHelperStage,
  LiquidGlassCard,
  LiquidMeshGradient,
  BlurVignette,
  LiquidImageRipple,
  NoiseOverlay,
  ComparisonHelper,
  ListicleHelper,
  MotionNumberHelper,
  CalloutBadgeHelper,
  OpticalRackFocusStage,
  VisualHelper,
} from "../VisualHelpers";

describe("VisualHelpers Architecture & Archetypes", () => {
  it("renders NoiseOverlay deterministically without crashing", () => {
    const html = renderToStaticMarkup(<NoiseOverlay frame={10} opacity={0.08} />);
    expect(html).toContain("<svg");
    expect(html).toContain("feTurbulence");
  });

  it("renders BlurVignette with radial mask and children", () => {
    const html = renderToStaticMarkup(
      <BlurVignette radius="28px" blur="16px">
        <div>Vignette Content</div>
      </BlurVignette>
    );
    expect(html).toContain("Vignette Content");
    expect(html).toContain("radial-gradient");
  });

  it("renders LiquidGlassCard with SVG displacement filter and specular shine", () => {
    const html = renderToStaticMarkup(
      <LiquidGlassCard frame={15} fps={30}>
        <div id="card-inner">Glass Card Inner</div>
      </LiquidGlassCard>
    );
    expect(html).toContain("Glass Card Inner");
    expect(html).toContain("feDisplacementMap");
    expect(html).toContain("liquid-glass-blur");
  });

  it("renders LiquidMeshGradient with undulating radial gradients", () => {
    const html = renderToStaticMarkup(
      <LiquidMeshGradient frame={25} fps={30} primaryColor="#A855F7" accentColor="#38BDF8" />
    );
    expect(html).toContain("radialGradient");
    expect(html).toContain("#A855F7");
  });

  it("renders LiquidImageRipple with sinusoidal wave SVG displacement", () => {
    const html = renderToStaticMarkup(
      <LiquidImageRipple frame={20} fps={30}>
        <span>Rippling Asset</span>
      </LiquidImageRipple>
    );
    expect(html).toContain("Rippling Asset");
    expect(html).toContain("feDisplacementMap");
  });

  it("renders before_after_comparison helper with split divider", () => {
    const helper: VisualHelper = {
      type: "before_after_comparison",
      title: "PROMETHEUS TRANSFORMATION",
      beforeLabel: "LEGACY METHOD",
      beforeValue: "Chaotic",
      afterLabel: "NEW SYSTEM",
      afterValue: "Cinematic",
      splitRatio: 0.5,
    };
    const html = renderToStaticMarkup(
      <ComparisonHelper helper={helper} frame={15} fps={30} />
    );
    expect(html).toContain("PROMETHEUS TRANSFORMATION");
    expect(html).toContain("LEGACY METHOD");
    expect(html).toContain("NEW SYSTEM");
    expect(html).toContain("SIDE-BY-SIDE");
  });

  it("renders listicle helper with staggered items", () => {
    const helper: VisualHelper = {
      type: "listicle",
      title: "3 RULES TO WIN",
      items: [
        { id: "1", text: "Master Attention", label: "01", highlight: true },
        { id: "2", text: "Create Contrast", label: "02" },
        { id: "3", text: "Compound Impact", label: "03" },
      ],
    };
    const html = renderToStaticMarkup(
      <ListicleHelper helper={helper} frame={20} fps={30} />
    );
    expect(html).toContain("3 RULES TO WIN");
    expect(html).toContain("Master Attention");
    expect(html).toContain("Create Contrast");
    expect(html).toContain("Compound Impact");
  });

  it("renders motion_number helper with rolling digits and currency formatting", () => {
    const helper: VisualHelper = {
      type: "motion_number",
      title: "ANNUAL REVENUE",
      value: 125000,
      targetValue: 125000,
      prefix: "$",
      suffix: " ARR",
      format: "currency",
    };
    const html = renderToStaticMarkup(
      <MotionNumberHelper helper={helper} frame={30} fps={30} />
    );
    expect(html).toContain("ANNUAL REVENUE");
    expect(html).toContain("$");
    expect(html).toContain("ARR");
  });

  it("renders callout_badge helper with icon and headline", () => {
    const helper: VisualHelper = {
      type: "callout_badge",
      title: "CRITICAL LAW",
      subtitle: "Never dilute the core message.",
      badge: "NON-NEGOTIABLE",
      icon: "star",
    };
    const html = renderToStaticMarkup(
      <CalloutBadgeHelper helper={helper} frame={10} fps={30} />
    );
    expect(html).toContain("CRITICAL LAW");
    expect(html).toContain("NON-NEGOTIABLE");
    expect(html).toContain("Never dilute the core message.");
  });

  it("renders VisualHelperStage with correct positioning and null handling", () => {
    const emptyHtml = renderToStaticMarkup(
      <VisualHelperStage frame={0} fps={30} />
    );
    expect(emptyHtml).toBe("");

    const flankHelper: VisualHelper = {
      type: "callout_badge",
      title: "PRO TIP",
      badge: "TACTICAL",
      position: "flank_right",
      icon: "zap",
    };
    const flankHtml = renderToStaticMarkup(
      <VisualHelperStage visualHelper={flankHelper} frame={15} fps={30} />
    );
    expect(flankHtml).toContain("PRO TIP");
    expect(flankHtml).toContain("right:24px");
  });

  it("renders OpticalRackFocusStage with physical lens breathing, bloom, and kinetic typography", () => {
    const html = renderToStaticMarkup(
      <OpticalRackFocusStage
        frame={15}
        fps={30}
        durationFrames={90}
        headlineText="COMPETING PRIORITIES"
        subtitleText="Something has to win"
        bloomColor="rgba(56, 189, 248, 0.4)"
        enableBloom={true}
        enableVignette={true}
        enableFilmGrain={true}
        enableFloorShadow={true}
      >
        <div id="hero-artifact">Mechanical Gear</div>
      </OpticalRackFocusStage>
    );
    expect(html).toContain("COMPETING PRIORITIES");
    expect(html).toContain("Something has to win");
    expect(html).toContain("Mechanical Gear");
    expect(html).toContain("feTurbulence"); // Film grain SVG filter
    expect(html).toContain("radial-gradient"); // Bloom / shadow
  });

  it("renders VisualHelperStage dispatching optical_rack_focus archetype fullscreen", () => {
    const rackHelper: VisualHelper = {
      type: "optical_rack_focus",
      headlineText: "INFLECTION MOMENT",
      subtitleText: "Zero in on the core goal",
    };
    const html = renderToStaticMarkup(
      <VisualHelperStage visualHelper={rackHelper} frame={15} fps={30} />
    );
    expect(html).toContain("INFLECTION MOMENT");
    expect(html).toContain("Zero in on the core goal");
    expect(html).toContain("inset:0"); // Fullscreen container
  });
});
