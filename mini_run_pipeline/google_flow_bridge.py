"""Google Flow MCP Bridge — stdin/stdout JSON protocol adapter.

Called by the TypeScript MCP gateway (backend/src/gateway/tools.ts) via child_process.
Reads one JSON line from stdin: {"command": "...", "args": {...}}
Writes one JSON result line to stdout.

Supported commands:
  generate_video  — dispatches Playwright browser automation to Google Flow
  poll_status     — checks the generation state of a known job
  download_asset  — downloads the finished MP4 to the output dir
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Setup path so module runs from repo root
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mini_run_pipeline.google_flow_automation import GoogleFlowBrowserEngine  # noqa: E402

# In-process job state (lives for the duration of the bridge process; gateway holds jobIds)
_ACTIVE_JOBS: dict[str, dict] = {}

OUTPUT_DIR = Path("docs/mini_run_studio/flow_clips")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def _cmd_generate_video(args: dict) -> dict:
    prompt: str = args.get("prompt", "")
    duration_sec: int = int(args.get("duration_sec", 6))
    aspect_ratio: str = args.get("aspect_ratio", "9:16")
    model: str = args.get("model", "Veo 3.1 - Fast")
    output_filename: str = args.get("output_filename") or f"flow_{int(time.time() * 1000)}.mp4"

    if not prompt.strip():
        return {"error": "prompt cannot be empty"}

    job_id = f"flow_vid_{int(time.time() * 1000)}"

    # Register job
    _ACTIVE_JOBS[job_id] = {
        "jobId": job_id,
        "status": "GENERATION_DISPATCHED",
        "progressPercent": 0,
        "prompt": prompt,
        "duration_sec": duration_sec,
        "aspect_ratio": aspect_ratio,
        "model": model,
        "output_filename": output_filename,
        "dispatchedAt": time.time(),
        "mp4Path": None,
    }

    # Fire-and-forget: launch browser automation in background
    # (bridge process stays alive — TypeScript will poll via separate invocations)
    asyncio.ensure_future(_run_generation(job_id))

    return {
        "jobId": job_id,
        "status": "GENERATION_DISPATCHED",
        "prompt": prompt,
        "durationSec": duration_sec,
        "aspectRatio": aspect_ratio,
        "model": model,
        "dispatchedAt": _ACTIVE_JOBS[job_id]["dispatchedAt"],
    }


async def _run_generation(job_id: str) -> None:
    """Background task: drives Playwright automation and marks job complete."""
    job = _ACTIVE_JOBS.get(job_id)
    if not job:
        return

    try:
        job["status"] = "GENERATING"
        job["progressPercent"] = 10

        engine = GoogleFlowBrowserEngine(
            headless=True,
            output_dir=OUTPUT_DIR,
        )

        dest = await engine.generate_video(
            prompt=job["prompt"],
            output_filename=job["output_filename"],
            duration_sec=job["duration_sec"],
            aspect_ratio=job["aspect_ratio"],
            timeout_sec=600,
        )

        job["status"] = "COMPLETE"
        job["progressPercent"] = 100
        job["mp4Path"] = str(dest)

    except Exception as exc:
        job["status"] = "FAILED"
        job["error"] = str(exc)


async def _cmd_poll_status(args: dict) -> dict:
    job_id = args.get("job_id", "")
    job = _ACTIVE_JOBS.get(job_id)
    if not job:
        return {"error": f"Unknown jobId: {job_id}"}
    return {
        "jobId": job_id,
        "status": job["status"],
        "progressPercent": job.get("progressPercent", 0),
        "message": job.get("error", ""),
        "mp4Path": job.get("mp4Path"),
    }


async def _cmd_download_asset(args: dict) -> dict:
    job_id = args.get("job_id", "")
    job = _ACTIVE_JOBS.get(job_id)
    if not job:
        return {"error": f"Unknown jobId: {job_id}"}
    if job["status"] != "COMPLETE" or not job.get("mp4Path"):
        return {"error": f"Job {job_id} is not complete yet (status={job['status']})"}

    mp4_path = Path(job["mp4Path"])
    size = mp4_path.stat().st_size if mp4_path.exists() else 0
    return {
        "jobId": job_id,
        "mp4Path": str(mp4_path.resolve()),
        "sizeBytes": size,
        "status": "DOWNLOADED",
    }


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_COMMANDS = {
    "generate_video": _cmd_generate_video,
    "poll_status": _cmd_poll_status,
    "download_asset": _cmd_download_asset,
}


async def main() -> None:
    raw = sys.stdin.readline().strip()
    if not raw:
        print(json.dumps({"error": "empty input"}), flush=True)
        return

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON parse error: {e}"}), flush=True)
        return

    command = payload.get("command", "")
    args = payload.get("args", {})

    handler = _COMMANDS.get(command)
    if not handler:
        print(json.dumps({"error": f"Unknown command: {command}"}), flush=True)
        return

    try:
        result = await handler(args)
        print(json.dumps(result), flush=True)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
