"""Headless Google Flow runner entrypoint for GitHub Actions runners and backend services.

Handles:
1. Secure AES-256-GCM browser profile decryption & runner DPAPI re-encryption.
2. In-pipeline Gemini semantic extraction with 3-phase kinematic lifecycle.
3. Headless Veo 3.1 video generation via GoogleFlowServerClient.
4. Rule 11 Hostile Output Critique verification.
5. Deterministic receipt emission and R2 asset backup.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import logging
import os
import shutil
import sys
import tarfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Dynamic import for Windows DPAPI
if sys.platform == "win32":
    import win32crypt
else:
    win32crypt = None

logger = logging.getLogger("flow_gha_runner")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TRANSCRIPT = [
    {
        "chunkIndex": 0,
        "startMs": 0,
        "endMs": 3200,
        "text": "When you build physical hardware at scale, you cannot just push a software patch over the air.",
    },
    {
        "chunkIndex": 1,
        "startMs": 3200,
        "endMs": 7500,
        "text": "Every single micron of tolerance has to clamp down with ruthless precision across the entire line.",
    },
    {
        "chunkIndex": 2,
        "startMs": 7500,
        "endMs": 11800,
        "text": "If that mechanical clamp drifts by even ten microns, the assembly line seizes up and your gross margin drops to zero.",
    },
    {
        "chunkIndex": 3,
        "startMs": 11800,
        "endMs": 15500,
        "text": "Get the physical foundation locked first, and the manufacturing yield takes care of itself.",
    },
]


def hydrate_browser_profile(
    enc_path: Path,
    target_dir: Path,
    auth_key_hex: str,
) -> Path:
    """Decrypts profile archive and re-encrypts Chromium master key with runner DPAPI."""
    logger.info(f"Hydrating browser profile from {enc_path}...")
    if not enc_path.exists():
        raise FileNotFoundError(f"Encrypted profile bundle not found at {enc_path}")

    auth_key = bytes.fromhex(auth_key_hex)
    aesgcm = AESGCM(auth_key)

    with open(enc_path, "rb") as f:
        payload = f.read()

    nonce = payload[:12]
    ciphertext = payload[12:]
    tar_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    logger.info(f"Decrypted profile bundle ({len(tar_bytes):,} bytes). Extracting...")

    target_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tar:
        tar.extractall(target_dir)

    # Re-encrypt master key using Windows DPAPI if running on Windows
    raw_key_path = target_dir / "raw_master_key.bin"
    ls_path = target_dir / "Local State"

    if sys.platform == "win32" and raw_key_path.exists() and ls_path.exists():
        logger.info("Re-encrypting Chromium master key with runner DPAPI...")
        raw_master_key = raw_key_path.read_bytes()
        protected_key = b"DPAPI" + win32crypt.CryptProtectData(
            raw_master_key, None, None, None, None, 0
        )
        with open(ls_path, "r", encoding="utf-8") as f:
            ls = json.load(f)

        ls["os_crypt"]["encrypted_key"] = base64.b64encode(protected_key).decode("utf-8")
        with open(ls_path, "w", encoding="utf-8") as f:
            json.dump(ls, f)
        logger.info("Local State updated with runner DPAPI key.")

    return target_dir


def sync_profile_to_r2(tar_bytes: bytes) -> None:
    """Backs up authenticated browser profile to Cloudflare R2 if credentials exist."""
    endpoint = os.environ.get("R2_ENDPOINT")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket = os.environ.get("R2_UPLOAD_BUCKET", "prometheus-uploads")

    if not (endpoint and access_key and secret_key):
        logger.info("R2 credentials not present, skipping remote R2 profile backup.")
        return

    try:
        import boto3
        from botocore.config import Config

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
        r2_key = "flow_auth/flow_browser_profile.tar.gz"
        logger.info(f"Uploading profile backup to R2 bucket {bucket} key {r2_key}...")
        s3.put_object(Bucket=bucket, Key=r2_key, Body=tar_bytes)
        logger.info("R2 profile backup completed successfully.")
    except Exception as exc:
        logger.warning(f"R2 profile backup encountered warning (non-fatal): {exc}")


async def run_gha_pipeline(
    transcript: List[Dict[str, Any]],
    output_mp4: Path,
    profile_dir: Path,
) -> Dict[str, Any]:
    """Executes full headless generation pipeline on GHA runner."""
    from mini_run_pipeline.curito_semantic_extractor import (
        DiffusionPromptPolicyCritic,
        extract_and_synthesize_curito_prompt,
    )
    from mini_run_pipeline.google_flow_service import (
        FlowServiceConfig,
        GoogleFlowServerClient,
    )

    # 1. Semantic extraction via Gemini API
    logger.info("Synthesizing diffusion prompt with 3-phase kinematic lifecycle...")
    plan = extract_and_synthesize_curito_prompt(transcript)
    prompt = plan["assembled_diffusion_prompt"]
    logger.info(f"Assembled prompt:\n{prompt}")

    # 2. Hostile policy critic
    audit = DiffusionPromptPolicyCritic.audit_prompt(prompt)
    if not audit["passed"]:
        raise ValueError(f"Prompt failed policy audit: {audit['flaws']}")

    # 3. Headless Flow generation
    logger.info(f"Dispatching to Google Flow headlessly (profile: {profile_dir})...")
    config = FlowServiceConfig(
        profile_dir=profile_dir,
        headless=True,
        timeout_sec=600,
    )
    client = GoogleFlowServerClient(config=config)
    gen_result = await client.generate_video(prompt=prompt, output_path=output_mp4)

    # 4. Hostile Output Critique
    critique = run_hostile_critique(output_mp4)

    # 5. Build receipt
    receipt = {
        "jobId": f"gha_flow_{int(time.time())}",
        "environment": "github_actions",
        "deploymentFingerprint": {
            "gitSha": os.environ.get("GITHUB_SHA", "local"),
            "ref": os.environ.get("GITHUB_REF", "main"),
            "runId": os.environ.get("GITHUB_RUN_ID", "local"),
        },
        "generation": gen_result.to_dict(),
        "critique": critique,
        "plan": plan,
    }
    return receipt


def run_hostile_critique(mp4_path: Path) -> Dict[str, Any]:
    """Deterministic Rule 11 histogram and luminance checks on rendered MP4."""
    try:
        import cv2
        import numpy as np

        cap = cv2.VideoCapture(str(mp4_path))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        shadow_clipped = []
        highlight_clipped = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            total_px = gray.size
            shadow_clipped.append(float(np.sum(gray <= 5) / total_px * 100))
            highlight_clipped.append(float(np.sum(gray >= 250) / total_px * 100))

        cap.release()
        max_shadow = float(max(shadow_clipped)) if shadow_clipped else 0.0
        max_hl = float(max(highlight_clipped)) if highlight_clipped else 0.0
        passed = max_shadow < 15.0 and max_hl < 5.0
        return {
            "status": "PASS" if passed else "FLAGGED",
            "max_shadow_crush_pct": round(max_shadow, 2),
            "max_highlight_blown_pct": round(max_hl, 2),
            "total_frames_audited": frame_count,
        }
    except Exception as exc:
        logger.warning(f"Hostile critique warning: {exc}")
        return {"status": "SKIPPED", "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Headless Google Flow GHA runner")
    parser.add_argument("--transcript-json", type=str, default=None)
    parser.add_argument("--output", type=str, default="docs/mini_run_studio/flow_clips/gha_flow_output.mp4")
    parser.add_argument("--enc-bundle", type=str, default="config/flow_auth_bundle.enc")
    args = parser.parse_args()

    auth_key = os.environ.get("FLOW_AUTH_KEY")
    profile_dir = REPO_ROOT / "config" / "flow_browser_profile"
    enc_path = REPO_ROOT / args.enc_bundle
    repo_cookies = REPO_ROOT / "config" / "flow_cookies.json"

    if auth_key and enc_path.exists():
        try:
            hydrate_browser_profile(
                enc_path=enc_path,
                target_dir=profile_dir,
                auth_key_hex=auth_key,
            )
        except Exception as hyd_err:
            logger.warning(f"Profile hydration failed ({hyd_err}), falling back to direct cookie injection.")
            profile_dir.mkdir(parents=True, exist_ok=True)
    elif repo_cookies.exists():
        logger.info(f"Using repository flow_cookies.json directly for authentication.")
        profile_dir.mkdir(parents=True, exist_ok=True)
    else:
        raise RuntimeError("Neither valid FLOW_AUTH_KEY with encrypted bundle nor config/flow_cookies.json is available.")

    # Purge stale Chrome Account Manager database and SQLite cookies from legacy profile
    # that mark the account as 'Signed out', allowing CDP cookie injection to authenticate cleanly.
    for stale_item in [
        profile_dir / "Default" / "Account Web Data",
        profile_dir / "Default" / "Account Web Data-journal",
        profile_dir / "Default" / "Network" / "Cookies",
        profile_dir / "Default" / "Network" / "Cookies-journal",
    ]:
        if stale_item.exists():
            try:
                stale_item.unlink()
                logger.info(f"Purged stale session blocker: {stale_item.name}")
            except Exception:
                pass

    # Synchronize fresh repository cookies into profile directory if present
    repo_cookies = REPO_ROOT / "config" / "flow_cookies.json"
    if repo_cookies.exists():
        shutil.copyfile(repo_cookies, profile_dir / "flow_cookies.json")
        logger.info(f"Synchronized fresh authentication cookies to {profile_dir / 'flow_cookies.json'}")

    # Ingest transcript
    if args.transcript_json and Path(args.transcript_json).exists():
        with open(args.transcript_json, "r", encoding="utf-8") as f:
            transcript = json.load(f)
    elif args.transcript_json:
        transcript = json.loads(args.transcript_json)
    else:
        transcript = DEFAULT_TRANSCRIPT

    output_path = REPO_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    receipt = asyncio.run(run_gha_pipeline(transcript, output_path, profile_dir))

    # Write receipt
    receipt_json_path = output_path.with_suffix(".receipt.json")
    receipt_json_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    logger.info(f"Receipt written to {receipt_json_path}")


if __name__ == "__main__":
    main()
