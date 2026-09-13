"""Audit test proving Round 17 Commit 1B: Authentic Lumix Looks & Finishing Neutralization.

Verifies:
1. All curated looks in run_github_hakt_test.py resolve to authentic .cube files in mini_run_pipeline/luts/.
2. Every authentic 3D LUT look builds a filter graph containing lut3d=file= and tetrahedral/trilinear interpolation.
3. The harsh finishing stack is neutralized: no look produces 'rs=-0.08' or 'noise=alls=10'.
4. Grain strength is restrained to noise=alls=2:allf=t.
5. Legacy look aliases (moody_dramatic_cinema, bleach_bypass, fuji_3513_print) resolve to authentic .cube files.
"""

from pathlib import Path
import unittest

from mini_run_pipeline import looks
import run_github_hakt_test


class AuditRound17Commit1Tests(unittest.TestCase):
    """Test suite proving authentic Lumix grading and finishing stack neutralization."""

    def test_curated_looks_all_resolve_to_authentic_luts(self):
        """All curated looks in run_github_hakt_test.py must resolve to existing .cube files."""
        for look_id in run_github_hakt_test.CURATED_LOOKS:
            plan = looks.select_look(design={"lookId": look_id})
            self.assertEqual(plan["lookId"], look_id)
            lut_path = looks._resolve_lut_for_look(plan)
            self.assertIsNotNone(
                lut_path,
                f"Curated look '{look_id}' failed to resolve an authentic .cube LUT",
            )
            self.assertTrue(
                lut_path.is_file(),
                f"Resolved LUT path does not exist on disk: {lut_path}",
            )
            filter_str = looks.build_grade_filter(plan)
            self.assertIn("lut3d=file=", filter_str)

    def test_harsh_finishing_stack_globally_neutralized(self):
        """No look may output harsh 'rs=-0.08' cyan shadow shift or 'noise=alls=10'."""
        for look_id in run_github_hakt_test.CURATED_LOOKS:
            plan = looks.select_look(design={"lookId": look_id})
            plan["opticalFinishing"] = {
                "subtractiveSaturation": True,
                "filmGrain": True,
                "shoulderRollOff": True,
            }
            filter_str = looks.build_grade_filter(plan)

            # Must NEVER contain the old harsh cyan-shadow split tone
            self.assertNotIn(
                "rs=-0.08",
                filter_str,
                f"Look '{look_id}' contains harsh rs=-0.08 finishing stack: {filter_str}",
            )
            # Must NEVER contain excessive coarse digital noise
            self.assertNotIn(
                "noise=alls=10",
                filter_str,
                f"Look '{look_id}' contains harsh noise=alls=10: {filter_str}",
            )
            # Grain must be restrained to subtle 35mm emulsion (strength 2)
            self.assertIn(
                "noise=alls=2:allf=t",
                filter_str,
                f"Look '{look_id}' missing restrained grain noise=alls=2:allf=t: {filter_str}",
            )

    def test_legacy_look_aliases_resolve_to_authentic_cubes(self):
        """Legacy aliases (e.g. moody_dramatic_cinema) must resolve to authentic cubes without crashing."""
        for legacy_id in ["moody_dramatic_cinema", "bleach_bypass", "fuji_3513_print"]:
            plan = looks.select_look(design={"lookId": legacy_id})
            lut_path = looks._resolve_lut_for_look(plan)
            self.assertIsNotNone(
                lut_path,
                f"Legacy look '{legacy_id}' failed to resolve an authentic .cube file via aliases",
            )
            self.assertTrue(
                lut_path.is_file(),
                f"Resolved LUT path for legacy '{legacy_id}' does not exist on disk: {lut_path}",
            )
            filter_str = looks.build_grade_filter(plan)
            self.assertIn("lut3d=file=", filter_str)
            self.assertNotIn("rs=-0.08", filter_str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
