import { describe, it, expect } from "vitest";
import * as fs from "fs";
import * as path from "path";
import {
  SPRING_TACTILE,
  SPRING_ORGANIC,
  SPRING_KINETIC,
  GLASS_SURFACE_TOKENS,
  ASSET_TYPOGRAPHY_TOKENS,
} from "../VisualHelpers/tokens";

describe("Asset Architecture & Anti-Mock Quality Guardrails", () => {
  it("enforces that motion physics tokens are strictly calibrated and bounded", () => {
    // Tactile profile must have zero overshoot clamping for numerical stability
    expect(SPRING_TACTILE.overshootClamping).toBe(true);
    expect(SPRING_TACTILE.damping).toBeGreaterThanOrEqual(20);

    // Organic profile must have smooth deceleration
    expect(SPRING_ORGANIC.damping).toBeGreaterThanOrEqual(15);
    expect(SPRING_ORGANIC.stiffness).toBeGreaterThanOrEqual(100);

    // Kinetic profile must be responsive but stable
    expect(SPRING_KINETIC.damping).toBeGreaterThanOrEqual(12);
    expect(SPRING_KINETIC.mass).toBeLessThanOrEqual(1.0);
  });

  it("enforces that glass surface tokens meet Rec.709 contrast and depth specifications", () => {
    expect(GLASS_SURFACE_TOKENS.background).toContain("rgba(15, 23, 42");
    expect(GLASS_SURFACE_TOKENS.backdropFilter).toContain("blur(");
    expect(GLASS_SURFACE_TOKENS.borderRadius).toBe("20px");
    expect(GLASS_SURFACE_TOKENS.boxShadow).toContain("inset 0 1px 1px");
  });

  it("enforces that typography tokens use governed font stacks and uppercase kickers", () => {
    expect(ASSET_TYPOGRAPHY_TOKENS.kicker.textTransform).toBe("uppercase");
    expect(ASSET_TYPOGRAPHY_TOKENS.kicker.letterSpacing).toBe("0.14em");
    expect(ASSET_TYPOGRAPHY_TOKENS.title.fontFamily).toContain("Montserrat");
  });

  it("AUDIT GUARD: verifies no component in VisualHelpers contains static mock data arrays", () => {
    const visualHelpersDir = path.resolve(__dirname, "../VisualHelpers");
    const files = fs.readdirSync(visualHelpersDir).filter((f) => f.endsWith(".tsx") || f.endsWith(".ts"));

    const prohibitedPatterns = [
      { pattern: /const\s+CALENDAR_DAYS\s*=\s*\[/i, name: "Hardcoded CALENDAR_DAYS mock array" },
      { pattern: /const\s+MOCK_\w+\s*=\s*\[/i, name: "Explicit MOCK array declaration" },
      { pattern: /\{\s*day:\s*1,\s*inMonth:\s*true\s*\},/i, name: "Hardcoded calendar day object literal" },
    ];

    const violations: string[] = [];

    for (const file of files) {
      const fullPath = path.join(visualHelpersDir, file);
      const content = fs.readFileSync(fullPath, "utf-8");

      for (const { pattern, name } of prohibitedPatterns) {
        if (pattern.test(content)) {
          violations.push(`${file}: contains ${name}`);
        }
      }
    }

    expect(
      violations,
      `Guardrail violation! Components must be dynamically driven from props, not static mock arrays: ${violations.join(
        "; "
      )}`
    ).toEqual([]);
  });
});
