import { describe, it, expect } from "vitest";
import { createJobId, createEditSessionId } from "../utils/ids";

describe("Cryptographic ID Generation (Anti-Enumeration & Anti-IDOR)", () => {
  const UUID_V4_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  it("generates job IDs conforming to standard UUIDv4 format with prefix", () => {
    const id = createJobId();
    expect(id.startsWith("job_")).toBe(true);

    const uuidPart = id.replace(/^job_/, "");
    expect(UUID_V4_PATTERN.test(uuidPart)).toBe(true);
  });

  it("generates edit session IDs conforming to standard UUIDv4 format with prefix", () => {
    const id = createEditSessionId();
    expect(id.startsWith("edit_")).toBe(true);

    const uuidPart = id.replace(/^edit_/, "");
    expect(UUID_V4_PATTERN.test(uuidPart)).toBe(true);
  });

  it("guarantees high entropy with zero collisions across 1,000 generated IDs", () => {
    const count = 1000;
    const generatedJobIds = new Set<string>();
    const generatedSessionIds = new Set<string>();

    for (let i = 0; i < count; i++) {
      generatedJobIds.add(createJobId());
      generatedSessionIds.add(createEditSessionId());
    }

    expect(generatedJobIds.size).toBe(count);
    expect(generatedSessionIds.size).toBe(count);
  });

  it("eliminates predictable sequential or timestamp prefixes", () => {
    const id1 = createJobId();
    const id2 = createJobId();

    // Verify it doesn't share identical timestamp base36 prefixes
    const prefix1 = id1.slice(4, 12);
    const prefix2 = id2.slice(4, 12);
    // UUIDv4 first 8 hex characters are pseudo-random and will differ
    expect(prefix1).not.toBe(prefix2);
  });
});
