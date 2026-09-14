"""Tests for google_flow_bridge.py — JSON protocol, job file round-trip, command dispatch."""

from __future__ import annotations

import json
import sys
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def _call_bridge(payload: dict, timeout: float = 15.0) -> dict:
    raw = json.dumps(payload) + "\n"
    r = subprocess.run(
        [sys.executable, "-m", "mini_run_pipeline.google_flow_bridge"],
        input=raw,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(_REPO),
    )
    assert r.returncode == 0, f"Bridge exited {r.returncode}: {r.stderr[:300]}"
    return json.loads(r.stdout.strip().split("\n")[-1])


class TestGoogleFlowBridge(unittest.TestCase):

    def test_unknown_command_returns_error(self):
        result = _call_bridge({"command": "nonexistent", "args": {}})
        self.assertIn("error", result)
        self.assertIn("nonexistent", result["error"])

    def test_empty_input_returns_error(self):
        r = subprocess.run(
            [sys.executable, "-m", "mini_run_pipeline.google_flow_bridge"],
            input="\n",
            capture_output=True,
            text=True,
            timeout=8,
            cwd=str(_REPO),
        )
        result = json.loads(r.stdout.strip())
        self.assertIn("error", result)

    def test_poll_status_unknown_job(self):
        result = _call_bridge({"command": "poll_status", "args": {"job_id": "nonexistent_xyz"}})
        self.assertIn("error", result)
        self.assertIn("nonexistent_xyz", result["error"])

    def test_download_asset_unknown_job(self):
        result = _call_bridge({"command": "download_asset", "args": {"job_id": "ghost_job_999"}})
        self.assertIn("error", result)

    def test_generate_video_empty_prompt_returns_error(self):
        result = _call_bridge({"command": "generate_video", "args": {"prompt": "   "}})
        self.assertIn("error", result)

    def test_generate_video_dispatches_and_writes_job_file(self):
        result = _call_bridge({
            "command": "generate_video",
            "args": {
                "prompt": "Dark cinematic void",
                "duration_sec": 6,
                "aspect_ratio": "9:16",
            }
        })

        # Must return immediately with dispatched status
        self.assertNotIn("error", result, f"Unexpected error: {result.get('error')}")
        self.assertEqual(result["status"], "GENERATION_DISPATCHED")
        self.assertIn("jobId", result)
        self.assertIn("dispatchedAt", result)

        job_id = result["jobId"]

        # Job file must exist
        job_file = _REPO / "docs" / "mini_run_studio" / "flow_clips" / ".jobs" / f"{job_id}.json"
        self.assertTrue(job_file.exists(), f"Job file not written: {job_file}")

        job_data = json.loads(job_file.read_text())
        self.assertEqual(job_data["jobId"], job_id)
        self.assertEqual(job_data["prompt"], "Dark cinematic void")
        self.assertIn(job_data["status"], {"GENERATION_DISPATCHED", "GENERATING", "COMPLETE", "FAILED"})

    def test_poll_status_reflects_job_file(self):
        # First dispatch a job
        gen = _call_bridge({
            "command": "generate_video",
            "args": {"prompt": "Minimal glowing headline", "duration_sec": 6}
        })
        self.assertNotIn("error", gen)
        job_id = gen["jobId"]

        # Poll immediately — should show dispatched or generating
        poll = _call_bridge({"command": "poll_status", "args": {"job_id": job_id}})
        self.assertNotIn("error", poll, f"poll_status returned error: {poll}")
        self.assertEqual(poll["jobId"], job_id)
        self.assertIn(poll["status"], {"GENERATION_DISPATCHED", "GENERATING", "COMPLETE", "FAILED"})

    def test_bridge_exits_fast_for_poll(self):
        """Bridge must respond in under 6s (3s for python startup + protocol)."""
        import time
        start = time.time()
        _call_bridge({"command": "poll_status", "args": {"job_id": "speed_test_job"}})
        elapsed = time.time() - start
        self.assertLess(elapsed, 6.0, f"Bridge took {elapsed:.2f}s — too slow")


if __name__ == "__main__":
    unittest.main()
