"""Audit test proving Round 19: Semantic Phrase Protection, Dynamic MediaPipe Chin Deck Placement & Rack-Focus Exit.

Verifies:
1. Inseparable phrases ('in pure profit.', 'sunshine and rainbows.', 'perfectly transparent, growing')
   are correctly identified by _is_inseparable_phrase and protected from layer tearing.
2. generate_font_manifest does NOT admit inseparable prepositional clauses into behind-subject layers.
3. plan_subject_safe_placements dynamically anchors dialogue captions below the speaker's chin
   (44% - 76% Y range) rather than the rigid 80% legacy baseline.
4. PrometheusMinRun.tsx initiates rack-focus defocus blur BEFORE the incoming chunk mounts
   (nextChunkStartFrame - exitFrames), preventing visual collision overlap.
"""

from pathlib import Path
import unittest

from mini_run_pipeline.subject_placement import plan_subject_safe_placements
from mini_run_pipeline.typography import _is_inseparable_phrase, generate_font_manifest


class AuditRound19PlacementFluidityTests(unittest.TestCase):
    """Test suite proving Round 19 typography fluidity, phrase integrity, and chin clearance."""

    def test_inseparable_phrase_detection(self):
        """_is_inseparable_phrase must flag prepositional, conjunctive, and connective phrases."""
        inseparable_cases = [
            ["in", "pure", "profit."],
            ["sunshine", "and", "rainbows."],
            ["perfectly", "transparent,", "growing"],
            ["to", "this", "level"],
            ["and", "the", "best"],
            ["for", "years"],
            ["of", "business"],
            ["with", "clarity"],
        ]
        for words in inseparable_cases:
            self.assertTrue(
                _is_inseparable_phrase(words),
                f"Phrase {' '.join(words)} must be detected as inseparable",
            )

        separable_cases = [
            ["RESOLD"],
            ["SCALE"],
            ["GROWTH"],
            ["MASSIVE"],
            ["REAL", "RESULTS"],
        ]
        for words in separable_cases:
            self.assertFalse(
                _is_inseparable_phrase(words),
                f"Word/phrase {' '.join(words)} should not be flagged as inseparable",
            )

    def test_inseparable_chunks_protected_from_behind_subject_tearing(self):
        """Chunks with inseparable phrases must not be selected as behind-subject punchy layers."""
        chunks = [
            {"id": "c1", "text": "They generated six figures", "start": 0.0, "end": 2.0},
            {"id": "c2", "text": "in pure profit.", "start": 2.0, "end": 4.0},
            {"id": "c3", "text": "And the best part is,", "start": 4.0, "end": 6.0},
            {"id": "c4", "text": "perfectly transparent, growing", "start": 6.0, "end": 8.0},
            {"id": "c5", "text": "sunshine and rainbows.", "start": 8.0, "end": 10.0},
        ]
        manifest = generate_font_manifest(chunks, design_override={"subjectLayering": "auto"})
        manifest_chunks = manifest.get("chunks", [])

        chunk_map = {c["text"]: c for c in manifest_chunks}

        # c2 ("in pure profit.") must NOT be behindSubject
        self.assertFalse(
            chunk_map["in pure profit."].get("subjectLayering", {}).get("behindSubject", False),
            "Chunk 'in pure profit.' must not be placed behind the subject",
        )
        # c4 ("perfectly transparent, growing") must NOT be behindSubject
        self.assertFalse(
            chunk_map["perfectly transparent, growing"].get("subjectLayering", {}).get("behindSubject", False),
            "Chunk 'perfectly transparent, growing' must not be placed behind the subject",
        )
        # c5 ("sunshine and rainbows.") must NOT be behindSubject
        self.assertFalse(
            chunk_map["sunshine and rainbows."].get("subjectLayering", {}).get("behindSubject", False),
            "Chunk 'sunshine and rainbows.' must not be placed behind the subject",
        )

    def test_dynamic_chin_clearance_deck_placement(self):
        """Dialogue chunks must anchor dynamically below the speaker's chin, not at rigid 80%."""
        chunks = [
            {"id": "c1", "text": "This is a centered dialogue statement.", "start": 0.0, "end": 2.0},
            {"id": "c2", "text": "Continuing the dialogue cleanly.", "start": 2.0, "end": 4.0},
        ]
        # Subject centered, faceBottom at 0.50 (y=960px on 1920px canvas)
        subject_obs = [
            {
                "time": 0.5,
                "head_mid_x": 0.50,
                "head_top": 0.16,
                "head_bottom": 0.48,
                "face_bottom": 0.48,
                "box": [0.35, 0.16, 0.30, 0.55],
                "left_flank": 0.18,
                "right_flank": 0.18,
            },
            {
                "time": 2.5,
                "head_mid_x": 0.50,
                "head_top": 0.16,
                "head_bottom": 0.48,
                "face_bottom": 0.48,
                "box": [0.35, 0.16, 0.30, 0.55],
                "left_flank": 0.18,
                "right_flank": 0.18,
            },
        ]

        placements = plan_subject_safe_placements(chunks, subject_obs)
        self.assertEqual(len(placements), 2)

        for p in placements:
            y_percent_str = p.get("yPercent", "")
            self.assertTrue(y_percent_str.endswith("%"), f"yPercent must be formatted as %; got {y_percent_str}")
            y_val = float(y_percent_str.rstrip("%")) / 100.0

            # Must anchor comfortably below chin (faceBottom=0.48 -> target ~0.56 - 0.68)
            self.assertGreaterEqual(
                y_val,
                0.50,
                f"Base text should sit below chin; got {y_val}",
            )
            self.assertLessEqual(
                y_val,
                0.76,
                f"Base text should not be pushed to the bottom of the screen (legacy 80%); got {y_val}",
            )
            self.assertNotEqual(
                y_percent_str,
                "80%",
                "Base text must not be rigidly stuck at legacy 80%",
            )

    def test_rack_focus_exit_timing_in_composition(self):
        """PrometheusMinRun.tsx must initiate rack focus defocus before incoming chunk mounts."""
        comp_file = Path("remotion-app/src/compositions/PrometheusMinRun.tsx")
        self.assertTrue(comp_file.is_file(), "PrometheusMinRun.tsx composition file must exist")
        content = comp_file.read_text(encoding="utf-8")

        expected_timing = "hasIncomingCollision ? Math.max(0, nextChunkStartFrame - exitFrames) : Math.max(0, totalFrames - exitFrames)"
        self.assertIn(
            expected_timing,
            content,
            "Composition must calculate rackFocusStartFrame as (nextChunkStartFrame - exitFrames) upon collision",
        )


if __name__ == "__main__":
    unittest.main()
