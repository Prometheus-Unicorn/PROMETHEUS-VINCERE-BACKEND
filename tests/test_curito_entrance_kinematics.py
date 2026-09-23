"""Unit tests for dynamic entrance-into-view kinematics and anti-static-duck policy enforcement."""

import unittest
from mini_run_pipeline.curito_animation_dna import (
    ENTRANCE_TREATMENT_REGISTRY,
    CuritoPromptStitcher,
    CuritoWordSyncCalculator,
    EntranceTreatment,
    select_entrance_treatment,
)
from mini_run_pipeline.curito_semantic_extractor import (
    _RESPONSE_SCHEMA,
    DiffusionPromptPolicyCritic,
)


class TestCuritoEntranceKinematics(unittest.TestCase):
    """Verifies that hero assets animate into view and frame-zero static props are rejected."""

    def test_entrance_registry_contains_six_canonical_treatments(self):
        """ENTRANCE_TREATMENT_REGISTRY must contain the 6 vetted entrance treatments."""
        expected_ids = {
            "vertical_bottom_emergence",
            "lateral_friction_slide",
            "slapdrop_bounce",
            "off_axis_3d_swing",
            "polarizing_bevel_elevation",
            "optical_rack_focus_bokeh_accretion",
        }
        self.assertEqual(set(ENTRANCE_TREATMENT_REGISTRY.keys()), expected_ids)
        for tid, treatment in ENTRANCE_TREATMENT_REGISTRY.items():
            self.assertIsInstance(treatment, EntranceTreatment)
            self.assertEqual(treatment.id, tid)
            self.assertTrue(len(treatment.dna_snippet) > 40)
            self.assertTrue(len(treatment.use_cases) >= 2)

    def test_select_entrance_treatment_default_and_routing(self):
        """select_entrance_treatment defaults to vertical_bottom_emergence and matches by keyword."""
        default_et = select_entrance_treatment()
        self.assertEqual(default_et.id, "vertical_bottom_emergence")

        slide_et = select_entrance_treatment(treatment_id="lateral_friction_slide")
        self.assertEqual(slide_et.id, "lateral_friction_slide")

        swing_et = select_entrance_treatment(use_case_hint="3d hinged gate perspective swing")
        self.assertEqual(swing_et.id, "off_axis_3d_swing")

        bounce_et = select_entrance_treatment(tags=["slapdrop", "squash", "bounce"])
        self.assertEqual(bounce_et.id, "slapdrop_bounce")

        rack_et = select_entrance_treatment(treatment_id="optical_rack_focus_bokeh_accretion")
        self.assertEqual(rack_et.id, "optical_rack_focus_bokeh_accretion")

        rack_hint_et = select_entrance_treatment(use_case_hint="anamorphic cinema lens f1.2 rack-focus reveal")
        self.assertEqual(rack_hint_et.id, "optical_rack_focus_bokeh_accretion")

    def test_stitch_prompt_incorporates_entrance_treatment(self):
        """CuritoPromptStitcher.stitch_prompt incorporates dynamic entrance snippet into action."""
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:05.000",
            target_phrase="unit economics",
            target_word_offset_sec=3.0,
            desired_duration_sec=6.0,
        )
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="dual-beam analytical balance scale",
            word_sync=word_sync,
            entrance_treatment="vertical_bottom_emergence",
        )
        prompt_str = stitched.full_prompt
        self.assertIn("submerged off-screen position", prompt_str)
        self.assertIn("power4.out cubic deceleration", prompt_str)
        self.assertIn("unit economics", prompt_str)

    def test_stitch_prompt_incorporates_optical_rack_focus_treatment(self):
        """CuritoPromptStitcher.stitch_prompt incorporates optical rack-focus anamorphic bokeh accretion."""
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:05.000",
            target_phrase="first principles",
            target_word_offset_sec=3.0,
            desired_duration_sec=6.0,
        )
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="precision horological escapement mechanism",
            word_sync=word_sync,
            entrance_treatment="optical_rack_focus_bokeh_accretion",
        )
        prompt_str = stitched.full_prompt
        self.assertIn("anamorphic cinema lens", prompt_str)
        self.assertIn("blur: 36px, brightness: 1.6", prompt_str)
        self.assertIn("power4.out cubic deceleration", prompt_str)
        self.assertIn("first principles", prompt_str)

    def test_response_schema_mandates_entrance_properties(self):
        """_RESPONSE_SCHEMA must require selected_entrance_treatment_id and entrance_kinematic_treatment."""
        props = _RESPONSE_SCHEMA.get("properties", {})
        self.assertIn("selected_entrance_treatment_id", props)
        required = _RESPONSE_SCHEMA.get("required", [])
        self.assertIn("selected_entrance_treatment_id", required)

        vp_props = props["visual_plate_schema"]["properties"]
        self.assertIn("entrance_kinematic_treatment", vp_props)
        vp_required = props["visual_plate_schema"]["required"]
        self.assertIn("entrance_kinematic_treatment", vp_required)

    def test_audit_treatment_ids_validates_entrance_id(self):
        """DiffusionPromptPolicyCritic.audit_treatment_ids validates entrance treatment ID."""
        valid_payload = {
            "selected_background_treatment_id": "halftone_raster_canvas",
            "selected_motion_treatment_id": "defocus_blur",
            "selected_entrance_treatment_id": "lateral_friction_slide",
        }
        res = DiffusionPromptPolicyCritic.audit_treatment_ids(valid_payload)
        self.assertTrue(res["passed"])
        self.assertEqual(res["selected_entrance_treatment_id"], "lateral_friction_slide")

        valid_payload_optical = {
            "selected_background_treatment_id": "halftone_raster_canvas",
            "selected_motion_treatment_id": "defocus_blur",
            "selected_entrance_treatment_id": "optical_rack_focus_bokeh_accretion",
        }
        res_optical = DiffusionPromptPolicyCritic.audit_treatment_ids(valid_payload_optical)
        self.assertTrue(res_optical["passed"])
        self.assertEqual(res_optical["selected_entrance_treatment_id"], "optical_rack_focus_bokeh_accretion")

        invalid_payload = {
            "selected_background_treatment_id": "halftone_raster_canvas",
            "selected_motion_treatment_id": "defocus_blur",
            "selected_entrance_treatment_id": "bogus_entrance",
        }
        res_invalid = DiffusionPromptPolicyCritic.audit_treatment_ids(invalid_payload)
        self.assertFalse(res_invalid["passed"])
        self.assertEqual(res_invalid["selected_entrance_treatment_id"], "vertical_bottom_emergence")

    def test_audit_prompt_rejects_static_duck_and_missing_entrance(self):
        """DiffusionPromptPolicyCritic.audit_prompt flags frame-zero static props and missing entrance."""
        static_duck_prompt = (
            "At center frame, a high-precision dual-beam balance scale sits suspended from frame 0. "
            "Hand-finished solid brass and blackened carbon steel. Suspended in spatial-temporal space "
            "against a pristine matte off-white graphic canvas with subtle halftone dot screening, "
            "reserving upper 45% as clean negative space. Warm diffuse overhead lighting with floating "
            "ambient occlusion volume. Spatially locked fixed-tripod camera with 1-DoF constrained "
            "axial rotation along central shaft, strict rigid-body topological permanence, single cohesive mesh, "
            "zero 180-degree yaw flipping, zero ghosting, 24fps native cinema cadence. Rotational torque "
            "with mechanical snap locking anvil into place."
        )
        res = DiffusionPromptPolicyCritic.audit_prompt(static_duck_prompt)
        self.assertFalse(res["passed"])
        flaws_text = " ".join(res["flaws"])
        self.assertIn("Entrance Kinematics", flaws_text)

    def test_audit_prompt_accepts_dynamic_entrance_into_view(self):
        """DiffusionPromptPolicyCritic.audit_prompt passes prompts with dynamic entrance kinematics."""
        compliant_prompt = (
            "The scene opens on an unpopulated, pristine graphic canvas with subtle halftone dot screening, "
            "reserving upper 45% as clean negative space. At frame 0, a high-precision dual-beam analytical "
            "balance scale with tungsten calibration mass initiates from a submerged off-screen position "
            "below lower frame boundary and is propelled upward along vertical axis with steep power4.out cubic "
            "deceleration, animates into view and decelerates into locked centroid position by 1.2s. "
            "Hand-finished solid brass beam and blackened steel arresting anvil. Warm diffuse overhead wash "
            "with floating ambient occlusion volume. Spatially locked fixed-tripod 45-degree isometric camera, "
            "1-DoF constrained axial rotation, single cohesive mesh, strict rigid-body topological permanence, "
            "zero 180-degree yaw flipping, zero ghosting, 24fps native cadence. Solid tungsten mass drops into pan "
            "with rotational torque, mechanical snap locking firmly against anvil."
        )
        res = DiffusionPromptPolicyCritic.audit_prompt(compliant_prompt)
        self.assertTrue(res["passed"], f"Expected compliant prompt to pass but got flaws: {res['flaws']}")

    def test_audit_prompt_handles_negated_forbidden_terms(self):
        """Negated terms like 'no camera orbit' and 'no table' must not trigger policy violations."""
        prompt = (
            "The scene opens on an unpopulated, pristine graphic canvas with subtle halftone dot screening, "
            "reserving upper 45% as clean negative space, with absolutely no table or domestic furniture. "
            "At frame 0, a high-precision dual-throw knife switch with heavy copper blades initiates from "
            "submerged off-screen position Y: +120% and is propelled upward along vertical axis, animates into view "
            "with steep power4.out cubic deceleration into locked centroid position by 1.2s. "
            "Solid copper busbars and blackened carbon steel. Warm diffuse overhead wash with floating ambient occlusion. "
            "Spatially locked fixed-tripod 45-degree isometric view with absolutely no camera orbit and zero revolving camera motion. "
            "Constrained 1-DoF single-axis downward rotation, strict rigid-body topological permanence, single cohesive mesh, "
            "zero 180-degree yaw flipping, zero ghosting, 24fps native cadence. Snapping down into busbar jaws with rotational torque."
        )
        res = DiffusionPromptPolicyCritic.audit_prompt(prompt)
        self.assertTrue(res["passed"], f"Expected negated prompt to pass cleanly but got flaws: {res['flaws']}")

    def test_audit_prompt_accepts_optical_rack_focus_prompt(self):
        """DiffusionPromptPolicyCritic.audit_prompt passes prompts with optical rack-focus bokeh accretion."""
        optical_prompt = (
            "The scene opens on an unpopulated, pristine graphic canvas with subtle halftone dot screening, "
            "reserving upper 45% as clean negative space. At frame 0, an ultra-wide aperture anamorphic cinema lens "
            "(f/1.2 equivalent) stops down from total defocus (blur: 36px, brightness: 1.6) into tack-sharp clarity "
            "as a high-precision dual-beam analytical balance scale with tungsten calibration mass animates into view "
            "and elevates upward along the Y-axis with steep power4.out cubic deceleration and directional motion blur, "
            "resolving into locked centroid position with shallow depth-of-field stratification and rotational torque, "
            "followed by a breathing micro-drift hold from 1.8s to 4.5s. Solid brass beam and blackened steel arresting anvil. "
            "Warm diffuse overhead wash with floating ambient occlusion volume. Spatially locked fixed-tripod 45-degree "
            "isometric camera, 1-DoF constrained axial rotation, single cohesive solid topological manifold, strict rigid-body "
            "permanence, zero 180-degree yaw flipping, zero ghosting, 24fps native cadence."
        )
        res = DiffusionPromptPolicyCritic.audit_prompt(optical_prompt)
        self.assertTrue(res["passed"], f"Expected optical rack-focus prompt to pass cleanly but got flaws: {res['flaws']}")


if __name__ == "__main__":
    unittest.main()

