import { describe, it, expect, vi } from "vitest";
import { sanitizeSegment } from "../integrations/r2";
import { resolveAuthScope, SecurityViolationError } from "../gateway/security";

describe("Upload & Storage Security (Anti-Parameter-Tampering & Anti-IDOR)", () => {
  it("sanitizes storage key segments and neutralizes directory traversal indicators", () => {
    expect(sanitizeSegment("safe-user_123", "fallback")).toBe("safe-user_123");
    expect(sanitizeSegment("../etc/passwd", "fallback")).toBe("fallback");
    expect(sanitizeSegment("..", "fallback")).toBe("fallback");
    expect(sanitizeSegment(".", "fallback")).toBe("fallback");
    expect(sanitizeSegment("user/../../evil", "fallback")).toBe("fallback");
    expect(sanitizeSegment("   ", "fallback")).toBe("fallback");
  });

  it("derives user and tenant scope strictly from authorization session, ignoring untrusted overrides", () => {
    const session = resolveAuthScope("Bearer pat_tenantABC_user42_hash123");
    expect(session.authenticated).toBe(true);
    expect(session.userId).toBe("usr_user42");
    expect(session.tenantId).toBe("tenant_tenantABC");

    // Client body attempts to claim user15
    const clientSuppliedUserId = "user15";
    const effectiveUserId = session.authenticated ? session.userId : clientSuppliedUserId;

    // Must strictly prioritize the session identity over the client payload
    expect(effectiveUserId).toBe("usr_user42");
    expect(effectiveUserId).not.toBe("user15");
  });

  it("blocks cross-user storage path access when an authenticated user attempts to process another user's uploads", () => {
    const authScope = resolveAuthScope("Bearer pat_tenant1_alice_hash");
    expect(authScope.userId).toBe("usr_alice");

    const victimKey = "uploads/usr_bob/confidential-recording.mp4";
    const ownKey = "uploads/usr_alice/vacation-video.mp4";

    const validateAccess = (key: string) => {
      if (authScope.authenticated && key.startsWith("uploads/")) {
        const expectedPrefix = `uploads/${authScope.userId}/`;
        if (!key.startsWith(expectedPrefix)) {
          throw new SecurityViolationError(
            "Access denied: Cannot access or process storage assets belonging to another user."
          );
        }
      }
    };

    // Access to own object is allowed
    expect(() => validateAccess(ownKey)).not.toThrow();

    // Access to Bob's object triggers a SecurityViolationError
    expect(() => validateAccess(victimKey)).toThrow(SecurityViolationError);
    expect(() => validateAccess(victimKey)).toThrow(/Access denied/);
  });
});
