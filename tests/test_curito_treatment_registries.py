"""Unit tests for Curito Background & Motion Treatment Registries and Policy Auditing."""

from __future__ import annotations

import unittest

from mini_run_pipeline.curito_animation_dna import (
    BACKGROUND_TREATMENT_REGISTRY,
    MOTION_TREATMENT_REGISTRY,
    BackgroundTreatment,
    MotionTreatment,
    select_background_treatment,
    select_motion_treatment,
)
from mini_run_pipeline.curito_semantic_extractor import DiffusionPromptPolicyCritic


class CuritoTreatmentRegistriesTests(unittest.TestCase):
    """Verify registry population, selection algorithms, and policy audit validation."""

    def test_background_registry_contains_four_canonical_treatments(self):
        """BACKGROUND_TREATMENT_REGISTRY must contain the 4 canonical background IDs."""
        expected_ids = {
            "halftone_raster_canvas",
            "luxury_editorial_sunlight_canvas",
            "newspaper_collage_deconstructed",
            "modern_swiss_museum_poster",
        }
        self.assertEqual(set(BACKGROUND_TREATMENT_REGISTRY.keys()), expected_ids)
        for bg_id, bg in BACKGROUND_TREATMENT_REGISTRY.items():
            self.assertIsInstance(bg, BackgroundTreatment)
            self.assertEqual(bg.id, bg_id)
            self.assertTrue(len(bg.name) > 0)
            self.assertTrue(len(bg.dna_snippet) > 20)
            self.assertTrue(len(bg.tags) > 0)
            self.assertTrue(len(bg.use_cases) > 0)

    def test_motion_registry_contains_four_canonical_treatments(self):
        """MOTION_TREATMENT_REGISTRY must contain the 4 canonical motion blur IDs."""
        expected_ids = {
            "defocus_blur",
            "gaussian_blur",
            "bokeh_blur",
            "slow_shutter_motion_blur",
        }
        self.assertEqual(set(MOTION_TREATMENT_REGISTRY.keys()), expected_ids)
        for mt_id, mt in MOTION_TREATMENT_REGISTRY.items():
            self.assertIsInstance(mt, MotionTreatment)
            self.assertEqual(mt.id, mt_id)
            self.assertTrue(len(mt.name) > 0)
            self.assertTrue(len(mt.dna_snippet) > 20)
            self.assertTrue(len(mt.tags) > 0)
            self.assertTrue(len(mt.kinetic_classes) > 0)
            self.assertTrue(len(mt.use_cases) > 0)

    def test_select_background_treatment_default_and_routing(self):
        """select_background_treatment defaults to halftone_raster_canvas and routes by keywords."""
        default_bg = select_background_treatment()
        self.assertEqual(default_bg.id, "halftone_raster_canvas")

        luxury_bg = select_background_treatment(use_case_hint="luxury editorial sunlight canvas with warm amber tone")
        self.assertEqual(luxury_bg.id, "luxury_editorial_sunlight_canvas")

        grunge_bg = select_background_treatment(tags=["newspaper", "collage", "grunge"])
        self.assertEqual(grunge_bg.id, "newspaper_collage_deconstructed")

        swiss_bg = select_background_treatment(use_case_hint="modern swiss museum poster high contrast architectural grid")
        self.assertEqual(swiss_bg.id, "modern_swiss_museum_poster")

    def test_select_motion_treatment_default_and_routing(self):
        """select_motion_treatment defaults to defocus_blur and routes by kinetic class/tags."""
        default_mt = select_motion_treatment()
        self.assertEqual(default_mt.id, "defocus_blur")

        kinetic_mt = select_motion_treatment(kinetic_class="high_speed_rotation", use_case_hint="fast spinning gears")
        self.assertEqual(kinetic_mt.id, "slow_shutter_motion_blur")

        gaussian_mt = select_motion_treatment(use_case_hint="soft entry ethereal haze dissolve")
        self.assertEqual(gaussian_mt.id, "gaussian_blur")

        bokeh_mt = select_motion_treatment(tags=["bokeh", "depth_of_field", "isolation"])
        self.assertEqual(bokeh_mt.id, "bokeh_blur")

    def test_audit_treatment_ids_valid_and_invalid(self):
        """DiffusionPromptPolicyCritic.audit_treatment_ids flags invalid IDs and provides defaults."""
        valid_dict = {
            "selected_background_treatment_id": "luxury_editorial_sunlight_canvas",
            "selected_motion_treatment_id": "slow_shutter_motion_blur",
        }
        res = DiffusionPromptPolicyCritic.audit_treatment_ids(valid_dict)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["flaws"]), 0)
        self.assertEqual(res["selected_background_treatment_id"], "luxury_editorial_sunlight_canvas")
        self.assertEqual(res["selected_motion_treatment_id"], "slow_shutter_motion_blur")

        invalid_dict = {
            "selected_background_treatment_id": "nonexistent_canvas",
            "selected_motion_treatment_id": "unknown_blur",
        }
        res_invalid = DiffusionPromptPolicyCritic.audit_treatment_ids(invalid_dict)
        self.assertFalse(res_invalid["passed"])
        self.assertEqual(len(res_invalid["flaws"]), 2)
        # Should be auto-defaulted to canonical fallbacks
        self.assertEqual(res_invalid["selected_background_treatment_id"], "halftone_raster_canvas")
        self.assertEqual(res_invalid["selected_motion_treatment_id"], "defocus_blur")


if __name__ == "__main__":
    unittest.main()
