"""Curito Animation Orchestration Engine for Mini-Runs.

Orchestrates the complete lifecycle of generative Curito animations:
1. Candidate Detection: Evaluates transcript chunks to identify moments optimal for animation
   (high abstract framework weight, system architecture, inflection turning points).
2. Word-Sync & Timestamp Calculation: Computes relative offsets (e.g. +3.0s into the segment)
   for spoken phrase synchrony.
3. DNA Genome Stitching: Stitches modular visual, lighting, camera, and scene genomes into
   proven 6-part Google Flow prompts.
4. Google Flow MCP Generation: Invokes Google Flow MCP to generate, monitor, and download MP4 assets.
5. Mini-Run Background Layer Integration: Formats placement directives to composite the animation
   as a background video / cutaway layer on the timeline.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .broll_engine import BrollSuitabilityEngine
from .curito_animation_dna import (
    CURITO_TREATMENT_FAMILY,
    CuritoOutfitReference,
    CuritoPromptStitcher,
    CuritoSentimentBlendShape,
    CuritoWordSyncCalculator,
    CuritoWordSyncSchema,
)
from .curito_semantic_extractor import (
    DiffusionPromptPolicyCritic,
    extract_and_synthesize_curito_prompt,
)
from .google_flow_client import CuritoAnimationReport, GoogleFlowConfig, GoogleFlowMCPClient
from .veo_backend_client import VeoBackendClient, VeoGenerationResult


# ---------------------------------------------------------------------------
# Placement Directive Model
# ---------------------------------------------------------------------------

@dataclass
class CuritoPlacementDirective:
    """Timeline placement directive for compositing a Curito animation into a mini-run video."""
    id: str
    chunk_index: int
    concept_title: str
    timeline_start_ms: int
    timeline_end_ms: int
    duration_ms: int
    duration_sec: int
    treatment_family: str
    mp4_path: str
    word_sync: CuritoWordSyncSchema
    genomes_used: List[str]
    report_json_path: str
    report_md_path: str
    composite_layer: str = "background_video_cutaway"
    blend_mode: str = "normal"
    opacity: float = 1.0
    relative_asset_path: Optional[str] = None
    outfit_reference: Optional[CuritoOutfitReference] = None
    sentiment_blendshape: Optional[CuritoSentimentBlendShape] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "id": self.id,
            "chunkIndex": self.chunk_index,
            "conceptTitle": self.concept_title,
            "timelineStartMs": self.timeline_start_ms,
            "timelineEndMs": self.timeline_end_ms,
            "durationMs": self.duration_ms,
            "durationSec": self.duration_sec,
            "treatmentFamily": self.treatment_family,
            "mp4Path": str(self.mp4_path),
            "relativeAssetPath": self.relative_asset_path or str(self.mp4_path),
            "wordSync": self.word_sync.to_dict(),
            "genomesUsed": self.genomes_used,
            "reportJsonPath": str(self.report_json_path),
            "reportMdPath": str(self.report_md_path),
            "compositeLayer": self.composite_layer,
            "blendMode": self.blend_mode,
            "opacity": self.opacity,
        }
        if self.outfit_reference:
            res["outfitReference"] = self.outfit_reference.to_dict()
            res["outfit_reference"] = self.outfit_reference.to_dict()
        if self.sentiment_blendshape:
            res["sentimentBlendshape"] = self.sentiment_blendshape.to_dict()
            res["sentiment_blendshape"] = self.sentiment_blendshape.to_dict()
        return res


# ---------------------------------------------------------------------------
# Candidate Detection Engine
# ---------------------------------------------------------------------------

class CuritoAnimationDetector:
    """Evaluates transcript chunks to detect prime candidates for generative animations."""

    # High conceptual affinity tokens that trigger Curito animation evaluation
    ANIMATION_AFFINITY_TOKENS = {
        "framework", "system", "algorithm", "strategy", "breakthrough", "architecture",
        "solution", "leverage", "engine", "scale", "feedback", "pillar", "code",
        "loop", "execution", "discipline", "principle", "asymmetry", "experiment",
        "process", "mechanism", "growth", "revenue", "secrets", "formula",
    }

    @classmethod
    def evaluate_chunk_for_animation(
        cls,
        chunk: Dict[str, Any],
        chunk_index: int = 0,
        time_since_last_animation_sec: float = 100.0,
    ) -> Tuple[bool, float, str]:
        """Evaluate if a monologue chunk is ideal for getting animated.
        
        Returns:
            (is_candidate, score, rationale)
        """
        text = str(chunk.get("text") or "").strip()
        start_ms = int(chunk.get("startMs") or 0)
        end_ms = int(chunk.get("endMs") or (start_ms + 4000))
        dur_sec = max(0.1, (end_ms - start_ms) / 1000.0)

        # 1. Check B-roll suitability engine recommendation
        broll_eval = BrollSuitabilityEngine.evaluate_chunk(
            chunk_index=chunk_index,
            text=text,
            duration_sec=dur_sec,
            time_since_last_broll_sec=time_since_last_animation_sec,
            time_since_last_visual_break_sec=time_since_last_animation_sec,
        )

        tokens = {t.lower().strip(".,!?:;\"'") for t in text.split() if t}
        matched_affinity = tokens.intersection(cls.ANIMATION_AFFINITY_TOKENS)

        score = broll_eval.abstract_penalty + (len(matched_affinity) * 0.20)

        # If broll_engine recommended motion_graphic or if high concept affinity tokens match
        if broll_eval.recommended_treatment_category == "motion_graphic" or len(matched_affinity) >= 1:
            if dur_sec >= 1.8:
                rationale = (
                    f"Candidate identified: {len(matched_affinity)} concept tokens matched "
                    f"({', '.join(sorted(matched_affinity)) or 'motion graphics affinity'}). "
                    f"Duration {dur_sec:.1f}s allows proper visual staging."
                )
                return True, min(1.0, score + 0.3), rationale

        return False, score, "Insufficient conceptual weight for animation."


# ---------------------------------------------------------------------------
# Curito Animation Orchestrator
# ---------------------------------------------------------------------------

class CuritoAnimationOrchestrator:
    """Orchestrates candidate detection, prompt stitching, generation, and timeline integration."""

    def __init__(
        self,
        client: Optional[Any] = None,
        veo_client: Optional[VeoBackendClient] = None,
        flow_client: Optional[GoogleFlowMCPClient] = None,
        output_dir: Optional[str | Path] = None,
        fixture_video_path: Optional[str | Path] = None,
    ):
        self.output_dir = Path(output_dir or "docs/mini_run_studio/flow_clips")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = client
        self.veo_client = veo_client
        self.flow_client = flow_client
        self.fixture_video_path = Path(fixture_video_path) if fixture_video_path else None

        # Resolve fixture from env if set
        if not self.fixture_video_path and os.getenv("CURITO_FIXTURE_VIDEO"):
            cand = Path(os.getenv("CURITO_FIXTURE_VIDEO"))
            if cand.exists():
                self.fixture_video_path = cand

        # Default resolution: prioritize native headless VeoBackendClient if available
        if self.client is None and self.veo_client is None and self.flow_client is None and self.fixture_video_path is None:
            try:
                self.veo_client = VeoBackendClient()
            except Exception:
                # Fallback to GoogleFlowMCPClient
                self.flow_client = GoogleFlowMCPClient(GoogleFlowConfig(output_dir=str(self.output_dir)))

    def _build_report_from_existing_mp4(
        self,
        dest_mp4: Path,
        prompt: Any,
        word_sync: CuritoWordSyncSchema,
        concept_title: str,
    ) -> CuritoAnimationReport:
        storyboard = GoogleFlowMCPClient.build_storyboard_breakdown(prompt, word_sync)
        job_id = f"curito_clip_{dest_mp4.stem}"
        report = CuritoAnimationReport(
            job_id=job_id,
            treatment_family=CURITO_TREATMENT_FAMILY,
            concept_title=concept_title,
            project_name=f"Prometheus_{dest_mp4.stem}",
            account_email="headless-api@google.genai",
            model=getattr(prompt, "model", "Veo 3.1 - Fast"),
            duration_sec=word_sync.total_duration_sec,
            aspect_ratio=getattr(prompt, "aspect_ratio", "9:16"),
            prompt=prompt,
            word_sync=word_sync,
            storyboard_beats=storyboard,
            mp4_asset_path=str(dest_mp4.resolve()),
            generated_at=time.time(),
            status="SUCCESS",
        )
        json_report_path = dest_mp4.parent / f"{dest_mp4.stem}_report.json"
        md_report_path = dest_mp4.parent / f"{dest_mp4.stem}_report.md"
        json_report_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        md_report_path.write_text(report.render_markdown_summary(), encoding="utf-8")
        return report

    def _build_report_from_veo_result(
        self,
        veo_result: VeoGenerationResult,
        prompt: Any,
        word_sync: CuritoWordSyncSchema,
        concept_title: str,
    ) -> CuritoAnimationReport:
        dest_mp4 = Path(veo_result.mp4_path)
        storyboard = GoogleFlowMCPClient.build_storyboard_breakdown(prompt, word_sync)
        clean_op = veo_result.operation_name.replace("/", "_")
        report = CuritoAnimationReport(
            job_id=clean_op,
            treatment_family=CURITO_TREATMENT_FAMILY,
            concept_title=concept_title,
            project_name=f"Prometheus_Veo_{clean_op[-8:]}",
            account_email="headless-api@google.genai",
            model=veo_result.model,
            duration_sec=veo_result.duration_sec,
            aspect_ratio=veo_result.aspect_ratio,
            prompt=prompt,
            word_sync=word_sync,
            storyboard_beats=storyboard,
            mp4_asset_path=str(dest_mp4.resolve()),
            generated_at=veo_result.completed_at,
            status="SUCCESS",
        )
        json_report_path = dest_mp4.parent / f"{dest_mp4.stem}_report.json"
        md_report_path = dest_mp4.parent / f"{dest_mp4.stem}_report.md"
        json_report_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        md_report_path.write_text(report.render_markdown_summary(), encoding="utf-8")
        return report

    def plan_and_generate_animation(
        self,
        chunk: Dict[str, Any],
        chunk_index: int,
        target_phrase: Optional[str] = None,
        sync_offset_sec: Optional[float] = 3.0,
        concept_title: Optional[str] = None,
        outfit_reference: Optional[CuritoOutfitReference] = None,
        sentiment_blendshape: Optional[CuritoSentimentBlendShape] = None,
        extrapolate_hold_sec: Optional[float] = None,
        model: str = "Veo 3.1 - Fast",
        aspect_ratio: str = "9:16",
    ) -> CuritoPlacementDirective:
        """Execute the complete generation and return the placement directive.
        
        Args:
            chunk: Monologue transcript chunk with 'text', 'startMs', 'endMs'.
            chunk_index: Index of the chunk in timeline.
            target_phrase: Specific spoken words to synchronize (default: extracted from chunk text).
            sync_offset_sec: Seconds from chunk start where the target word occurs.
            concept_title: Human-readable concept title.
            outfit_reference: Ground-truth reference anchor of the speaker's outfit in the video.
            sentiment_blendshape: Extrapolated emotional sentiment & facial blend shape expression.
            extrapolate_hold_sec: Post-speech hold runway buffer (default: 2.0s, e.g. 3s mapped -> 5s total).
            model: Google Flow / Veo model name.
            aspect_ratio: Video aspect ratio ("9:16" vertical).
        """
        text = str(chunk.get("text") or "").strip()
        start_ms = int(chunk.get("startMs") or 0)
        end_ms = int(chunk.get("endMs") or (start_ms + 6000))
        chunk_dur_sec = max(1.0, (end_ms - start_ms) / 1000.0)

        # Resolve target phrase if not provided
        resolved_phrase = target_phrase
        if not resolved_phrase:
            # Pick first 2-3 significant words
            words = [w for w in text.split() if len(w) > 3]
            resolved_phrase = " ".join(words[:2]) if words else text[:20]

        start_ts = CuritoWordSyncCalculator.format_seconds_to_timestamp(start_ms / 1000.0)
        title = concept_title or f"Curito Beat #{chunk_index + 1}: {resolved_phrase}"

        # Resolve ground-truth video reference anchors if not provided
        if outfit_reference is None:
            outfit_reference = CuritoOutfitReference(
                description="minimalist studio wardrobe",
                palette=["#121212", "#2A2A2A"],
                material_texture="matte textile weave",
                reference_frame_ms=start_ms,
                style_category="editorial_luxury",
            )
        if sentiment_blendshape is None:
            sentiment_blendshape = CuritoSentimentBlendShape(
                primary_emotion="resolute_focus",
                intensity=0.85,
                blendshape_weights={"brow_concentration": 0.70, "jaw_conviction": 0.65},
                motion_direction="forward_push",
                energy_velocity_curve="sharp_snap_hold",
            )

        # 1. Compute Word-Sync Schema (with 3s mapped -> extrapolate 2s = 5s total architecture)
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp=start_ts,
            target_phrase=resolved_phrase,
            target_word_offset_sec=sync_offset_sec,
            desired_duration_sec=chunk_dur_sec,
            extrapolate_hold_sec=extrapolate_hold_sec,
        )

        # 2. Stitch Curito Prompt from DNA Genomes with Video Outfit & Sentiment Anchors
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor=f"Cinematic visual metaphor for {resolved_phrase}",
            word_sync=word_sync,
            outfit_reference=outfit_reference,
            sentiment_blendshape=sentiment_blendshape,
            model=model,
            aspect_ratio=aspect_ratio,
        )

        # 3. Generate Animation & Produce Storyboard Report via Headless Veo / Google Flow MCP
        clip_filename = f"curito_chunk_{chunk_index:02d}_{word_sync.total_duration_sec}s.mp4"
        dest_mp4 = self.output_dir / clip_filename

        if self.client is not None:
            report = self.client.generate_curito_animation(
                prompt=stitched,
                concept_title=title,
                clip_filename=clip_filename,
            )
        elif self.fixture_video_path and self.fixture_video_path.exists():
            shutil.copyfile(self.fixture_video_path, dest_mp4)
            report = self._build_report_from_existing_mp4(
                dest_mp4=dest_mp4,
                prompt=stitched,
                word_sync=word_sync,
                concept_title=title,
            )
        elif self.veo_client is not None:
            try:
                res = self.veo_client.generate_curito_video(
                    prompt=stitched,
                    output_path=dest_mp4,
                    duration_sec=word_sync.total_duration_sec,
                    aspect_ratio=aspect_ratio,
                )
                report = self._build_report_from_veo_result(
                    veo_result=res,
                    prompt=stitched,
                    word_sync=word_sync,
                    concept_title=title,
                )
            except Exception as veo_err:
                err_str = str(veo_err)
                if dest_mp4.exists() and dest_mp4.stat().st_size > 1000:
                    report = self._build_report_from_existing_mp4(
                        dest_mp4=dest_mp4,
                        prompt=stitched,
                        word_sync=word_sync,
                        concept_title=title,
                    )
                elif isinstance(veo_err, PermissionError) or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str:
                    raise PermissionError(
                        f"VEO 3.1 API QUOTA EXHAUSTED: Google AI Studio returned 429 RESOURCE_EXHAUSTED. "
                        f"To enable headless video generation in production, link a Google Cloud Billing "
                        f"account (Pay-as-you-go) to your project at: https://ai.google.dev/gemini-api/docs/rate-limits"
                    ) from veo_err
                else:
                    raise veo_err
        elif self.flow_client is not None:
            report = self.flow_client.generate_curito_animation(
                prompt=stitched,
                concept_title=title,
                clip_filename=clip_filename,
            )
        elif dest_mp4.exists() and dest_mp4.stat().st_size > 1000:
            report = self._build_report_from_existing_mp4(
                dest_mp4=dest_mp4,
                prompt=stitched,
                word_sync=word_sync,
                concept_title=title,
            )
        else:
            raise RuntimeError(
                f"Headless Curito animation generation failed for '{clip_filename}': "
                "No active generator (VeoBackendClient/GoogleFlowMCPClient) or fixture video available."
            )

        mp4_path_obj = Path(report.mp4_asset_path)

        # Enforce pristine H.264 encoding via FFmpeg for 100% Remotion/Chromium compatibility
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin and mp4_path_obj.exists():
            tmp_transcode = mp4_path_obj.with_name(f"{mp4_path_obj.stem}_h264.mp4")
            try:
                subprocess.run(
                    [
                        ffmpeg_bin, "-y",
                        "-i", str(mp4_path_obj),
                        "-c:v", "libx264",
                        "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        str(tmp_transcode),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if tmp_transcode.exists() and tmp_transcode.stat().st_size > 500:
                    shutil.move(str(tmp_transcode), str(mp4_path_obj))
            except Exception:
                if tmp_transcode.exists():
                    tmp_transcode.unlink(missing_ok=True)

        # Mirror asset into remotion-app/public/source/ so Remotion can resolve it via staticFile()
        rel_asset_path = f"source/{clip_filename}"
        repo_root = Path(__file__).resolve().parent.parent
        remotion_pub_dir = repo_root / "remotion-app" / "public" / "source"
        if remotion_pub_dir.exists() and mp4_path_obj.exists():
            target_public_file = remotion_pub_dir / clip_filename
            try:
                if str(mp4_path_obj.resolve()) != str(target_public_file.resolve()):
                    shutil.copyfile(mp4_path_obj, target_public_file)
            except Exception:
                pass

        # 4. Compute Timeline Window
        timeline_start_ms = start_ms
        timeline_end_ms = start_ms + (word_sync.total_duration_sec * 1000)

        report_stem = Path(report.mp4_asset_path).stem
        report_json = Path(report.mp4_asset_path).parent / f"{report_stem}_report.json"
        report_md = Path(report.mp4_asset_path).parent / f"{report_stem}_report.md"

        directive = CuritoPlacementDirective(
            id=f"curito_anim_{chunk_index:02d}",
            chunk_index=chunk_index,
            concept_title=title,
            timeline_start_ms=timeline_start_ms,
            timeline_end_ms=timeline_end_ms,
            duration_ms=word_sync.total_duration_sec * 1000,
            duration_sec=word_sync.total_duration_sec,
            treatment_family=CURITO_TREATMENT_FAMILY,
            mp4_path=str(mp4_path_obj),
            relative_asset_path=rel_asset_path,
            word_sync=word_sync,
            genomes_used=stitched.genome_ids,
            report_json_path=str(report_json),
            report_md_path=str(report_md),
            composite_layer="background_video_cutaway",
            outfit_reference=outfit_reference,
            sentiment_blendshape=sentiment_blendshape,
        )

        return directive

    def process_timeline_chunks(
        self,
        chunks: List[Dict[str, Any]],
        max_animations: int = 1,
    ) -> List[CuritoPlacementDirective]:
        """Scan monologue chunks, select top candidate moments, and generate Curito animations."""
        candidates = []
        last_anim_sec = -100.0

        for idx, chunk in enumerate(chunks):
            start_ms = int(chunk.get("startMs") or 0)
            time_since = max(0.0, (start_ms / 1000.0) - last_anim_sec)

            is_cand, score, rationale = CuritoAnimationDetector.evaluate_chunk_for_animation(
                chunk=chunk,
                chunk_index=idx,
                time_since_last_animation_sec=time_since,
            )
            if is_cand:
                candidates.append((idx, chunk, score, rationale))

        # Sort by candidate score descending
        candidates.sort(key=lambda x: x[2], reverse=True)

        directives: List[CuritoPlacementDirective] = []
        for idx, chunk, score, rationale in candidates[:max_animations]:
            directive = self.plan_and_generate_animation(
                chunk=chunk,
                chunk_index=idx,
            )
            directives.append(directive)
            last_anim_sec = directive.timeline_end_ms / 1000.0

        return directives

    def plan_from_full_transcript(
        self,
        transcript_chunks: List[Dict[str, Any]],
        model_name: str = "gemini-3.5-flash",
    ) -> Dict[str, Any]:
        """Runs full-transcript deep semantic extraction, inflection selection,
        and diffusion prompt policy synthesis with adversarial self-critique.
        
        Conforms strictly to the Diffusion Asset Prompting Policy (5-element schema,
        zero typography, zero 2D UI elements, zero lighting fixtures, explicit floor/shadow).
        """
        return extract_and_synthesize_curito_prompt(
            transcript_chunks=transcript_chunks,
            model_name=model_name,
        )
