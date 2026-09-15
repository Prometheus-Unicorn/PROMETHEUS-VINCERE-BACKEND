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

    def test_curito_default_model_is_gemini_2_5_pro(self):
        """Curito semantic extractor defaults to gemini-2.5-pro for highest-capability prompt transduction."""
        from mini_run_pipeline.curito_semantic_extractor import DEFAULT_MODEL
        self.assertEqual(DEFAULT_MODEL, "gemini-2.5-pro")


if __name__ == "__main__":
    unittest.main()

