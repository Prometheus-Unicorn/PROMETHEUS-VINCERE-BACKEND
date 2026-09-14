"""Audit test proving Round 18: Rec.709 Studio Grade Protection & Zero Shadow Crush.

Verifies:
1. Selecting lookId='none' (or 'passthrough', 'original') produces an empty filter string ("").
2. Passing standard Rec.709 studio footage with lookId='none' bypasses destructive V-Log LUT transforms.
3. run_github_hakt_test.build_payload() defaults to 'none' for test-video.mp4 to prevent accidental V-Log shadow crushing.
4. run_github_hakt_test.SUPPORTED_LOOKS contains 'none' and 'passthrough'.
5. Shadow clipping (<10 luminance) on Rec.709 passthrough remains strictly bounded below 5.0%.
"""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import cv2
import numpy as np

from mini_run_pipeline import looks
import run_github_hakt_test


class AuditRound18Rec709ProtectionTests(unittest.TestCase):
    """Test suite proving Rec.709 studio footage preservation and shadow crush prevention."""

    def test_none_look_produces_empty_filter_string(self):
        """lookId='none' must produce an empty FFmpeg filter string ("") with zero intensity."""
        for none_synonym in ["none", "passthrough", "original", "natural", "raw"]:
            plan = looks.select_look(design={"lookId": none_synonym})
            self.assertEqual(plan["lookId"], "none")
            self.assertEqual(plan["intensity"], 0.0)
            filter_str = looks.build_grade_filter(plan)
            self.assertEqual(
                filter_str,
                "",
                f"Synonym '{none_synonym}' must produce empty filter string; got: {filter_str}",
            )

    def test_run_github_hakt_test_defaults_to_none(self):
        """run_github_hakt_test.build_payload must default to 'none' to protect Rec.709 footage."""
        payload = run_github_hakt_test.build_payload()
        self.assertEqual(
            payload["design"]["lookId"],
            "none",
            "run_github_hakt_test must default to 'none' for test video to prevent V-Log crushing",
        )
        self.assertEqual(payload["metadata"]["lookId"], "none")

    def test_supported_looks_includes_passthrough_options(self):
        """run_github_hakt_test.SUPPORTED_LOOKS must include 'none' and 'passthrough'."""
        self.assertIn("none", run_github_hakt_test.SUPPORTED_LOOKS)
        self.assertIn("passthrough", run_github_hakt_test.SUPPORTED_LOOKS)

    def test_rec709_passthrough_preserves_studio_shadows_and_lighting(self):
        """grade_video_shot with lookId='none' must preserve pristine Rec.709 dynamic range (<5% shadow clip)."""
        source_video = Path("remotion-app/public/source/test-video.mp4")
        if not source_video.is_file():
            self.skipTest("Source test video not found on disk")

        with tempfile.TemporaryDirectory() as tmpdir:
            out_shot = Path(tmpdir) / "passthrough_shot.mp4"
            plan = looks.select_look(design={"lookId": "none"})
            result_path = looks.grade_video_shot(source_video, out_shot, plan)
            self.assertTrue(result_path.is_file())

            # Extract frame at 7.1s to measure shadow clipping
            proof_frame = Path(tmpdir) / "proof_7.1s.png"
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error",
                "-ss", "7.1", "-i", str(result_path),
                "-vframes", "1", "-q:v", "2", str(proof_frame)
            ], check=True)

            img = cv2.imread(str(proof_frame))
            self.assertIsNotNone(img)

            # Quantitative measurement: shadow clipping (<10) must be < 5.0%
            shadow_clipped_pct = float(np.mean(img < 10) * 100)
            mean_brightness = float(np.mean(img))

            self.assertLess(
                shadow_clipped_pct,
                5.0,
                f"Rec.709 passthrough exhibited excessive shadow clipping: {shadow_clipped_pct:.2f}%",
            )
            self.assertGreater(
                mean_brightness,
                40.0,
                f"Rec.709 passthrough exhibited crushed underexposure: mean={mean_brightness:.2f}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
