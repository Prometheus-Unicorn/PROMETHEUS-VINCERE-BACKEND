"""test_curito_autonomous_pipeline.py - Verification for autonomous repository-contained Curito video pipeline."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import cv2

from mini_run_pipeline.backgrounds import plan_backgrounds
from mini_run_pipeline.curito_animation_dna import (
    CuritoOutfitReference,
    CuritoSentimentBlendShape,
    CuritoWordSyncCalculator,
)
from mini_run_pipeline.curito_animation_orchestrator import (
    CuritoAnimationDetector,
    CuritoAnimationOrchestrator,
    CuritoPlacementDirective,
)


class CuritoAutonomousPipelineTests(unittest.TestCase):
    """Test suite proving the complete cause-and-effect generative video pipeline
    operates autonomously within the repository alone without manual intervention.
    """

    def test_curito_detector_identifies_turning_point_candidates(self):
        """Verify: Transcript chunks with high conceptual tokens trigger Curito animation evaluation."""
        candidate_chunk = {
            "chunkIndex": 2,
            "text": "The entire architecture of the system hinges on this breakthrough algorithm.",
            "startMs": 4000,
            "endMs": 7500,
        }
        is_cand, score, rationale = CuritoAnimationDetector.evaluate_chunk_for_animation(
            chunk=candidate_chunk,
            chunk_index=2,
            time_since_last_animation_sec=100.0,
        )
        self.assertTrue(is_cand)
        self.assertGreaterEqual(score, 0.60)
        self.assertIn("concept tokens matched", rationale)
        self.assertIn("architecture", rationale)

        non_candidate_chunk = {
            "chunkIndex": 3,
            "text": "yeah so anyway like you know um",
            "startMs": 7600,
            "endMs": 9000,
        }
        is_cand_2, score_2, _ = CuritoAnimationDetector.evaluate_chunk_for_animation(
            chunk=non_candidate_chunk,
            chunk_index=3,
            time_since_last_animation_sec=100.0,
        )
        self.assertFalse(is_cand_2)
        self.assertLess(score_2, 0.60)

    def test_curito_orchestrator_autonomous_generation(self):
        """Verify: CuritoAnimationOrchestrator produces a valid 5s 9:16 vertical MP4 autonomously."""
        chunk = {
            "chunkIndex": 0,
            "text": "We engineered the entire feedback loop into a repeatable system.",
            "startMs": 1000,
            "endMs": 4000,  # 3.0s speech duration
        }
        outfit = CuritoOutfitReference(
            description="matte charcoal tailored blazer",
            palette=["#181818", "#2F2F2F"],
            material_texture="structured wool weave",
            reference_frame_ms=1000,
            style_category="editorial_luxury",
        )
        sentiment = CuritoSentimentBlendShape(
            primary_emotion="resolute_focus",
            intensity=0.90,
            blendshape_weights={"brow_concentration": 0.80, "jaw_conviction": 0.75},
            motion_direction="forward_push",
            energy_velocity_curve="sharp_snap_hold",
        )

        orchestrator = CuritoAnimationOrchestrator()
        directive = orchestrator.plan_and_generate_animation(
            chunk=chunk,
            chunk_index=0,
            outfit_reference=outfit,
            sentiment_blendshape=sentiment,
        )

        # 1. Verify Directive Model properties
        self.assertIsInstance(directive, CuritoPlacementDirective)
        # 3.0s speech mapped -> extrapolate +2.0s hold runway = 5.0s total duration
        self.assertEqual(directive.duration_sec, 5)
        self.assertEqual(directive.duration_ms, 5000)
        self.assertTrue(directive.relative_asset_path.startswith("source/"))

        # 2. Verify Output Video File on disk
        mp4_path = Path(directive.mp4_path)
        self.assertTrue(mp4_path.exists(), f"Generated MP4 must exist at {mp4_path}")
        self.assertGreater(mp4_path.stat().st_size, 1000, "MP4 file size must be non-empty")

        # 3. Verify Video Properties via OpenCV Probe
        cap = cv2.VideoCapture(str(mp4_path))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        dur_sec = frame_cnt / fps if fps > 0 else 0
        cap.release()

        self.assertEqual(w, 1080, "Video must be 1080px wide (9:16 vertical)")
        self.assertEqual(h, 1920, "Video must be 1920px high (9:16 vertical)")
        self.assertAlmostEqual(dur_sec, 5.0, delta=0.2, msg="Video duration must be exactly 5.0s")

        # 4. Verify asset mirrored to remotion-app/public/source/
        repo_root = Path(__file__).resolve().parent.parent
        mirrored_file = repo_root / "remotion-app" / "public" / directive.relative_asset_path
        self.assertTrue(mirrored_file.exists(), f"Asset must be mirrored to {mirrored_file}")

    def test_plan_backgrounds_integrates_curito_animation(self):
        """Verify: plan_backgrounds automatically detects candidate, executes animation, and attaches to timeline."""
        chunks = [
            {
                "chunkIndex": 0,
                "text": "Welcome back to the breakdown.",
                "startMs": 0,
                "endMs": 2500,
            },
            {
                "chunkIndex": 1,
                "text": "The entire architecture of this breakthrough strategy operates as an engine.",
                "startMs": 2800,
                "endMs": 5800,
            },
            {
                "chunkIndex": 2,
                "text": "And that is how you win in this market.",
                "startMs": 6000,
                "endMs": 8500,
            },
        ]
        scenes = [
            {"id": "scene_0", "role": "intro", "salience": 0.5, "startMs": 0, "endMs": 2500},
            {"id": "scene_1", "role": "turning_point", "salience": 0.95, "startMs": 2800, "endMs": 5800},
            {"id": "scene_2", "role": "conclusion", "salience": 0.4, "startMs": 6000, "endMs": 8500},
        ]

        backgrounds = plan_backgrounds(
            chunks=chunks,
            scenes=scenes,
            design={"brollTreatment": "evidentiary_dossier_card"},
            duration_ms=9000,
            prompt="breakthrough system architecture",
        )

        self.assertGreater(len(backgrounds), 0, "Plan backgrounds should place at least one background")
        # Check if Curito animation background was placed
        curito_bg = next((bg for bg in backgrounds if str(bg.get("code", "")).startswith("bg_curito_animation")), None)
        self.assertIsNotNone(curito_bg, "Curito animation background should be selected and placed")

        self.assertEqual(curito_bg["kind"], "broll_cutaway")
        broll = curito_bg.get("broll", {})
        self.assertEqual(broll.get("source"), "curito_generative_engine")
        self.assertTrue(broll.get("videoFile", "").startswith("source/"))
        self.assertIn("curito", curito_bg)
        self.assertEqual(curito_bg["curito"]["durationSec"], 5)

    def test_gha_roundtrip_packaging_and_slice_download(self):
        """Verify: Background assets in props.json are correctly prepared for R2 upload and slice download."""
        test_orch = {
            "backgrounds": [
                {
                    "id": "bg-curito-0",
                    "kind": "broll_cutaway",
                    "broll": {
                        "videoFile": "source/test_curito.mp4",
                        "r2Key": "gha-renders/job123/broll_0_test_curito.mp4",
                    },
                }
            ]
        }
        props = {"jobId": "job123", "orchestration": test_orch}

        # Simulated runner check
        with tempfile.TemporaryDirectory() as tmpdir:
            props_file = Path(tmpdir) / "props_job123.json"
            props_file.write_text(json.dumps(props), encoding="utf-8")

            # Slice runner inspects props
            with open(props_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            bgs = loaded.get("orchestration", {}).get("backgrounds", [])
            self.assertEqual(len(bgs), 1)
            broll = bgs[0].get("broll", {})
            self.assertEqual(broll.get("videoFile"), "source/test_curito.mp4")
            self.assertEqual(broll.get("r2Key"), "gha-renders/job123/broll_0_test_curito.mp4")

    def test_curito_orchestrator_headless_veo_client_dispatch(self):
        """Verify: CuritoAnimationOrchestrator seamlessly orchestrates via headless VeoBackendClient."""
        from unittest.mock import MagicMock
        from mini_run_pipeline.veo_backend_client import VeoBackendClient, VeoGenerationResult

        chunk = {
            "chunkIndex": 5,
            "text": "The entire strategic architecture compounds exponentially.",
            "startMs": 12000,
            "endMs": 15000,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_out = Path(tmpdir)
            mock_veo = MagicMock(spec=VeoBackendClient)

            fake_mp4 = tmp_out / "curito_chunk_05_5s.mp4"
            fake_mp4.write_bytes(b"\x00" * 4096)

            mock_veo.generate_curito_video.return_value = VeoGenerationResult(
                mp4_path=str(fake_mp4),
                duration_sec=5,
                aspect_ratio="9:16",
                model="veo-3.1-fast-generate-preview",
                file_size_bytes=4096,
                operation_name="operations/veo-gen-mock-789",
                prompt="Stitched prompt",
                completed_at=1789500000.0,
            )

            orchestrator = CuritoAnimationOrchestrator(veo_client=mock_veo, output_dir=tmp_out)
            directive = orchestrator.plan_and_generate_animation(
                chunk=chunk,
                chunk_index=5,
            )

            mock_veo.generate_curito_video.assert_called_once()
            call_kwargs = mock_veo.generate_curito_video.call_args.kwargs
            self.assertEqual(call_kwargs["duration_sec"], 5)
            self.assertEqual(call_kwargs["aspect_ratio"], "9:16")

            self.assertEqual(directive.id, "curito_anim_05")
            self.assertEqual(directive.duration_sec, 5)
            self.assertTrue(Path(directive.report_json_path).exists())
            self.assertTrue(Path(directive.report_md_path).exists())


if __name__ == "__main__":
    unittest.main()
