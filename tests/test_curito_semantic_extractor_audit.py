"""Unit tests for Curito Semantic Extractor treatment auditing and schema validation."""

from __future__ import annotations

import unittest

from mini_run_pipeline.curito_semantic_extractor import (
    _RESPONSE_SCHEMA,
    DiffusionPromptPolicyCritic,
)


class CuritoSemanticExtractorAuditTests(unittest.TestCase):
    """Test schema definitions and policy critic audit for background and motion treatments."""

    def test_response_schema_contains_treatment_properties(self):
        """_RESPONSE_SCHEMA must require selected_background_treatment_id and selected_motion_treatment_id."""
        props = _RESPONSE_SCHEMA.get("properties", {})
        self.assertIn("selected_background_treatment_id", props)
        self.assertIn("selected_motion_treatment_id", props)
        required = _RESPONSE_SCHEMA.get("required", [])
        self.assertIn("selected_background_treatment_id", required)
        self.assertIn("selected_motion_treatment_id", required)

    def test_audit_treatment_ids_detects_invalid_values(self):
        """DiffusionPromptPolicyCritic reports invalid treatment IDs and replaces with canonical defaults."""
        payload = {
            "selected_background_treatment_id": "invalid_canvas",
            "selected_motion_treatment_id": "invalid_blur",
        }
        res = DiffusionPromptPolicyCritic.audit_treatment_ids(payload)
        self.assertFalse(res["passed"])
        self.assertEqual(len(res["flaws"]), 2)
        self.assertEqual(res["selected_background_treatment_id"], "halftone_raster_canvas")
        self.assertEqual(res["selected_motion_treatment_id"], "defocus_blur")

    def test_audit_treatment_ids_accepts_valid_values(self):
        """DiffusionPromptPolicyCritic accepts canonical IDs without generating flaws."""
        payload = {
            "selected_background_treatment_id": "modern_swiss_museum_poster",
            "selected_motion_treatment_id": "slow_shutter_motion_blur",
        }
        res = DiffusionPromptPolicyCritic.audit_treatment_ids(payload)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["flaws"]), 0)
        self.assertEqual(res["selected_background_treatment_id"], "modern_swiss_museum_poster")
        self.assertEqual(res["selected_motion_treatment_id"], "slow_shutter_motion_blur")

    def test_curito_default_model_is_gemini_3_8_flash(self):
        """Curito semantic extractor defaults to gemini-3.8-flash for high-tier instantaneous prompt transduction."""
        from mini_run_pipeline.curito_semantic_extractor import DEFAULT_MODEL
        self.assertEqual(DEFAULT_MODEL, "gemini-3.8-flash")

    def test_negation_includes_avoiding_and_free_from(self):
        """_is_negated correctly recognizes 'avoiding all' and 'free from' as valid negations."""
        lowered = "dramatic lighting creates floating ambient volume, avoiding all furniture or floor contact."
        # Find index of furniture
        idx = lowered.find("furniture")
        self.assertTrue(DiffusionPromptPolicyCritic._is_negated(lowered, idx))

        lowered2 = "floating in neutral spatial void, free from tables or desks."
        idx2 = lowered2.find("tables")
        self.assertTrue(DiffusionPromptPolicyCritic._is_negated(lowered2, idx2))

    def test_audit_passes_with_unitary_physics(self):
        """DiffusionPromptPolicyCritic accepts a full compliant prompt including unitary physics."""
        prompt = (
            "A heavy industrial cast-iron toggle clamp assembly with a polished steel plunger and solid brass "
            "pivot handle, captured in a spatially locked 45-degree isometric studio view. The scene opens on "
            "an unpopulated graphic canvas; at 0.0s, the clamp emerges vertically from submerged off-screen "
            "coordinates (Y: +120%), decelerating into a locked centroid position by 1.5s. The background is a "
            "modern Swiss museum poster with pristine #ECECEC matte paper, a micro-stippled technical coordinate "
            "dot grid, and 45% negative space at the top. Dramatic high-contrast raked lighting creates a floating "
            "ambient occlusion volume with soft directional shadows, avoiding all furniture or floor contact. "
            "At 3.0s, the handle snaps down with 1-DoF constrained mechanical torque, maintaining strict rigid-body "
            "topological permanence, single cohesive solid topological manifold with pinned UV surface coordinates, "
            "zero ghosted duplication, zero mesh fission, and zero 180-degree yaw flipping. Directional motion "
            "streaks on the moving handle, stationary elements remain sharp, 24fps cinema cadence. slow_shutter_motion_blur"
        )
        audit = DiffusionPromptPolicyCritic.audit_prompt(prompt)
        self.assertTrue(audit["passed"], f"Flaws detected: {audit['flaws']}")
        self.assertEqual(len(audit["flaws"]), 0)


if __name__ == "__main__":
    unittest.main()

