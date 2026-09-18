"""Test Suite: Ubicloud Runner Migration & Scope Wall Invariants.

Verifies:
1. .github/workflows/prometheus-render.yml exclusively targets Ubicloud runners (ubicloud-standard-2).
2. Zero legacy GitHub-hosted runners (ubuntu-22.04 / ubuntu-latest) remain in prometheus-render.yml.
3. .github/workflows/fetch-props.yml targets Ubicloud runners (ubicloud-standard-2).
4. Strict Scope Wall enforcement: macro-section files and landscape files are untouched.
5. Render concurrency and slice dispatch latency invariants are preserved.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestUbicloudMigration(unittest.TestCase):
    def test_prometheus_render_workflow_uses_ubicloud_runners(self):
        """prometheus-render.yml must use Ubicloud runners for orchestrate, render_slice, and stitch."""
        wf_path = REPO_ROOT / ".github/workflows/prometheus-render.yml"
        content = wf_path.read_text(encoding="utf-8")

        # Find all runs-on definitions in the workflow
        runs_on_matches = re.findall(r"runs-on:\s*([^\s\n]+)", content)
        self.assertTrue(runs_on_matches, "prometheus-render.yml must define runs-on for its jobs")
        self.assertEqual(len(runs_on_matches), 3, f"Expected 3 jobs with runs-on, found {len(runs_on_matches)}")

        # Every job must use a Ubicloud runner label
        for runner in runs_on_matches:
            self.assertTrue(
                runner.startswith("ubicloud"),
                f"Expected runner to start with 'ubicloud', but got '{runner}'"
            )

        # Specifically ensure legacy runners are gone
        self.assertNotIn("ubuntu-22.04", content, "Legacy ubuntu-22.04 runner found in prometheus-render.yml")
        self.assertNotIn("ubuntu-latest", content, "Legacy ubuntu-latest runner found in prometheus-render.yml")

    def test_fetch_props_workflow_uses_ubicloud_runner(self):
        """fetch-props.yml helper must use Ubicloud runner."""
        wf_path = REPO_ROOT / ".github/workflows/fetch-props.yml"
        content = wf_path.read_text(encoding="utf-8")

        runs_on_matches = re.findall(r"runs-on:\s*([^\s\n]+)", content)
        self.assertTrue(runs_on_matches, "fetch-props.yml must define runs-on")
        for runner in runs_on_matches:
            self.assertTrue(
                runner.startswith("ubicloud"),
                f"Expected runner in fetch-props.yml to start with 'ubicloud', got '{runner}'"
            )

    def test_scope_wall_intact(self):
        """Scope Wall Rule 10: mini-run work must never modify macro files or landscape files."""
        res = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        modified_files = [f.strip() for f in res.stdout.strip().splitlines() if f.strip()]

        for path in modified_files:
            lower = path.lower()
            self.assertNotIn("macro", lower, f"Scope Wall violated: modified macro file {path}")
            self.assertNotIn("landscape", lower, f"Scope Wall violated: modified landscape file {path}")

    def test_render_workflow_latency_invariants_preserved(self):
        """Concurrency <= 2, parallel slices <= 10, and fast path preserved on Ubicloud."""
        wf_path = REPO_ROOT / ".github/workflows/prometheus-render.yml"
        content = wf_path.read_text(encoding="utf-8")

        concurrency_matches = re.findall(r"--concurrency=(\d+)", content)
        self.assertTrue(concurrency_matches, "remotion render must specify --concurrency")
        for c in concurrency_matches:
            self.assertLessEqual(int(c), 2, f"--concurrency={c} exceeds allowed maximum of 2")

        slices_matches = re.findall(r'PARALLEL_SLICES:\s*"(\d+)"', content)
        self.assertTrue(slices_matches, "PARALLEL_SLICES must be defined")
        for s in slices_matches:
            self.assertLessEqual(int(s), 10, f"PARALLEL_SLICES={s} exceeds 10")

        self.assertIn("npm install --legacy-peer-deps --prefer-offline --no-audit --no-fund", content)


if __name__ == "__main__":
    unittest.main()
