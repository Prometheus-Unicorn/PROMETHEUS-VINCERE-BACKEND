"""
run_r13_final.py - Dispatches Round 13 Cloud Render with All Addenda to GitHub Actions:
  - Addendum 1: Narrative-beat song handoff trigger (2 song events with crossfade)
  - Addendum 2: Default lookId "none" (original camera natural) + non-skipping pixel A/B gate
  - Addendum 3: Cranial halo guard + binary depth rim + calibrated ambient matte shadow
  - Fixes 1-5: Reverted flank z-order, textVisibility check, structural z-stack, zone diversity cap
Monitors execution, downloads receipt with policyReport, master MP4, and extracts proof keyframes.
"""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO = "italianigris-tech/PROMETHEUS-VINCERE-BACKEND"
WORKFLOW = "prometheus-render.yml"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_ARTIFACT_DIR = Path(r"C:\Users\HomePC\.gemini\antigravity-cli\brain\8ec47dcb-d657-40d5-8c1c-7270878d6444")

JOB_ID = f"gha_hakt_30s_r13_final_{int(time.time())}"

payload = {
    "jobId": JOB_ID,
    "source": {"path": "remotion-app/public/source/test-video.mp4"},
    "selectedWindow": {"sourceStartMs": 0, "sourceEndMs": 30000},
    "maxClipMs": 30000,
    "silencePolicy": "preserve",
    "parallelSlices": 18,
    "metadata": {
        "pipeline": "minirun",
        "jobName": "pbd_30s_hakt_gha_r13_final",
        "lookId": "none",
        "sourceType": "talking_head",
    },
    "design": {
        "aspectRatio": "9:16",
        "typographySystem": "hakt",
        "lookId": "none",
        "lookPolicy": "dynamic",
        "springPhysics": {"damping": 24, "stiffness": 180, "mass": 1.1},
        "specularSheen": True,
        "specularAngle": -35,
        "halationBloom": True,
        "halationSpread": 1.6,
        "backdropCanvas": "paper",
        "canvasTexture": "paper",
        "textureOpacity": 0.18,
        "grainIntensity": 0.08,
        "additiveBlend": True,
        "motionStyle": "cinematic",
        "creativity": "expressive",
        "pacing": "adaptive",
        "typographyBias": "mixed",
        "visualIntensity": 0.95,
        "motif": "electric_cyan",
        "subjectLayering": "auto",
        "pipPolicy": "disabled",
    },
    "audio": {"songPolicy": "auto", "sfxEnabled": True, "cueBus": True},
}

print("=" * 70)
print(f"DISPATCHING ROUND 13 FINAL CLOUD RENDER: {JOB_ID}")
print(f"Commit HEAD: 9431f07")
print(f"Look: none (original camera natural) | Motif: electric_cyan")
print("=" * 70)

payload_json = json.dumps(payload)
payload_b64 = base64.b64encode(payload_json.encode("utf-8")).decode("ascii")
t_start = time.monotonic()

prev_run_id = None
init_res = subprocess.run([
    "gh", "run", "list", "--repo", REPO,
    "--workflow", WORKFLOW,
    "--limit", "1",
    "--json", "databaseId",
], capture_output=True, text=True)
if init_res.returncode == 0:
    try:
        init_runs = json.loads(init_res.stdout)
        if init_runs:
            prev_run_id = init_runs[0]["databaseId"]
    except Exception:
        pass

trigger_cmd = [
    "gh", "workflow", "run", WORKFLOW,
    "--repo", REPO,
    "--field", f"payload_b64={payload_b64}",
]
print("[trigger] Dispatching workflow via gh workflow run...", flush=True)
res = subprocess.run(trigger_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print(f"[trigger] ERROR: {res.stderr}", flush=True)
    sys.exit(1)
print("[trigger] Dispatched! Waiting for new run to appear...", flush=True)

run_id = None
for _ in range(30):
    time.sleep(3)
    list_res = subprocess.run([
        "gh", "run", "list", "--repo", REPO,
        "--workflow", WORKFLOW,
        "--limit", "5",
        "--json", "databaseId,status,conclusion,createdAt",
    ], capture_output=True, text=True)
    if list_res.returncode == 0:
        try:
            runs = json.loads(list_res.stdout)
            for r in runs:
                if r["databaseId"] != prev_run_id:
                    run_id = r["databaseId"]
                    break
            if run_id:
                break
        except Exception:
            pass

if not run_id:
    print("[trigger] ERROR: could not find workflow run ID", flush=True)
    sys.exit(1)

print(f"[trigger] Run ID: {run_id}", flush=True)
print(f"[trigger] Watch URL: https://github.com/{REPO}/actions/runs/{run_id}", flush=True)
print("-" * 70, flush=True)

last_report = time.monotonic()
while True:
    elapsed = time.monotonic() - t_start
    status_res = subprocess.run([
        "gh", "run", "view", str(run_id),
        "--repo", REPO,
        "--json", "status,conclusion",
    ], capture_output=True, text=True)

    if status_res.returncode == 0:
        info = json.loads(status_res.stdout)
        status = info.get("status", "unknown")
        conclusion = info.get("conclusion", "")

        if status == "completed":
            print(f"\n[poll] Run completed in {elapsed:.1f}s — conclusion: {conclusion}", flush=True)
            if conclusion != "success":
                print(f"[poll] ERROR: workflow did not succeed (conclusion={conclusion})", flush=True)
                sys.exit(1)
            break

        if time.monotonic() - last_report >= 30:
            print(f"... running ({elapsed:.0f}s, status={status}) ...", flush=True)
            last_report = time.monotonic()

    time.sleep(10)

artifact_dir = OUTPUT_DIR / JOB_ID
artifact_dir.mkdir(parents=True, exist_ok=True)
print(f"\n[download] Fetching artifacts to {artifact_dir}...", flush=True)
dl_res = subprocess.run([
    "gh", "run", "download", str(run_id),
    "--repo", REPO,
    "--dir", str(artifact_dir),
], capture_output=True, text=True)
if dl_res.returncode != 0:
    print(f"[download] WARNING: {dl_res.stderr}", flush=True)

receipt_files = list(artifact_dir.rglob("*.json"))
mp4_files = list(artifact_dir.rglob("*.mp4"))

receipt = {}
if receipt_files:
    preferred_receipt = None
    for rf in receipt_files:
        if "receipt" in rf.name.lower():
            preferred_receipt = rf
            break
    receipt_file = preferred_receipt or receipt_files[0]
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    out_receipt = OUTPUT_DIR / f"{JOB_ID}_receipt.json"
    out_receipt.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"[download] Receipt -> {out_receipt}", flush=True)
    if BRAIN_ARTIFACT_DIR.exists():
        shutil.copy(out_receipt, BRAIN_ARTIFACT_DIR / "r13_final_receipt.json")
        shutil.copy(out_receipt, BRAIN_ARTIFACT_DIR / "r13_receipt.json")

local_mp4 = None
if mp4_files:
    preferred_mp4 = None
    for mf in mp4_files:
        if "master" in mf.name.lower() or "render" in mf.name.lower():
            preferred_mp4 = mf
            break
    chosen_mp4 = preferred_mp4 or mp4_files[0]
    local_mp4 = OUTPUT_DIR / f"{JOB_ID}_master.mp4"
    shutil.copy(chosen_mp4, local_mp4)
    print(f"[download] Master MP4 -> {local_mp4} ({local_mp4.stat().st_size / (1024 * 1024):.2f} MB)", flush=True)
    shutil.copy(chosen_mp4, OUTPUT_DIR / "master_r13_render.mp4")
    if BRAIN_ARTIFACT_DIR.exists():
        shutil.copy(chosen_mp4, BRAIN_ARTIFACT_DIR / "master_r13_render.mp4")

if local_mp4 and local_mp4.exists():
    print("\n[frames] Extracting proof keyframes...", flush=True)
    timestamps = [1.8, 2.0, 4.6, 8.6, 12.0, 15.0, 18.0, 20.5, 22.5, 24.5, 27.8, 28.0]
    for ts in timestamps:
        frame_file = OUTPUT_DIR / f"{JOB_ID}_frame_{ts:.1f}s.png"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", f"{ts:.3f}", "-i", str(local_mp4),
            "-vframes", "1", "-q:v", "2", str(frame_file)
        ], check=False)
        if frame_file.exists():
            print(f"  Captured {ts:.1f}s -> {frame_file.name}", flush=True)
            if BRAIN_ARTIFACT_DIR.exists():
                shutil.copy(frame_file, BRAIN_ARTIFACT_DIR / f"r13_frame_{ts:.1f}s.png")

total_elapsed = time.monotonic() - t_start
print("\n" + "=" * 70)
print(f"ROUND 13 FINAL CLOUD RENDER COMPLETED in {total_elapsed:.1f}s")
print(f"Run ID: {run_id}")
print(f"Master MP4: {local_mp4}")
print(f"Policy Report in Receipt: {'policyReport' in receipt}")
if "policyReport" in receipt:
    pr = receipt["policyReport"]
    print(f"  policyReport status: {pr.get('status')}")
    print(f"  passedChecks: {pr.get('passedChecks')} / {pr.get('totalChecks')}")
    for k, v in (pr.get("checks") or {}).items():
        print(f"    - {k}: {v.get('status')}")
print("=" * 70)
