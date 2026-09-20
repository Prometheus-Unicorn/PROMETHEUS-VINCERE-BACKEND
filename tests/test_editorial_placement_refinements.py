"""Tests for editorial placement refinements, cranial negative space elevation, and companion styling."""

import unittest
from mini_run_pipeline.subject_placement import (
    analyze_cranial_negative_space,
    plan_subject_safe_placements,
)
from mini_run_pipeline.typography import (
    generate_font_manifest,
)


class EditorialPlacementRefinementsTests(unittest.TestCase):
    def test_companion_placement_avoids_microphone_deck_plunge(self):
        """Companion layer in split-layer chunks must anchor in the middle third (54%-66% Y),

        NEVER plunging down to 80% Y where microphones, boom arms, and laps reside.
        """
        observation = {
            "frames": [
                {
                    "sourceMs": 3000,
                    "faceCount": 1,
                    "faceBox": {"x": 0.35, "y": 0.22, "width": 0.30, "height": 0.28},
                    "subjectBox": {"x": 0.25, "y": 0.22, "width": 0.50, "height": 0.75},
                }
            ]
        }
        chunks = [
            {
                "chunkIndex": 2,
                "startMs": 2980,
                "endMs": 6180,
                "text": "a better video editor.",
                "subjectLayering": {"behindSubject": True},
                "layers": [
                    {"text": "a better video", "behindSubject": False, "role": "context_clause"},
                    {"text": "EDITOR.", "behindSubject": True, "role": "primary_focus_word"},
                ],
            }
        ]

        placements = plan_subject_safe_placements(chunks, observation)
        self.assertEqual(len(placements), 1)
        placement = placements[0]
        
        # Check the companion placement
        self.assertTrue(placement.get("hasSplitLayerPlacement"))
        comp = placement.get("companionPlacement")
        self.assertIsNotNone(comp)
        
        comp_y_str = comp.get("yPercent", "")
        comp_y = float(comp_y_str.replace("%", ""))
        # Must be in natural middle third / lower-middle field (54% - 66%), strictly < 72%
        self.assertLessEqual(comp_y, 66.0, f"Companion Y {comp_y}% is too low (plunged over microphone)!")
        self.assertGreaterEqual(comp_y, 52.0, f"Companion Y {comp_y}% is too high (into face)!")
        print("PASS_G1_COMPANION_OK")

    def test_cranial_negative_space_elevates_into_open_ceiling(self):
        """When abundant headroom exists above the speaker (e.g. head top at 0.20-0.25),

        cranial text center must be allowed to elevate into the upper negative space (e.g. 8%-12% Y),
        rather than being clamped at an artificial 15%-19% floor where it gets swallowed by the hair.
        """
        analysis = analyze_cranial_negative_space(
            subject_box={"x": 0.30, "y": 0.22, "width": 0.40, "height": 0.65},
            head_top_y=0.22,
        )
        self.assertEqual(analysis["dominantZone"], "cranial_crown")
        y_str = analysis.get("yPercent", "")
        y_val = float(y_str.replace("%", ""))
        # Text center should elevate into the upper negative space (~9%-13%), not jammed down at 15%-19%
        self.assertLessEqual(y_val, 13.5, f"Cranial Y {y_val}% is clamped too low down onto the head!")
        self.assertGreaterEqual(y_val, 6.0, f"Cranial Y {y_val}% breached upper ceiling safe margin!")
        print("PASS_G2_CRANIAL_OK")

    def test_companion_clause_styling_not_flat_generic(self):
        """Secondary clauses and companion phrases must carry refined typography styling

        (proper casing, letter spacing, font pairing, and visual hierarchy) rather than raw unstyled flat all-caps.
        """
        chunks = [
            {
                "chunkIndex": 5,
                "text": "right now is completely unedited.",
                "words": [
                    {"text": "right", "start_ms": 7560, "end_ms": 7800},
                    {"text": "now", "start_ms": 7800, "end_ms": 8100},
                    {"text": "is", "start_ms": 8100, "end_ms": 8300},
                    {"text": "completely", "start_ms": 8300, "end_ms": 8900},
                    {"text": "unedited.", "start_ms": 8900, "end_ms": 12640},
                ],
            }
        ]
        manifest = generate_font_manifest(chunks, {"typographySystem": "hakt", "motif": "royal_amethyst"})
        manifest_chunk = manifest["chunks"][0]
        layers = manifest_chunk.get("layers", [])
        self.assertGreaterEqual(len(layers), 2)
        
        comp_layer = next((l for l in layers if not l.get("isHero") and not l.get("behindSubject")), layers[0])
        # Companion layer should have letter spacing, weight balance, or refined case
        self.assertIsNotNone(comp_layer.get("letterSpacing"), "Companion layer missing letterSpacing")
        # Ensure it doesn't default to unstyled generic fallback
        self.assertNotIn(comp_layer.get("fontFamily"), ["sans-serif", "arial", "system-ui"])
        print("PASS_G3_STYLING_OK")


if __name__ == "__main__":
    unittest.main()
