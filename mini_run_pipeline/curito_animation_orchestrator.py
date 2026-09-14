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
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .broll_engine import BrollSuitabilityEngine
from .curito_animation_dna import (
    CURITO_TREATMENT_FAMILY,
    CuritoPromptStitcher,
    CuritoWordSyncCalculator,
    CuritoWordSyncSchema,
)
from .google_flow_client import CuritoAnimationReport, GoogleFlowConfig, GoogleFlowMCPClient


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "chunkIndex": self.chunk_index,
            "conceptTitle": self.concept_title,
            "timelineStartMs": self.timeline_start_ms,
            "timelineEndMs": self.timeline_end_ms,
            "durationMs": self.duration_ms,
            "durationSec": self.duration_sec,
            "treatmentFamily": self.treatment_family,
            "mp4Path": str(self.mp4_path),
            "wordSync": self.word_sync.to_dict(),
            "genomesUsed": self.genomes_used,
            "reportJsonPath": str(self.report_json_path),
            "reportMdPath": str(self.report_md_path),
            "compositeLayer": self.composite_layer,
            "blendMode": self.blend_mode,
            "opacity": self.opacity,
        }


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

    def __init__(self, client: Optional[GoogleFlowMCPClient] = None):
        self.client = client or GoogleFlowMCPClient()

    def plan_and_generate_animation(
        self,
        chunk: Dict[str, Any],
        chunk_index: int,
        target_phrase: Optional[str] = None,
        sync_offset_sec: Optional[float] = 3.0,
        concept_title: Optional[str] = None,
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

        # 1. Compute Word-Sync Schema
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp=start_ts,
            target_phrase=resolved_phrase,
            target_word_offset_sec=sync_offset_sec,
            desired_duration_sec=chunk_dur_sec,
        )

        # 2. Stitch Curito Prompt from DNA Genomes
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor=f"Cinematic visual metaphor for {resolved_phrase}",
            word_sync=word_sync,
            model=model,
            aspect_ratio=aspect_ratio,
        )

        # 3. Generate Animation & Produce Storyboard Report via Google Flow MCP
        clip_filename = f"curito_chunk_{chunk_index:02d}_{word_sync.total_duration_sec}s.mp4"
        report = self.client.generate_curito_animation(
            prompt=stitched,
            concept_title=title,
            clip_filename=clip_filename,
        )

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
            mp4_path=report.mp4_asset_path,
            word_sync=word_sync,
            genomes_used=stitched.genome_ids,
            report_json_path=str(report_json),
            report_md_path=str(report_md),
            composite_layer="background_video_cutaway",
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
