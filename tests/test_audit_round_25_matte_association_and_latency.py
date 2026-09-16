"""Round 25 Audit: Strict Subject Matte Association & Cloud Render Latency Optimization.

Verifies:
1. Strict matte identity matching: test-video.mp4 never matches alien female test_matte.webm.
2. Aspect ratio concordance: aspect ratio mismatches (> 5%) are strictly rejected.
3. Canonical podcast matching: MALE-BLACK-TALKING-HEAD-PODCAST matches male_black_matte.webm.
4. GHA render workflow latency invariants: concurrency <= 2, parallel slices <= 10, npm install fast-path.
5. Runner script defaults: parallelSlices is 8, default source is vertical podcast.
"""
from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Provide dummy R2 env vars if not present so gha_orchestrate can be loaded
os.environ.setdefault("R2_ENDPOINT", "https://dummy.r2.cloudflarestorage.com")
os.environ.setdefault("R2_ACCESS_KEY_ID", "dummy_key")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "dummy_secret")

from importlib.machinery import SourceFileLoader

gha_orchestrate_module = SourceFileLoader(
    "gha_orchestrate",
    str(REPO_ROOT / ".github/scripts/gha_orchestrate.py")
).load_module()
resolve_verified_precomputed_matte = gha_orchestrate_module.resolve_verified_precomputed_matte


class TestAuditRound25MatteAndLatency(unittest.TestCase):
    def test_matte_association_rejects_unrelated_test_video(self):
        """test-video.mp4 (bald male speaker) must never be assigned alien test_matte.webm (female speaker)."""
        result = resolve_verified_precomputed_matte(
            src_str="remotion-app/public/source/test-video.mp4",
            expected_width=1280,
            expected_height=720,
            expected_duration_ms=30000,
        )
        self.assertIsNone(
            result,
            "test-video.mp4 must not resolve to any precomputed matte because no valid matching matte exists"
        )

    def test_matte_association_rejects_aspect_mismatch(self):
        """A 9:16 portrait matte must never be composited onto a 16:9 landscape source video."""
        # Even if a file named male_black_talking_head_podcast is requested with 16:9 dimensions:
        result = resolve_verified_precomputed_matte(
            src_str="remotion-app/public/source/MALE-BLACK-TALKING-HEAD-PODCAST.mp4",
            expected_width=1920,
            expected_height=1080,  # 16:9 landscape expected, but matte is 720x1280 (9:16 portrait)
            expected_duration_ms=25000,
        )
        self.assertIsNone(result, "Matte with aspect ratio mismatch must be rejected")

    def test_matte_association_accepts_canonical_podcast_video(self):
        """MALE-BLACK-TALKING-HEAD-PODCAST (720x1280) must cleanly match male_black_matte.webm."""
        result = resolve_verified_precomputed_matte(
            src_str="remotion-app/public/source/MALE-BLACK-TALKING-HEAD-PODCAST.mp4",
            expected_width=720,
            expected_height=1280,
            expected_duration_ms=25000,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "male_black_matte.webm")

    def test_render_workflow_latency_invariants(self):
        """Workflow prometheus-render.yml must use concurrency <= 2, slices <= 10, and skip redundant npm install."""
        wf_path = REPO_ROOT / ".github/workflows/prometheus-render.yml"
        content = wf_path.read_text(encoding="utf-8")

        # Concurrency must be <= 2 to prevent CPU thrashing under software SwANGLE WebGL
        concurrency_matches = re.findall(r"--concurrency=(\d+)", content)
        self.assertTrue(concurrency_matches, "remotion render must specify --concurrency")
        for c in concurrency_matches:
            self.assertLessEqual(int(c), 2, f"--concurrency={c} exceeds maximum allowed concurrency of 2 for 2-vCPU runners")

        # Parallel slices default must be <= 10 to avoid queue throttling and VM provisioning tax
        slices_matches = re.findall(r'PARALLEL_SLICES:\s*"(\d+)"', content)
        self.assertTrue(slices_matches, "PARALLEL_SLICES must be defined")
        for s in slices_matches:
            self.assertLessEqual(int(s), 10, f"PARALLEL_SLICES={s} exceeds 10")

        # npm install fast path: must check whether node_modules already exists
        self.assertIn('if [ ! -d "node_modules/@prometheus" ]; then', content)

    def test_runner_script_defaults(self):
        """run_github_hakt_test.py must configure parallelSlices <= 10 and default to vertical podcast."""
        script_path = REPO_ROOT / "run_github_hakt_test.py"
        content = script_path.read_text(encoding="utf-8")

        self.assertIn('"parallelSlices": 8', content)
        self.assertIn('remotion-app/public/source/MALE-BLACK-TALKING-HEAD-PODCAST.mp4', content)


if __name__ == "__main__":
    unittest.main()
