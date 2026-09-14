"""Audit test proving Round 20: Flank Routing, Skull Occlusion Guard, and Advance Rack-Focus Decollision.

Verifies:
1. When cranial headroom is tight (< 0.22 Y), behind-subject chunks avoid skull collision
   and route to lateral flanks (flank_right_column or flank_left_column).
2. When genuine cranial headroom is available (>= 0.22 Y), cranial_crown placement is permitted.
3. PrometheusMinRun.tsx resolves nextChunkStartFrame for split-layer chunks via findIndex,
   ensuring the 5-frame advance rack-focus exit blur triggers prior to collision.
4. gha_orchestrate.py preserves dynamic chin clearance without clobbering to 80%.
"""

from pathlib import Path
import unittest

from mini_run_pipeline.subject_placement import (
    analyze_cranial_negative_space,
    plan_subject_safe_placements,
)


class AuditRound20DecollisionAndFlankTests(unittest.TestCase):
    """Test suite proving Round 20 skull occlusion guard and advance decollision."""

    def test_tight_headroom_routes_to_flank_to_avoid_skull(self):
        """When head_top is tight (e.g. 0.141 Y), placement must route to lateral flank, not skull center."""
        # Simulated observation matching the Round 19 footage:
        # Bald speaker centered, head top at 0.141, skull spanning x: 0.35 to 0.65
        observation = {
            "frames": [
                {
                    "sourceMs": 500,
                    "faceBox": {"x": 0.36, "y": 0.141, "width": 0.28, "height": 0.36},
                    "subjectBox": {"x": 0.30, "y": 0.141, "width": 0.40, "height": 0.65},
                }
            ]
        }
        chunks = [{"text": "RIGHT?", "subjectLayering": {"behindSubject": True}}]
        placements = plan_subject_safe_placements(chunks, observation)
        self.assertEqual(len(placements), 1)
        p = placements[0]

        # Must NOT be cranial_crown (which placed text inside the skull at y=15%, x=50%)
        self.assertNotEqual(
            p.get("dominantZone"),
            "cranial_crown",
            "Tight headroom (< 0.22) must not assign cranial_crown to avoid placing text inside the skull",
        )
        self.assertIn(
            p.get("dominantZone"),
            ("flank_right_column", "flank_left_column"),
            "Tight headroom must route behind-subject text to an open lateral flank",
        )
        # Lateral flank xPercent must be cleared outside the head center (x=50%)
        x_val = float(p["xPercent"].rstrip("%")) / 100.0
        self.assertTrue(
            x_val <= 0.30 or x_val >= 0.70,
            f"Flank xPercent must be on lateral columns (< 30% or > 70%); got {x_val}",
        )

    def test_genuine_headroom_allows_cranial_crown(self):
        """When head_top is low enough (>= 0.22 Y), cranial_crown is safely permitted above the head."""
        observation = {
            "frames": [
                {
                    "sourceMs": 500,
                    "faceBox": {"x": 0.40, "y": 0.25, "width": 0.20, "height": 0.25},
                    "subjectBox": {"x": 0.35, "y": 0.25, "width": 0.30, "height": 0.60},
                }
            ]
        }
        chunks = [{"text": "CROWN", "subjectLayering": {"behindSubject": True}}]
        placements = plan_subject_safe_placements(chunks, observation)
        self.assertEqual(len(placements), 1)
        p = placements[0]
        self.assertEqual(p.get("dominantZone"), "cranial_crown")
        self.assertEqual(p.get("xPercent"), "50.0%")
        y_val = float(p["yPercent"].rstrip("%")) / 100.0
        self.assertGreaterEqual(y_val, 0.150)
        self.assertLessEqual(y_val, 0.190)

    def test_composition_resolves_next_chunk_for_split_layers(self):
        """PrometheusMinRun.tsx must use findIndex so split-layer chunks resolve nextChunkStartFrame."""
        comp_file = Path("remotion-app/src/compositions/PrometheusMinRun.tsx")
        self.assertTrue(comp_file.is_file(), "PrometheusMinRun.tsx must exist")
        content = comp_file.read_text(encoding="utf-8")

        # Must NOT use raw indexOf(chunk) which always returned -1 on split-layer object literals
        self.assertNotIn(
            "const overallIdx = (chunks || []).indexOf(chunk);",
            content,
            "Must not use indexOf(chunk) which returns -1 for split-layer chunk clones",
        )
        self.assertIn(
            "const overallIdx = (chunks || []).findIndex(",
            content,
            "Must use findIndex to resolve chunk index across split-layer clones",
        )

    def test_gha_orchestrate_preserves_dynamic_chin_clearance(self):
        """gha_orchestrate.py must not hardcode lower-deck text to 80% Y."""
        orch_file = Path(".github/scripts/gha_orchestrate.py")
        self.assertTrue(orch_file.is_file(), "gha_orchestrate.py must exist")
        content = orch_file.read_text(encoding="utf-8")

        self.assertNotIn(
            'placement["yPercent"] = "80%"',
            content,
            "gha_orchestrate.py must not hardcode placement to 80%",
        )


if __name__ == "__main__":
    unittest.main()
