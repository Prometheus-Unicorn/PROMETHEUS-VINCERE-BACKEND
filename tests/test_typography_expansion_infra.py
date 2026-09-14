"""Unit tests for Typography Expansion Infrastructure (Commit 0).

Verifies:
1. Launch-rotation and promotion policy constants (multiplier, threshold, quota).
2. Intrinsic duration floor >= 750ms.
3. Hold-idle treatment catalog and deterministic selection.
4. Premium promotion multiplier boost (< 3 uses) and decay (>= 3 uses).
5. 4-chunk dedup window enforcement for premium presets.
6. Per-video quota enforcement (>= 25% premium selections when eligible).
7. Chunk manifest emission of overlayPreset and holdIdlePreset.
"""

import os
import sys
import random
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from mini_run_pipeline import typography


class TypographyExpansionInfraTests(unittest.TestCase):

    def test_named_constants_exist_with_exact_values(self):
        """The multiplier (2.5), lifetime threshold (3), and quota (25%) live as named constants."""
        self.assertEqual(typography.PREMIUM_TIER_PROMOTION_MULTIPLIER, 2.5)
        self.assertEqual(typography.PREMIUM_TIER_LIFETIME_THRESHOLD, 3)
        self.assertEqual(typography.PREMIUM_TIER_PER_VIDEO_QUOTA, 0.25)
        self.assertIn("origin_ripple_wave", typography.ANIMA_HOLD_IDLE_TREATMENTS)

    def test_intrinsic_durations_floor(self):
        """Every intrinsic duration entry respects the >= 750ms floor."""
        self.assertGreater(len(typography.INTRINSIC_ANIMATION_DURATIONS_MS), 0)
        for preset_id, dur_ms in typography.INTRINSIC_ANIMATION_DURATIONS_MS.items():
            self.assertGreaterEqual(
                dur_ms, 750,
                f"Preset {preset_id} has intrinsic duration {dur_ms}ms, below the 750ms floor"
            )

    def test_select_hold_idle_behavior(self):
        """_select_hold_idle returns None for reserved policy and valid treatment for expressive."""
        rng = random.Random(42)
        policy_reserved = {"creativity": "reserved"}
        signal = {"salience": 1.0}
        self.assertIsNone(typography._select_hold_idle(rng, policy_reserved, signal, "apple_keynote_headline_punch"))

        # Under expressive creativity, hold-idle is eligible
        selections = set()
        for i in range(50):
            r = random.Random(i)
            choice = typography._select_hold_idle(r, {"creativity": "expressive"}, {"salience": 1.0}, "some_fx")
            if choice:
                selections.add(choice)
        self.assertIn("origin_ripple_wave", selections)

    def test_premium_multiplier_boost_and_decay(self):
        """Premium preset gets 2.5x boost when usage < 3, and decays when usage >= 3."""
        # Temporarily register a dummy premium item in ANIMA_RUNTIME_TREATMENTS
        dummy_premium = {
            "id": "dummy_origin_test_preset",
            "styles": {"cinematic", "editorial"},
            "energy": 0.45,
            "tier": "premium_new",
        }
        dummy_regular = {
            "id": "dummy_regular_test_preset",
            "styles": {"cinematic", "editorial"},
            "energy": 0.45,
        }

        # Inspect weight inside a mock _select_primary_treatment context
        policy = typography.resolve_typography_policy({"creativity": "balanced", "pacing": "adaptive", "motionStyle": "cinematic"})
        signal = {"cadenceMs": 350, "salience": 0.5, "hasNumber": 0.0}

        original_treatments = list(typography.ANIMA_RUNTIME_TREATMENTS)
        try:
            typography.ANIMA_RUNTIME_TREATMENTS = original_treatments + [dummy_premium, dummy_regular]

            # Under usage = 0, premium item receives promotion multiplier
            usage_fresh = {dummy_premium["id"]: 0, dummy_regular["id"]: 0}
            # Run selection 100 times with identical seed state to compare relative selection rates
            premium_picks = 0
            runs = 200
            for i in range(runs):
                rng = random.Random(i)
                pick = typography._select_primary_treatment(
                    rng, policy, signal, usage_fresh, recent=[], is_single_word=False
                )
                if pick == dummy_premium["id"]:
                    premium_picks += 1

            self.assertGreater(premium_picks, 0, "Fresh premium preset should be selected due to 2.5x boost")

            # When usage reaches or exceeds threshold (3), multiplier decays
            usage_decayed = {dummy_premium["id"]: 3, dummy_regular["id"]: 0}
            decayed_picks = 0
            for i in range(runs):
                rng = random.Random(i)
                pick = typography._select_primary_treatment(
                    rng, policy, signal, usage_decayed, recent=[], is_single_word=False
                )
                if pick == dummy_premium["id"]:
                    decayed_picks += 1

            # Decayed picks should be significantly fewer than fresh picks
            self.assertLess(decayed_picks, premium_picks, "Decayed picks should be lower after lifetime threshold")
        finally:
            typography.ANIMA_RUNTIME_TREATMENTS = original_treatments

    def test_premium_four_chunk_dedup_window(self):
        """A premium preset cannot appear twice within any 4-chunk window."""
        dummy_premium = {
            "id": "dummy_premium_dedup_preset",
            "styles": {"cinematic", "editorial"},
            "energy": 0.45,
            "tier": "premium_new",
        }
        original_treatments = list(typography.ANIMA_RUNTIME_TREATMENTS)
        try:
            typography.ANIMA_RUNTIME_TREATMENTS = original_treatments + [dummy_premium]
            policy = typography.resolve_typography_policy()
            signal = {"cadenceMs": 350, "salience": 0.5, "hasNumber": 0.0}
            usage = {dummy_premium["id"]: 0}

            # If recent[-4:] contains dummy_premium, it must NOT be selected
            recent_with_premium = ["preset_a", "preset_b", dummy_premium["id"], "preset_c"]
            for i in range(50):
                rng = random.Random(i)
                pick = typography._select_primary_treatment(
                    rng, policy, signal, usage, recent=recent_with_premium, is_single_word=False
                )
                self.assertNotEqual(
                    pick, dummy_premium["id"],
                    "Premium preset appeared within recent 4-chunk window!"
                )
        finally:
            typography.ANIMA_RUNTIME_TREATMENTS = original_treatments

    def test_per_video_quota_enforcement(self):
        """When premium candidates exist and quota is below 25%, selection prioritizes premium."""
        dummy_premium = {
            "id": "dummy_premium_quota_preset",
            "styles": {"cinematic", "editorial"},
            "energy": 0.45,
            "tier": "premium_new",
        }
        original_treatments = list(typography.ANIMA_RUNTIME_TREATMENTS)
        # All real premium_new preset IDs (already in catalog before dummy is added)
        real_premium_ids = {item["id"] for item in original_treatments if item.get("tier") == "premium_new"}
        try:
            typography.ANIMA_RUNTIME_TREATMENTS = original_treatments + [dummy_premium]
            policy = typography.resolve_typography_policy()
            signal = {"cadenceMs": 350, "salience": 0.5, "hasNumber": 0.0}

            # Simulate total_assigned = 5, premium_assigned = 0 → ratio = 0.0 < 0.25
            usage = {item["id"]: 1 for item in original_treatments[:5]}
            usage[dummy_premium["id"]] = 0
            # Also zero-out all real premium presets so the quota can pick any of them
            for pid in real_premium_ids:
                usage[pid] = 0

            all_premium_ids = real_premium_ids | {dummy_premium["id"]}

            rng = random.Random(99)
            pick = typography._select_primary_treatment(
                rng, policy, signal, usage, recent=["other_1", "other_2"], is_single_word=False
            )
            self.assertIn(pick, all_premium_ids, "Quota enforcement should select an available premium candidate")
        finally:
            typography.ANIMA_RUNTIME_TREATMENTS = original_treatments

    def test_manifest_emits_overlay_and_hold_idle_presets(self):
        """Manifest chunks and layers include overlayPreset and holdIdlePreset fields."""
        chunks = [
            {"text": "Performance isn't created", "startMs": 0, "endMs": 1500, "words": []},
            {"text": "it's engineered", "startMs": 1500, "endMs": 3000, "words": []},
        ]
        manifest = typography.generate_font_manifest(chunks, {"seed": "test-seed-manifest"})
        for chunk in manifest["chunks"]:
            self.assertIn("overlayPreset", chunk)
            self.assertIn("holdIdlePreset", chunk)
            self.assertIn("overlayPreset", chunk["selection"])
            self.assertIn("holdIdlePreset", chunk["selection"])
            for layer in chunk["layers"]:
                self.assertIn("overlayPreset", layer)
                self.assertIn("holdIdlePreset", layer)


if __name__ == "__main__":
    unittest.main()
