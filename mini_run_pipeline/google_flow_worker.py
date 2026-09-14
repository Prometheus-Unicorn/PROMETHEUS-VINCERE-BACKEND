"""Google Flow Worker — long-lived detached process that drives Playwright.

Spawned by google_flow_bridge.py. Reads the job spec file, runs the Playwright
automation to Google Flow, and writes progress/completion back to the same job file.

Usage (internal — called by bridge):
  python -m mini_run_pipeline.google_flow_worker <path/to/job_file.json>
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _update_job(job_file: Path, updates: dict) -> None:
    try:
        data = json.loads(job_file.read_text(encoding="utf-8")) if job_file.exists() else {}
        data.update(updates)
        job_file.write_text(json.dumps(data), encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"[flow_worker] Failed to write job file: {e}\n")


async def run(job_file: Path) -> None:
    data = json.loads(job_file.read_text(encoding="utf-8"))

    job_id = data["jobId"]
    prompt = data["prompt"]
    duration_sec = int(data.get("duration_sec", 6))
    output_filename = data.get("output_filename") or f"flow_{job_id}.mp4"

    output_dir = _REPO_ROOT / "docs" / "mini_run_studio" / "flow_clips"
    output_dir.mkdir(parents=True, exist_ok=True)

    _update_job(job_file, {"status": "GENERATING", "progressPercent": 5})

    try:
        # Lazy import — Playwright only needed inside the worker
        from mini_run_pipeline.google_flow_automation import GoogleFlowBrowserEngine

        engine = GoogleFlowBrowserEngine(
            headless=True,
            output_dir=output_dir,
        )

        _update_job(job_file, {"progressPercent": 10, "status": "GENERATING"})

        dest: Path = await engine.generate_video(
            prompt=prompt,
            output_filename=output_filename,
            duration_sec=duration_sec,
            aspect_ratio=data.get("aspect_ratio", "9:16"),
            timeout_sec=600,
        )

        _update_job(job_file, {
            "status": "COMPLETE",
            "progressPercent": 100,
            "mp4Path": str(dest.resolve()),
            "completedAt": time.time(),
        })

    except Exception as exc:
        _update_job(job_file, {
            "status": "FAILED",
            "error": str(exc),
            "progressPercent": 0,
        })
        sys.stderr.write(f"[flow_worker] FAILED job {job_id}: {exc}\n")
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write("[flow_worker] Usage: python -m mini_run_pipeline.google_flow_worker <job_file>\n")
        sys.exit(1)

    job_file = Path(sys.argv[1])
    if not job_file.exists():
        sys.stderr.write(f"[flow_worker] Job file not found: {job_file}\n")
        sys.exit(1)

    asyncio.run(run(job_file))


if __name__ == "__main__":
    main()
