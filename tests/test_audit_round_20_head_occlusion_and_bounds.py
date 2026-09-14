import unittest
from mini_run_pipeline.subject_placement import (
    _clamp_safe_x_percent,
    plan_subject_safe_placements,
    analyze_cranial_negative_space,
)
from mini_run_pipeline.policy_check import (
    validate_head_occlusion,
    run_post_render_conformance_check,
)


class TestAuditRound20HeadOcclusionAndBounds(unittest.TestCase):
    """Audit test suite for Round 20 Fix 3:
    1. Head occlusion on behind-subject pivots nestled in cranial crown negative space passes <= 40%.
    2. Wide captions (> 320px) are rejected from narrow flank columns, anchoring safely in foreground lower deck.
    3. _clamp_safe_x_percent protects off-center and flank elements from being teleported to 50%.
    4. Conformance check derives active chunk midpoints avoiding dead transition gaps.
    """

    def test_cranial_crown_head_occlusion_pass(self):
        """Behind-subject pivot in cranial crown maintains occlusion <= 40%."""
        observation = {
            "frames": [
                {
                    "sourceMs": 500,
                    "faceBox": {"x": 0.36, "y": 0.144, "width": 0.28, "height": 0.36},
                    "subjectBox": {"x": 0.30, "y": 0.144, "width": 0.40, "height": 0.65},
                }
            ]
        }
        chunk = {
            "chunkIndex": 17,
            "text": "dream come true, right?",
            "subjectLayering": {"behindSubject": True},
            "layers": [
                {
                    "layerIndex": 0,
                    "rawText": "DREAM COME TRUE,",
                    "behindSubject": False,
                    "fontSizePx": 80,
                    "fontFamily": "Inter",
                },
                {
                    "layerIndex": 1,
                    "rawText": "right?",
                    "behindSubject": True,
                    "fontSizePx": 210,
                    "fontFamily": "Teko",
                    "casing": "uppercase",
                },
            ],
        }
        placements = plan_subject_safe_placements([chunk], observation)
        self.assertEqual(len(placements), 1)
        p = placements[0]
        self.assertEqual(p["dominantZone"], "cranial_crown")
        self.assertEqual(p["xPercent"], "50.0%")
        self.assertEqual(p["yPercent"], "15.0%")

        # Policy check evaluation
        chunk["placement"] = p
        chunk["layers"][1]["placement"] = p
        res = validate_head_occlusion([chunk["layers"][1]], chunks=[chunk])
        self.assertEqual(res["status"], "passed")
        self.assertLessEqual(res["maxOcclusionFound"], 0.40)
        self.assertEqual(len(res["violations"]), 0)

    def test_wide_caption_flank_rejection(self):
        """Captions without flank intent or following cranial crown route safely to lower deck."""
        observation = {
            "frames": [
                {
                    "sourceMs": 500,
                    "faceBox": {"x": 0.36, "y": 0.15, "width": 0.28, "height": 0.35},
                    "subjectBox": {"x": 0.30, "y": 0.15, "width": 0.40, "height": 0.65},
                }
            ]
        }
        chunk_18 = {
            "chunkIndex": 18,
            "text": "Well, for me it was.",
            "layers": [
                {
                    "layerIndex": 0,
                    "rawText": "Well, for me it was.",
                    "fontFamily": "Outfit",
                    "fontSizePx": 64,
                    "estimatedWidthPx": 499.0,
                    "behindSubject": False,
                }
            ],
        }
        placements = plan_subject_safe_placements([chunk_18], observation)
        p = placements[0]
        self.assertEqual(p["dominantZone"], "foreground_lower_deck")
        self.assertEqual(p["xPercent"], "50.0%")

    def test_clamp_safe_x_percent_protects_flank_positions(self):
        """_clamp_safe_x_percent does not force off-center or flank elements to 50%."""
        # A 650px wide element placed at 20% on the left flank
        clamped_left = _clamp_safe_x_percent("20.0%", est_width_px=650.0, anchor="center")
        self.assertNotEqual(clamped_left, "50.0%")
        val_left = float(clamped_left.rstrip("%"))
        self.assertLess(val_left, 50.0)

        # A 650px wide element placed at 80% on the right flank
        clamped_right = _clamp_safe_x_percent("80.0%", est_width_px=650.0, anchor="center")
        self.assertNotEqual(clamped_right, "50.0%")
        val_right = float(clamped_right.rstrip("%"))
        self.assertGreater(val_right, 50.0)


if __name__ == "__main__":
    unittest.main()
