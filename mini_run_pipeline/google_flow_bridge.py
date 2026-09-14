"""Google Flow MCP Bridge — stdin/stdout JSON protocol adapter.

Called by the TypeScript MCP gateway (backend/src/gateway/tools.ts) via child_process.
Reads one JSON line from stdin: {"command": "...", "args": {...}}
Writes one JSON result line to stdout and exits immediately.

Supported commands:
  generate_video  — writes a job spec file and spawns a detached worker process
  poll_status     — reads the job state file written by the worker
  download_asset  — verifies MP4 exists and returns path + size

Worker pattern:
  generate_video spawns `python -m mini_run_pipeline.google_flow_worker <job_file>`
  with DETACHED creation flags (no wait). The worker writes a JSON state file at
  OUTPUT_DIR/.jobs/<jobId>.json which poll_status reads.
  This way the bridge process exits in <50ms — no event-loop hang.

No Playwright or asyncio is imported at the top level; everything heavy is
in google_flow_worker.py (the long-lived detached process).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

OUTPUT_DIR = _REPO_ROOT / "docs" / "mini_run_studio" / "flow_clips"
JOBS_DIR = OUTPUT_DIR / ".jobs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _job_file(job_id: str) -> Path:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    return JOBS_DIR / f"{job_id}.json"


def _write_job(job_id: str, data: dict) -> None:
    _job_file(job_id).write_text(json.dumps(data), encoding="utf-8")


def _read_job(job_id: str) -> dict | None:
    p = _job_file(job_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Command handlers (all synchronous — bridge exits after one command)
# ---------------------------------------------------------------------------

def cmd_generate_video(args: dict) -> dict:
    prompt: str = args.get("prompt", "").strip()
    if not prompt:
        return {"error": "prompt cannot be empty"}

    duration_sec: int = int(args.get("duration_sec", 6))
    aspect_ratio: str = args.get("aspect_ratio", "9:16")
    model: str = args.get("model", "Veo 3.1 - Fast")
    output_filename: str = args.get("output_filename") or f"flow_{int(time.time() * 1000)}.mp4"

    job_id = f"flow_vid_{int(time.time() * 1000)}"
    dispatched_at = time.time()

    # Write initial job state
    job_data = {
        "jobId": job_id,
        "status": "GENERATION_DISPATCHED",
        "progressPercent": 0,
        "prompt": prompt,
        "duration_sec": duration_sec,
        "aspect_ratio": aspect_ratio,
        "model": model,
        "output_filename": output_filename,
        "dispatchedAt": dispatched_at,
        "mp4Path": None,
        "error": None,
    }
    _write_job(job_id, job_data)

    # Spawn detached worker (no wait — worker updates the job state file)
    worker_cmd = [
        sys.executable, "-m", "mini_run_pipeline.google_flow_worker",
        str(_job_file(job_id))
    ]
    creation_flags = 0
    if sys.platform == "win32":
        import subprocess
        creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    import subprocess as _sp
    _sp.Popen(
        worker_cmd,
        cwd=str(_REPO_ROOT),
        stdin=_sp.DEVNULL,
        stdout=_sp.DEVNULL,
        stderr=_sp.DEVNULL,
        creationflags=creation_flags,
        close_fds=(sys.platform != "win32"),
    )

    return {
        "jobId": job_id,
        "status": "GENERATION_DISPATCHED",
        "prompt": prompt,
        "durationSec": duration_sec,
        "aspectRatio": aspect_ratio,
        "model": model,
        "dispatchedAt": dispatched_at,
    }


def cmd_poll_status(args: dict) -> dict:
    job_id = args.get("job_id", "").strip()
    if not job_id:
        return {"error": "job_id is required"}
    job = _read_job(job_id)
    if job is None:
        return {"error": f"Unknown jobId: {job_id}"}
    return {
        "jobId": job_id,
        "status": job.get("status", "UNKNOWN"),
        "progressPercent": job.get("progressPercent", 0),
        "message": job.get("error") or "",
        "mp4Path": job.get("mp4Path"),
    }


def cmd_download_asset(args: dict) -> dict:
    job_id = args.get("job_id", "").strip()
    if not job_id:
        return {"error": "job_id is required"}
    job = _read_job(job_id)
    if job is None:
        return {"error": f"Unknown jobId: {job_id}"}
    if job.get("status") != "COMPLETE" or not job.get("mp4Path"):
        return {"error": f"Job {job_id} not complete yet (status={job.get('status')})"}

    mp4_path = Path(job["mp4Path"])
    size = mp4_path.stat().st_size if mp4_path.exists() else 0
    return {
        "jobId": job_id,
        "mp4Path": str(mp4_path.resolve()),
        "sizeBytes": size,
        "status": "DOWNLOADED",
    }


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_COMMANDS = {
    "generate_video": cmd_generate_video,
    "poll_status": cmd_poll_status,
    "download_asset": cmd_download_asset,
}


def main() -> None:
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
        print(json.dumps({"error": f"Unknown command: {command}. Valid: {list(_COMMANDS)}"}), flush=True)
        return

    try:
        result = handler(args)
        print(json.dumps(result), flush=True)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), flush=True)


if __name__ == "__main__":
    main()
