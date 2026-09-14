import { describe, expect, test } from "vitest";
import {
  createSeededRng,
  splitTextIntoOriginChars,
  splitTextIntoOriginWords,
} from "../KineticText/origin-helpers";

describe("createSeededRng", () => {
  test("produces deterministic float sequence in [0, 1) for the same string seed", () => {
    const rngA = createSeededRng("test-seed-abc");
    const rngB = createSeededRng("test-seed-abc");

    const seqA = [rngA(), rngA(), rngA(), rngA(), rngA()];
    const seqB = [rngB(), rngB(), rngB(), rngB(), rngB()];

    expect(seqA).toEqual(seqB);
    for (const val of seqA) {
      expect(val).toBeGreaterThanOrEqual(0);
      expect(val).toBeLessThan(1);
    }
  });

  test("produces deterministic float sequence in [0, 1) for number seed", () => {
    const rngA = createSeededRng(12345);
    const rngB = createSeededRng(12345);

    const seqA = [rngA(), rngA(), rngA()];
    const seqB = [rngB(), rngB(), rngB()];

    expect(seqA).toEqual(seqB);
  });

  test("diverges across different seeds", () => {
    const rngA = createSeededRng("seed-one");
    const rngB = createSeededRng("seed-two");

    expect(rngA()).not.toBe(rngB());
  });
});

describe("splitTextIntoOriginChars", () => {
  test("splits empty string safely", () => {
    expect(splitTextIntoOriginChars("")).toEqual([]);
  });

  test("computes radial distance-from-center for odd-length string", () => {
    const chars = splitTextIntoOriginChars("ABC");
    expect(chars).toHaveLength(3);

    // Center index is 1 ('B')
    expect(chars[0]).toMatchObject({ char: "A", index: 0, totalChars: 3, distanceFromCenter: 1, normalizedDistance: 1 });
    expect(chars[1]).toMatchObject({ char: "B", index: 1, totalChars: 3, distanceFromCenter: 0, normalizedDistance: 0 });
    expect(chars[2]).toMatchObject({ char: "C", index: 2, totalChars: 3, distanceFromCenter: 1, normalizedDistance: 1 });
  });

  test("computes radial distance-from-center for even-length string", () => {
    const chars = splitTextIntoOriginChars("ABCD");
    expect(chars).toHaveLength(4);

    // Center is 1.5
    expect(chars[0].distanceFromCenter).toBe(1.5);
    expect(chars[1].distanceFromCenter).toBe(0.5);
    expect(chars[2].distanceFromCenter).toBe(0.5);
    expect(chars[3].distanceFromCenter).toBe(1.5);
  });
});

describe("splitTextIntoOriginWords", () => {
  test("splits empty or whitespace string safely", () => {
    expect(splitTextIntoOriginWords("")).toEqual([]);
    expect(splitTextIntoOriginWords("   ")).toEqual([]);
  });

  test("computes radial distance-from-center for multi-word phrase", () => {
    const words = splitTextIntoOriginWords("The quick brown fox jumps");
    expect(words).toHaveLength(5);

    // Center index is 2 ('brown')
    expect(words[0].word).toBe("The");
    expect(words[0].distanceFromCenter).toBe(2);
    expect(words[2].word).toBe("brown");
    expect(words[2].distanceFromCenter).toBe(0);
    expect(words[2].normalizedDistance).toBe(0);
    expect(words[4].word).toBe("jumps");
    expect(words[4].distanceFromCenter).toBe(2);
  });
});
