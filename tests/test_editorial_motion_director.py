"""Unit tests for the Editorial Motion Director Architecture.

Validates:
1. Editorial Primitives canonical dictionary completeness (the 8 core primitives).
2. Hostile Anti-Cliché Gate in DiffusionPromptPolicyCritic (rejection of glitch, rgb split, camera shake).
3. Explicit negation handling for anti-cliché terms.
4. Fail-Fast on prompt synthesis failure (EditorialPromptSynthesisError, strict NO SILENT FALLBACK).
5. Editorial causality chain schema compliance (3-act physical causality, audio-visual counterpoint, safe-zone).
6. EditorialDirectorDetector scoring and novelty budget restraint.
7. Fail-Fast on headless animation generation failure (EditorialAnimationGenerationError).
"""

from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from mini_run_pipeline.curito_semantic_extractor import (
    EDITORIAL_PRIMITIVES,
    DiffusionPromptPolicyCritic,
    EditorialPromptPolicyViolationError,
    EditorialPromptSynthesisError,
    _RESPONSE_SCHEMA,
    _build_deterministic_curito_plan,
    extract_and_synthesize_curito_prompt,
)
from mini_run_pipeline.curito_animation_orchestrator import (
    EditorialAnimationGenerationError,
    EditorialDirectorDetector,
    CuritoAnimationDetector,
    CuritoAnimationOrchestrator,
)


class EditorialMotionDirectorTests(unittest.TestCase):
    """Test suite for Editorial Motion Director architecture and non-negotiables."""

    def test_canonical_editorial_primitives_completeness(self):
        """Verify that all 8 canonical editorial primitives are defined with rigorous descriptions."""
        expected_primitives = {
            "CONTRAST",
            "SCALE_MAGNIFICATION",
            "MICRO_DEVIATION",
            "CASCADING_PROPAGATION",
            "PHYSICAL_SEIZURE",
            "CONSEQUENTIAL_CONVERGENCE",
            "FOUNDATIONAL_PROPAGATION",
            "INEVITABLE_YIELD",
        }
        self.assertEqual(set(EDITORIAL_PRIMITIVES.keys()), expected_primitives)
        for prim, desc in EDITORIAL_PRIMITIVES.items():
            self.assertGreater(len(desc), 20, f"Description for {prim} is too short.")

    def test_hostile_anti_cliche_gate_rejects_glitch_and_shake(self):
        """PromptPolicyCritic must reject digital clichés (glitch, rgb split, camera shake)."""
        cliche_prompt = (
            "A heavy industrial clamp with high rotational torque. "
            "At the inflection moment, the screen undergoes a digital glitch and violent camera shake "
            "with RGB split across the frame. Pristine halftone raster canvas background with negative space. "
            "Spatially locked fixed tripod camera, 1-DoF constrained axis, unitary manifold with zero duplication, "
            "vertical bottom emergence from submerged Y coordinates."
        )
        audit = DiffusionPromptPolicyCritic.audit_prompt(cliche_prompt)
        self.assertFalse(audit["passed"])
        flaws_str = " ".join(audit["flaws"])
        self.assertIn("VIOLATION (Editorial Anti-Cliché)", flaws_str)
        self.assertIn("glitch", flaws_str)
        self.assertIn("camera shake", flaws_str)
        self.assertIn("rgb split", flaws_str)

    def test_hostile_anti_cliche_gate_accepts_negated_cliches(self):
        """Explicitly negated clichés (e.g. 'zero glitch', 'no camera shake') must pass the gate."""
        negated_prompt = (
            "A heavy industrial dual-throw knife switch assembly, 45-degree isometric studio view. "
            "Pristine matte off-white graphic canvas with fine micro-stippled dot grid texture, reserving "
            "the upper 45% as clean negative space. Dramatic high-contrast raked key lighting with floating "
            "ambient occlusion volume, avoiding all tables and furniture. Spatially locked fixed tripod camera, "
            "1-DoF constrained downward rotation, single cohesive solid topological manifold with pinned UV coordinates, "
            "zero ghosted duplication, zero mesh fission, zero 180-degree yaw flipping, native 24fps cinema cadence. "
            "The assembly emerges from submerged off-screen coordinates Y: +120% during 0.0s - 1.5s decelerating into locked centroid. "
            "At 3.0s, the lever snaps down with mechanical torque into solid copper jaws, maintaining pure mechanical silence "
            "with zero glitch, no camera shake, and no digital distortion. Directional motion streaks on moving lever. slow_shutter_motion_blur"
        )
        audit = DiffusionPromptPolicyCritic.audit_prompt(negated_prompt)
        self.assertTrue(audit["passed"], f"Unexpected flaws: {audit['flaws']}")

    def test_response_schema_contains_editorial_causality_chain(self):
        """_RESPONSE_SCHEMA must specify and validate editorial_causality_chain."""
        props = _RESPONSE_SCHEMA.get("properties", {})
        self.assertIn("editorial_causality_chain", props)
        causality_props = props["editorial_causality_chain"]["properties"]
        self.assertIn("primary_editorial_primitive", causality_props)
        self.assertIn("causality_act_1_equilibrium", causality_props)
        self.assertIn("causality_act_2_inflection", causality_props)
        self.assertIn("causality_act_3_consequence", causality_props)
        self.assertIn("audio_visual_counterpoint", causality_props)
        self.assertIn("kinetic_momentum_vector", causality_props)
        self.assertIn("acoustic_co_destruction_spec", causality_props)
        self.assertIn("ergonomic_safe_zone", causality_props)

    def test_deterministic_plan_includes_causality_chain(self):
        """_build_deterministic_curito_plan must conform to the 3-act physical causality schema."""
        plan = _build_deterministic_curito_plan([{"text": "mechanical clamp drifts by ten microns"}])
        self.assertIn("editorial_causality_chain", plan)
        chain = plan["editorial_causality_chain"]
        self.assertEqual(chain["primary_editorial_primitive"], "FOUNDATIONAL_PROPAGATION")
        self.assertIn("causality_act_1_equilibrium", chain)
        self.assertIn("causality_act_2_inflection", chain)
        self.assertIn("causality_act_3_consequence", chain)
        # Check counterpoint lead and lag bounds
        av = chain["audio_visual_counterpoint"]
        self.assertLessEqual(av["visual_lead_sec"], 0.0)
        self.assertGreaterEqual(av["residual_lag_sec"], 0.8)
        # Check safe-zone diamond bounds
        sz = chain["ergonomic_safe_zone"]
        self.assertGreaterEqual(sz["top_y_px"], 300)
        self.assertLessEqual(sz["bottom_y_px"], 1500)

    @patch("requests.Session.post")
    def test_fail_fast_when_gemini_models_fail(self, mock_post):
        """extract_and_synthesize_curito_prompt MUST raise EditorialPromptSynthesisError on failure.
        
        Strict Non-Negotiable: No silent fallback to deterministic presets in production.
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_post.return_value = mock_resp

        chunks = [{"chunkIndex": 0, "startSec": 0.0, "endSec": 3.0, "text": "Every single micron of tolerance has to clamp down"}]
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_test_key_abc"}):
            with self.assertRaises(EditorialPromptSynthesisError) as ctx:
                extract_and_synthesize_curito_prompt(chunks)
            self.assertIn("Per strict editorial pipeline non-negotiables, silent fallback", str(ctx.exception))

    def test_editorial_director_detector_prioritizes_causality_over_generic_tokens(self):
        """EditorialDirectorDetector must score high-causality monologue chunks higher than generic speech."""
        high_causality_chunk = {
            "text": "If that mechanical clamp drifts by even ten microns, the assembly line seizes up and gross margin drops to zero.",
            "startMs": 7500,
            "endMs": 11800,
        }
        low_causality_chunk = {
            "text": "Here is a standard corporate framework for business growth.",
            "startMs": 7500,
            "endMs": 11800,
        }

        is_cand_high, score_high, rat_high = EditorialDirectorDetector.evaluate_chunk_for_animation(
            chunk=high_causality_chunk,
            chunk_index=2,
            time_since_last_animation_sec=50.0,
        )
        is_cand_low, score_low, rat_low = EditorialDirectorDetector.evaluate_chunk_for_animation(
            chunk=low_causality_chunk,
            chunk_index=2,
            time_since_last_animation_sec=50.0,
        )

        self.assertTrue(is_cand_high)
        self.assertGreater(score_high, score_low)
        self.assertIn("causality signals", rat_high)

    def test_novelty_budget_restraint_filter(self):
        """Novelty budget filter suppresses rapid consecutive animation spam."""
        low_causality_chunk = {
            "text": "This is another interesting principle.",
            "startMs": 4000,
            "endMs": 7000,
        }
        # Time since last animation is only 3.0s (less than 8s threshold)
        is_cand, score, rat = EditorialDirectorDetector.evaluate_chunk_for_animation(
            chunk=low_causality_chunk,
            chunk_index=1,
            time_since_last_animation_sec=3.0,
            novelty_budget_enforced=True,
        )
        self.assertFalse(is_cand)
        self.assertIn("Restraint filter", rat)

    def test_orchestrator_raises_editorial_generation_error_without_silent_fallback(self):
        """CuritoAnimationOrchestrator must raise EditorialAnimationGenerationError when generator fails."""
        orchestrator = CuritoAnimationOrchestrator(
            client=None,
            veo_client=None,
            flow_client=None,
            fixture_video_path="/nonexistent/fixture.mp4",
        )
        chunk = {
            "text": "When you build physical hardware at scale, you cannot just push a software patch over the air.",
            "startMs": 0,
            "endMs": 3500,
        }
        with self.assertRaises(EditorialAnimationGenerationError) as ctx:
            orchestrator.plan_and_generate_animation(
                chunk=chunk,
                chunk_index=0,
            )
        self.assertIn("Per strict editorial pipeline non-negotiables, silent fallback is prohibited", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
