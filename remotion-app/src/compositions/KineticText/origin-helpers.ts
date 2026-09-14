/**
 * Origin Kit Kinetic Text Helpers
 * Remotion-safe deterministic PRNG and radial distance/geometry helpers.
 */

/**
 * Deterministic mulberry32 seeded pseudo-random number generator.
 * Produces a pseudo-random float in [0, 1) per call.
 */
export function createSeededRng(seed: string | number): () => number {
  let s = 0;
  if (typeof seed === "number") {
    s = seed | 0;
  } else if (typeof seed === "string") {
    for (let i = 0; i < seed.length; i++) {
      s = (Math.imul(31, s) + seed.charCodeAt(i)) | 0;
    }
  }
  // Ensure non-zero seed state
  if (s === 0) {
    s = 0x12345678;
  }
  return function (): number {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export interface OriginCharItem {
  char: string;
  index: number;
  totalChars: number;
  distanceFromCenter: number;
  normalizedDistance: number;
}

/**
 * Splits text into character units with radial distance-from-center calculation.
 */
export function splitTextIntoOriginChars(text: string): OriginCharItem[] {
  if (!text) return [];
  const chars = Array.from(text);
  const total = chars.length;
  const center = (total - 1) / 2;
  return chars.map((char, index) => {
    const dist = Math.abs(index - center);
    const norm = center > 0 ? dist / center : 0;
    return {
      char,
      index,
      totalChars: total,
      distanceFromCenter: dist,
      normalizedDistance: norm,
    };
  });
}

export interface OriginWordItem {
  word: string;
  index: number;
  totalWords: number;
  distanceFromCenter: number;
  normalizedDistance: number;
}

/**
 * Splits text into word units with radial distance-from-center calculation (for GSAP center-stagger ports).
 */
export function splitTextIntoOriginWords(text: string): OriginWordItem[] {
  if (!text) return [];
  const words = text.trim().split(/\s+/).filter(Boolean);
  const total = words.length;
  const center = (total - 1) / 2;
  return words.map((word, index) => {
    const dist = Math.abs(index - center);
    const norm = center > 0 ? dist / center : 0;
    return {
      word,
      index,
      totalWords: total,
      distanceFromCenter: dist,
      normalizedDistance: norm,
    };
  });
}
