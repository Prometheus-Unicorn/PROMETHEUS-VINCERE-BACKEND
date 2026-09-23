import { describe, it, expect } from "vitest";
import { assertSessionOwnership } from "../edit-sessions/routes";
import { SecurityViolationError } from "../gateway/security";

describe("Edit Session Anti-IDOR & Session Ownership Verification", () => {
  it("allows access to anonymous/unowned sessions in local development/fixtures", () => {
    const anonymousSession = {
      id: "session_anon_1",
      metadata: {}
    };

    // Should not throw when no ownership is claimed
    expect(() => assertSessionOwnership(anonymousSession, undefined)).not.toThrow();
  });

  it("strictly grants access when the request Bearer token matches the session owner", () => {
    const aliceSession = {
      id: "session_alice_1",
      metadata: {
        userId: "usr_alice",
        tenantId: "tenant_alpha"
      }
    };

    const aliceAuthHeader = "Bearer pat_alpha_alice_securehash";

    // Alice accessing her own session -> MUST SUCCEED
    expect(() => assertSessionOwnership(aliceSession, aliceAuthHeader)).not.toThrow();
  });

  it("blocks unauthenticated callers from accessing an authenticated user's session (IDOR Prevention)", () => {
    const aliceSession = {
      id: "session_alice_1",
      metadata: {
        userId: "usr_alice",
        tenantId: "tenant_alpha"
      }
    };

    // Unauthenticated caller -> MUST FAIL WITH 403
    expect(() => assertSessionOwnership(aliceSession, undefined)).toThrow(SecurityViolationError);
    expect(() => assertSessionOwnership(aliceSession, undefined)).toThrow(
      /Authentication required to access this edit session/
    );
  });

  it("blocks a different authenticated user from accessing someone else's session (BOLA Prevention)", () => {
    const aliceSession = {
      id: "session_alice_1",
      metadata: {
        userId: "usr_alice",
        tenantId: "tenant_alpha"
      }
    };

    // Bob has a valid token for tenant_alpha, but is user 'bob' (not 'alice')
    const bobAuthHeader = "Bearer pat_alpha_bob_securehash";

    // Bob attempting to read Alice's session -> MUST FAIL WITH 403
    expect(() => assertSessionOwnership(aliceSession, bobAuthHeader)).toThrow(SecurityViolationError);
    expect(() => assertSessionOwnership(aliceSession, bobAuthHeader)).toThrow(
      /You do not have authorization to access this edit session/
    );

    // Charlie from tenant_beta attempting to read Alice's session -> MUST FAIL WITH 403
    const charlieAuthHeader = "Bearer pat_beta_charlie_securehash";
    expect(() => assertSessionOwnership(aliceSession, charlieAuthHeader)).toThrow(SecurityViolationError);
  });

  it("verifies R2-persisted session ownership flags (r2UserId and r2TenantId)", () => {
    const r2Session = {
      id: "session_r2_1",
      metadata: {
        r2UserId: "usr_target15",
        r2TenantId: "tenant_corp"
      }
    };

    // Attacker token attempting to access session created by user 15
    const attackerAuthHeader = "Bearer pat_corp_attacker_securehash";
    expect(() => assertSessionOwnership(r2Session, attackerAuthHeader)).toThrow(SecurityViolationError);

    // Legitimate user 15 token
    const legitimateAuthHeader = "Bearer pat_corp_target15_securehash";
    expect(() => assertSessionOwnership(r2Session, legitimateAuthHeader)).not.toThrow();
  });
});
