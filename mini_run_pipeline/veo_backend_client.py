"""Native Headless Google Veo 3.1 API Client for Prometheus Backend.

Provides 100% headless, zero-browser generative video generation using the official
Google GenAI SDK (google-genai). Designed specifically for backend servers, cloud runners,
and automated containerized environments (GitHub Actions, Docker, Linux VPS).

Supported Models:
- models/veo-3.1-fast-generate-preview (Fast 9:16 vertical generative video)
- models/veo-3.1-generate-preview (High-fidelity cinema cadence)
- models/nano-banana-pro-preview (Facial & multimodal expression blendshapes)

Eliminates all browser scraping, Playwright dependencies, and mock synthesizers.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from .curito_animation_dna import CuritoStitchedPrompt

logger = logging.getLogger("veo_backend_client")


@dataclass
class VeoGenerationResult:
    """Receipt and output artifact metadata from a native Veo 3.1 generation."""
    mp4_path: str
    duration_sec: int
    aspect_ratio: str
    model: str
    file_size_bytes: int
    operation_name: str
    prompt: str
    completed_at: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mp4Path": self.mp4_path,
            "durationSec": self.duration_sec,
            "aspectRatio": self.aspect_ratio,
            "model": self.model,
            "fileSizeBytes": self.file_size_bytes,
            "operationName": self.operation_name,
            "prompt": self.prompt,
            "completedAt": self.completed_at,
        }


class VeoBackendClient:
    """Native headless video generation client using the official Google GenAI SDK."""

    DEFAULT_MODEL = "veo-3.1-fast-generate-preview"
    DEFAULT_ASPECT_RATIO = "9:16"
    DEFAULT_FPS = 24

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._resolve_api_key()
        if not self.api_key:
            raise RuntimeError(
                "GOOGLE_AI_STUDIO_API_KEY / GEMINI_API_KEY is not configured in environment or .env file."
            )
        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def _resolve_api_key() -> Optional[str]:
        """Resolves API key from environment variables or .env file."""
        key = os.getenv("GOOGLE_AI_STUDIO_API_KEY") or os.getenv("GEMINI_API_KEY")
        if key and key.strip():
            return key.strip()

        env_file = Path(__file__).resolve().parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if line.startswith("GOOGLE_AI_STUDIO_API_KEY=") or line.startswith("GEMINI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        return None

    def generate_curito_video(
        self,
        prompt: CuritoStitchedPrompt | str,
        output_path: Path,
        duration_sec: int = 5,
        aspect_ratio: str = "9:16",
        fps: int = 24,
        model: Optional[str] = None,
        reference_image_bytes: Optional[bytes] = None,
        poll_interval_sec: int = 10,
        timeout_sec: int = 600,
    ) -> VeoGenerationResult:
        """Executes a 100% headless video generation call to Google's Veo 3.1 infrastructure.

        Args:
            prompt: CuritoStitchedPrompt object or prompt string.
            output_path: Destination path for the downloaded MP4 video.
            duration_sec: Video length in seconds (5, 6, or 8).
            aspect_ratio: Vertical framing, default '9:16'.
            fps: Native cinema cadence, default 24.
            model: Veo model name (default: veo-3.1-fast-generate-preview).
            reference_image_bytes: Optional raw PNG/JPEG image bytes for outfit/frame conditioning.
            poll_interval_sec: Polling interval while operation runs in Google's cloud.
            timeout_sec: Maximum wait time before raising TimeoutError.

        Returns:
            VeoGenerationResult containing metadata and verified output path.

        Raises:
            PermissionError: If API quota is exhausted (429) with actionable billing instructions.
            RuntimeError: If generation fails or Google Cloud rejects the request.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        target_model = model or self.DEFAULT_MODEL
        prompt_text = prompt.full_prompt if isinstance(prompt, CuritoStitchedPrompt) else str(prompt)

        # Build config (fps is internal 24fps in Gemini Developer API mode; Veo accepts discrete durations: 4, 6, 8)
        veo_dur = 4 if duration_sec <= 4 else (6 if duration_sec <= 6 else 8)
        config_kwargs: Dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "duration_seconds": veo_dur,
        }

        if reference_image_bytes:
            ref_img = types.VideoGenerationReferenceImage(
                image=types.Image(image_bytes=reference_image_bytes)
            )
            config_kwargs["reference_images"] = [ref_img]

        config = types.GenerateVideosConfig(**config_kwargs)

        logger.info(
            f"Dispatching headless Veo 3.1 generation: model={target_model}, "
            f"duration={duration_sec}s, aspect_ratio={aspect_ratio}"
        )

        try:
            operation = self.client.models.generate_videos(
                model=target_model,
                prompt=prompt_text,
                config=config,
            )
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                raise PermissionError(
                    f"VEO 3.1 API QUOTA EXHAUSTED: Google AI Studio returned 429 RESOURCE_EXHAUSTED. "
                    f"To enable headless video generation in production, link a Google Cloud Billing "
                    f"account (Pay-as-you-go) to your project at: https://ai.google.dev/gemini-api/docs/rate-limits"
                ) from e
            raise RuntimeError(f"Veo 3.1 API generation dispatch failed: {e}") from e

        # Poll operation
        start_time = time.time()
        logger.info(f"Veo 3.1 operation dispatched: {operation.name}. Polling...")

        while not operation.done:
            elapsed = int(time.time() - start_time)
            if elapsed > timeout_sec:
                raise TimeoutError(
                    f"Veo 3.1 video generation timed out after {elapsed}s (Operation: {operation.name})"
                )
            time.sleep(poll_interval_sec)
            try:
                operation = self.client.operations.get(operation)
            except Exception as poll_err:
                logger.warning(f"Error checking Veo operation status: {poll_err}")

        # Check for errors in completed operation
        if operation.error:
            raise RuntimeError(f"Veo 3.1 generation failed: {operation.error}")

        # Download video
        result = operation.result
        if not result or not result.generated_videos:
            raise RuntimeError("Veo 3.1 generation completed but returned zero generated videos.")

        generated_video = result.generated_videos[0]
        video_bytes = generated_video.video.video_bytes

        if not video_bytes or len(video_bytes) < 1000:
            raise RuntimeError(f"Veo 3.1 returned empty or corrupt video payload ({len(video_bytes or b'')} bytes).")

        output_path.write_bytes(video_bytes)
        file_size = output_path.stat().st_size

        logger.info(f"SUCCESS: Downloaded native Veo 3.1 MP4 -> {output_path} ({file_size:,} bytes)")

        return VeoGenerationResult(
            mp4_path=str(output_path.resolve()),
            duration_sec=duration_sec,
            aspect_ratio=aspect_ratio,
            model=target_model,
            file_size_bytes=file_size,
            operation_name=operation.name,
            prompt=prompt_text,
            completed_at=time.time(),
        )
