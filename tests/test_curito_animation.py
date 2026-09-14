"""Comprehensive Unit Tests for Curito Cinematic Animation Prompt DNA & Google Flow MCP Orchestration.

Validates:
1. Treatment family nomenclature ("animations_curito") and core genome taxonomy.
2. Word-sync calculations and timestamp schema (e.g. 5:30 interview moment with 3s sync offset).
3. 6-part Google Flow prompt stitching with imperative MCP agent formatting.
4. Google Flow MCP tool schemas and storyboard breakdown reporting.
5. Offline 9:16 vertical MP4 video asset synthesis and file validity.
6. End-to-end candidate detection and placement directive creation.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import cv2

from mini_run_pipeline.curito_animation_dna import (
    CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
    CATEGORY_LIGHTING_SHADING_PROFILE,
    CATEGORY_SCENE_ASSET_BREAKDOWN,
    CATEGORY_VISUAL_DESIGN_SYSTEM,
    CORE_GENOME_CATEGORIES,
    CURITO_GENOME_LIBRARY,
    CURITO_SAMPLE_VIDEO_MULTIMODAL_EXTRACTION,
    CURITO_TREATMENT_FAMILY,
    CuritoGenome,
    CuritoPromptStitcher,
    CuritoWordSyncCalculator,
    CuritoWordSyncSchema,
)
from mini_run_pipeline.google_flow_client import (
    CuritoAnimationReport,
    CuritoStoryboardBeat,
    GoogleFlowConfig,
    GoogleFlowMCPClient,
)
from mini_run_pipeline.curito_animation_orchestrator import (
    CuritoAnimationDetector,
    CuritoAnimationOrchestrator,
    CuritoPlacementDirective,
)
from mini_run_pipeline.google_flow_session import (
    CRITICAL_SESSION_COOKIES,
    GoogleFlowSessionManager,
)


class CuritoAnimationDnaTaxonomyTests(unittest.TestCase):
    """Test Curito genome taxonomy and nomenclature consistency."""

    def test_treatment_family_nomenclature(self):
        """All Curito genomes must belong to the 'animations_curito' family."""
        self.assertEqual(CURITO_TREATMENT_FAMILY, "animations_curito")
        for gid, genome in CURITO_GENOME_LIBRARY.items():
            self.assertEqual(
                genome.family,
                "animations_curito",
                f"Genome {gid} family '{genome.family}' must equal 'animations_curito'",
            )

    def test_four_core_genome_categories_populated(self):
        """The library must contain rich entries for all 4 core pillars."""
        for cat in CORE_GENOME_CATEGORIES:
            matches = [g for g in CURITO_GENOME_LIBRARY.values() if g.category == cat]
            self.assertGreaterEqual(
                len(matches),
                3,
                f"Category '{cat}' must have at least 3 curated DNA genomes (found {len(matches)}).",
            )

    def test_cinematic_dna_snippet_quality(self):
        """Genomes must contain descriptive, cinematic physical descriptors."""
        whitecheckered = CURITO_GENOME_LIBRARY.get("curito_vis_whitecheckered_hud")
        self.assertIsNotNone(whitecheckered)
        self.assertIn("transparent checkerboard", whitecheckered.dna_snippet.lower())
        self.assertIn("neon cyan", whitecheckered.dna_snippet.lower())

        chiaroscuro = CURITO_GENOME_LIBRARY.get("curito_lit_chiaroscuro_industrial")
        self.assertIsNotNone(chiaroscuro)
        self.assertIn("chiaroscuro", chiaroscuro.dna_snippet.lower())
        self.assertIn("tungsten", chiaroscuro.dna_snippet.lower())

        anamorphic = CURITO_GENOME_LIBRARY.get("curito_cam_35mm_anamorphic_drift")
        self.assertIsNotNone(anamorphic)
        self.assertIn("anamorphic", anamorphic.dna_snippet.lower())
        self.assertIn("sub-pixel drift", anamorphic.dna_snippet.lower())

    def test_extracted_reference_animation_genomes(self):
        """Verify newly extracted Porsche reference animation genomes across categories."""
        pedestal = CURITO_GENOME_LIBRARY.get("curito_vis_editorial_pedestal_orbit")
        self.assertIsNotNone(pedestal)
        self.assertEqual(pedestal.category, CATEGORY_VISUAL_DESIGN_SYSTEM)
        self.assertIn("pedestal", pedestal.dna_snippet.lower())

        triptych = CURITO_GENOME_LIBRARY.get("curito_vis_halftone_triptych_cutout")
        self.assertIsNotNone(triptych)
        self.assertIn("triptych", triptych.dna_snippet.lower())
        self.assertIn("barcode", triptych.dna_snippet.lower())

        zenith = CURITO_GENOME_LIBRARY.get("curito_vis_orthographic_zenith_dial")
        self.assertIsNotNone(zenith)
        self.assertIn("orthographic", zenith.dna_snippet.lower())
        self.assertIn("compass", zenith.dna_snippet.lower())

        bbox = CURITO_GENOME_LIBRARY.get("curito_scene_vector_bounding_box_ghost")
        self.assertIsNotNone(bbox)
        self.assertEqual(bbox.category, CATEGORY_SCENE_ASSET_BREAKDOWN)
        self.assertIn("bounding box", bbox.dna_snippet.lower())

        wipe = CURITO_GENOME_LIBRARY.get("curito_scene_halftone_dot_wipe")
        self.assertIsNotNone(wipe)
        self.assertIn("halftone", wipe.dna_snippet.lower())


class CuritoWordSyncCalculationTests(unittest.TestCase):
    """Test mathematical timestamp parsing, word-sync offsets, and duration clamping."""

    def test_timestamp_parsing_variants(self):
        """Supports 'MM:SS', 'MM:SS.mmm', and 'HH:MM:SS' strings."""
        calc = CuritoWordSyncCalculator
        self.assertAlmostEqual(calc.parse_timestamp_str_to_seconds("05:30.000"), 330.0)
        self.assertAlmostEqual(calc.parse_timestamp_str_to_seconds("05:30"), 330.0)
        self.assertAlmostEqual(calc.parse_timestamp_str_to_seconds("330.0"), 330.0)
        self.assertAlmostEqual(calc.parse_timestamp_str_to_seconds("01:05:30"), 3930.0)

    def test_five_thirty_interview_moment_with_three_second_offset(self):
        """Explicit requirement test: 5:30 interview moment with a 3.0s word-sync offset."""
        sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="05:30.000",
            target_phrase="radical self-reliance",
            target_word_offset_sec=3.0,
        )
        self.assertEqual(sync.interview_timestamp, "05:30.000")
        self.assertAlmostEqual(sync.interview_start_sec, 330.0)
        self.assertAlmostEqual(sync.sync_offset_sec, 3.0)
        self.assertIn("radical", sync.target_words)
        self.assertIn("self-reliance", sync.target_words)
        # Clamped to valid Veo duration (6s)
        self.assertEqual(sync.total_duration_sec, 6)
        # Timing cue includes exact seconds
        self.assertIn("+3.0s", sync.timing_cue)
        self.assertIn("radical self-reliance", sync.timing_cue)

    def test_duration_clamping_to_veo_intervals(self):
        """Duration must clamp strictly to 4, 6, or 8 seconds."""
        calc = CuritoWordSyncCalculator
        self.assertEqual(calc.clamp_generative_duration(2.5), 4)
        self.assertEqual(calc.clamp_generative_duration(5.0), 4)
        self.assertEqual(calc.clamp_generative_duration(5.5), 6)
        self.assertEqual(calc.clamp_generative_duration(7.0), 6)
        self.assertEqual(calc.clamp_generative_duration(7.5), 8)
        self.assertEqual(calc.clamp_generative_duration(12.0), 8)


class CuritoPromptStitcherTests(unittest.TestCase):
    """Test dynamic prompt stitching into the 6-part Google Flow structure."""

    def test_six_part_flow_structure_compliance(self):
        """Prompt must contain all 6 parts of the Google Flow viral formula."""
        sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:15.000",
            target_phrase="execute now",
            target_word_offset_sec=2.5,
        )
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="Mechanical brass gear train",
            word_sync=sync,
            model="Veo 3.1 - Fast",
            aspect_ratio="9:16",
        )

        full_prompt = stitched.full_prompt
        # Check structure components
        self.assertIn("Mechanical brass gear train", stitched.subject_element)
        self.assertIn("execute now", stitched.action_movement)
        self.assertIn("+2.5s", stitched.action_movement)
        self.assertIn("obsidian", stitched.location_background.lower())
        self.assertIn("anamorphic", stitched.composition.lower())
        self.assertIn("24fps", stitched.style_cues)

        # Check imperative prompt for Google Flow MCP
        self.assertIn("Generate immediately a", stitched.imperative_flow_prompt)
        self.assertIn("Veo 3.1 - Fast", stitched.imperative_flow_prompt)
        self.assertIn("9:16", stitched.imperative_flow_prompt)
        self.assertIn("Faithfully adhere", stitched.imperative_flow_prompt)


class GoogleFlowMCPClientTests(unittest.TestCase):
    """Test Google Flow MCP client tool protocols and artifact generation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="flow_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_call_protocols(self):
        """Validates tool call return signatures for flow_connect, flow_status, flow_generate_video."""
        cfg = GoogleFlowConfig(output_dir=self.temp_dir, dry_run=True)
        client = GoogleFlowMCPClient(config=cfg)

        conn = client.flow_connect()
        self.assertTrue(conn["connected"])
        self.assertEqual(conn["tool"], "flow_connect")

        stat = client.flow_status()
        self.assertTrue(stat["browserConnected"])
        self.assertEqual(stat["tool"], "flow_status")

        gen = client.flow_generate_video(prompt="Test prompt", duration="6s")
        self.assertEqual(gen["tool"], "flow_generate_video")
        self.assertEqual(gen["status"], "GENERATION_DISPATCHED")

    def test_storyboard_breakdown_and_report_generation(self):
        """Client must generate a 4-beat storyboard and write JSON + Markdown reports."""
        cfg = GoogleFlowConfig(output_dir=self.temp_dir, dry_run=True)
        client = GoogleFlowMCPClient(config=cfg)

        sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="05:30.000",
            target_phrase="radical self-reliance",
            target_word_offset_sec=3.0,
        )
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="Granite block pushed uphill",
            word_sync=sync,
        )

        report = client.generate_curito_animation(
            prompt=stitched,
            concept_title="Radical Self-Reliance",
            clip_filename="test_sr_01.mp4",
        )

        self.assertEqual(report.concept_title, "Radical Self-Reliance")
        self.assertEqual(report.duration_sec, 6)
        self.assertEqual(len(report.storyboard_beats), 4)

        # Verify MP4 file exists and has valid vertical 9:16 video properties
        mp4_path = Path(report.mp4_asset_path)
        self.assertTrue(mp4_path.exists(), "MP4 asset must be written to disk")
        self.assertGreater(mp4_path.stat().st_size, 1000, "MP4 file must not be empty")

        cap = cv2.VideoCapture(str(mp4_path))
        self.assertTrue(cap.isOpened(), "Generated MP4 must be readable by OpenCV")
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.assertEqual((w, h), (1080, 1920), "Must be 9:16 vertical resolution (1080x1920)")
        cap.release()

        # Verify JSON report exists and parses
        json_report = Path(self.temp_dir) / "test_sr_01_report.json"
        self.assertTrue(json_report.exists())
        data = json.loads(json_report.read_text(encoding="utf-8"))
        self.assertEqual(data["treatmentFamily"], "animations_curito")
        self.assertEqual(data["wordSync"]["syncOffsetSec"], 3.0)

        # Verify Markdown report exists and contains timing cues
        md_report = Path(self.temp_dir) / "test_sr_01_report.md"
        self.assertTrue(md_report.exists())
        md_content = md_report.read_text(encoding="utf-8")
        self.assertIn("05:30.000", md_content)
        self.assertIn("Chronological Storyboard Breakdown", md_content)


class CuritoAnimationOrchestratorTests(unittest.TestCase):
    """Test candidate detection and end-to-end orchestration for mini-run integration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="orch_test_")
        self.client = GoogleFlowMCPClient(config=GoogleFlowConfig(output_dir=self.temp_dir, dry_run=True))
        self.orchestrator = CuritoAnimationOrchestrator(client=self.client)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_candidate_detection_for_framework_monologue(self):
        """Chunks with framework, system, or leverage terms must be flagged as animation candidates."""
        chunk = {
            "text": "The entire architecture relies on an asymmetric feedback loop to scale revenue.",
            "startMs": 12000,
            "endMs": 18000,
        }
        is_cand, score, rationale = CuritoAnimationDetector.evaluate_chunk_for_animation(chunk, chunk_index=0)
        self.assertTrue(is_cand)
        self.assertGreater(score, 0.4)
        self.assertIn("architecture", rationale)

    def test_plan_and_generate_animation_directive(self):
        """End-to-end creation of a CuritoPlacementDirective ready for timeline compositing."""
        chunk = {
            "text": "No one is coming to save you, radical self-reliance is the only answer.",
            "startMs": 330000,  # 5:30
            "endMs": 336000,
        }
        directive = self.orchestrator.plan_and_generate_animation(
            chunk=chunk,
            chunk_index=3,
            target_phrase="radical self-reliance",
            sync_offset_sec=3.0,
        )

        self.assertEqual(directive.id, "curito_anim_03")
        self.assertEqual(directive.treatment_family, "animations_curito")
        self.assertEqual(directive.timeline_start_ms, 330000)
        self.assertEqual(directive.duration_sec, 6)
        self.assertEqual(directive.word_sync.sync_offset_sec, 3.0)
        self.assertTrue(Path(directive.mp4_path).exists())
        self.assertEqual(directive.composite_layer, "background_video_cutaway")


class CuritoDirectMultimodalExtractionTests(unittest.TestCase):
    """Test direct perceptual, visual, and acoustic multimodal extraction catalog."""

    def test_multimodal_extraction_catalog_metadata(self):
        """Metadata must match physical ground truth from the reference MP4 video."""
        data = CURITO_SAMPLE_VIDEO_MULTIMODAL_EXTRACTION
        self.assertEqual(data["extraction_method"], "direct_multimodal_perceptual_and_acoustic_audit")
        meta = data["video_metadata"]
        self.assertAlmostEqual(meta["duration_sec"], 23.62, places=1)
        self.assertEqual(meta["resolution"], "1080x1920")
        self.assertEqual(meta["aspect_ratio"], "9:16")

    def test_verbatim_transcript_accuracy(self):
        """Spoken transcript must reflect the verbatim voiceover without hallucination."""
        data = CURITO_SAMPLE_VIDEO_MULTIMODAL_EXTRACTION
        transcript = data["spoken_transcript_verbatim"]
        self.assertIn("Performance isn't created, it's engineered", transcript)
        self.assertIn("For over 75 years, Porsche has defined pure driving excellence", transcript)
        self.assertIn("precision in every curve, power in every detail", transcript)
        self.assertIn("Iconic design fused with motorsport DNA", transcript)
        self.assertIn("built to dominate the road, crafted to thrill the driver", transcript)
        self.assertIn("This isn't just a car, it's a statement", transcript)
        self.assertIn("Porsche, there is no substitute", transcript)

    def test_acoustic_word_cue_timestamps(self):
        """Acoustic word cues must have verified monotonic time offsets."""
        cues = CURITO_SAMPLE_VIDEO_MULTIMODAL_EXTRACTION["acoustic_word_cues"]
        self.assertGreaterEqual(len(cues), 7)
        prev_offset = -1.0
        for cue in cues:
            self.assertGreater(cue["offset_sec"], prev_offset)
            prev_offset = cue["offset_sec"]
            self.assertTrue(cue["phrase"])
            self.assertTrue(cue["key_accent"])

    def test_forensic_visual_system_parameters(self):
        """Visual system must contain authentic Swiss/Curito paper editorial tokens."""
        data = CURITO_SAMPLE_VIDEO_MULTIMODAL_EXTRACTION
        palette = data["color_palette"]
        self.assertEqual(palette["paper_canvas"], "#ECECEC")
        self.assertEqual(palette["primary_solid_black"], "#111111")
        self.assertEqual(palette["pure_vehicle_white"], "#FFFFFF")

        typography = data["typography_system"]
        self.assertIn("Neue Haas Grotesk", typography["headline_primary"])
        self.assertIn("Editorial New", typography["editorial_accent"])

        devices = data["graphic_devices"]
        self.assertTrue(any("bounding box" in d.lower() for d in devices))
        self.assertTrue(any("starburst" in d.lower() for d in devices))
        self.assertTrue(any("barcode" in d.lower() for d in devices))

        curves = data["motion_curves"]
        self.assertIn("cubic-bezier(0.16, 1.0, 0.3, 1.0)", curves["snap_deceleration"])


class CuritoPaperEditorialPromptStitchingTests(unittest.TestCase):
    """Test Curito paper editorial aesthetic prompt stitching vs legacy obsidian."""

    def test_curito_paper_editorial_stitching(self):
        """Curito paper aesthetic must generate off-white canvas, diffuse lighting, and Swiss typography."""
        sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:18.000",
            target_phrase="This isn't just a car",
            target_word_offset_sec=2.2,
        )
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="Top-down orthographic cut of white Porsche GT3 RS with carbon bonnet stripes",
            word_sync=sync,
            model="Veo 3.1 - Fast",
            aspect_ratio="9:16",
            aesthetic="curito_editorial_paper",
        )

        # Check background and lighting
        self.assertIn("#ECECEC", stitched.location_background)
        self.assertIn("paper canvas", stitched.location_background.lower())
        self.assertIn("diffuse high-key ambient", stitched.context_lighting.lower())
        self.assertIn("double-layer drop shadow", stitched.context_lighting.lower())

        # Check Swiss editorial style cues
        self.assertIn("neue haas grotesk", stitched.style_cues.lower())
        self.assertIn("editorial new", stitched.style_cues.lower())
        self.assertIn("figma bounding box", stitched.style_cues.lower())
        self.assertIn("barcode", stitched.style_cues.lower())

        # Full prompt has 6 formula parts
        parts = stitched.full_prompt.split(", ")
        self.assertGreaterEqual(len(parts), 6)

    def test_auto_detection_of_curito_keywords(self):
        """Auto aesthetic detects Curito/Porsche keywords and routes to paper editorial canvas."""
        sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:11.400",
            target_phrase="motorsport DNA",
            target_word_offset_sec=1.6,
        )
        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="Curito Porsche 911 editorial cutout on circular disc",
            word_sync=sync,
            aesthetic="auto",
        )
        self.assertIn("#ECECEC", stitched.location_background)
        self.assertIn("paper canvas", stitched.location_background.lower())


class GoogleFlowSessionManagerTests(unittest.TestCase):
    """Test persistent session manager, cookie serialization, and keep-alive configuration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="session_test_")
        self.auth_file = Path(self.temp_dir) / "test_auth.json"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cookie_serialization_and_roundtrip(self):
        """Cookies are saved and loaded atomically with last_synced_utc timestamp."""
        test_cookies = [
            {"name": "__Secure-1PSIDTS", "value": "test_sidts_val", "domain": ".google.com"},
            {"name": "SID", "value": "test_sid_val", "domain": ".google.com"},
            {"name": "OSID", "value": "test_osid_val", "domain": "flow.google.com"},
        ]
        mgr = GoogleFlowSessionManager(profile_dir=Path(self.temp_dir), auth_json_path=self.auth_file)
        mgr.save_stored_cookies(test_cookies, self.auth_file)

        self.assertTrue(self.auth_file.exists())
        loaded = mgr.load_stored_cookies(self.auth_file)
        self.assertEqual(len(loaded), 3)
        self.assertEqual(loaded[0]["name"], "__Secure-1PSIDTS")
        self.assertEqual(loaded[0]["value"], "test_sidts_val")

    def test_critical_session_cookies_constants(self):
        """Critical session cookies must include all Google Flow security tokens."""
        for required_cookie in ["__Secure-1PSIDTS", "__Secure-3PSIDTS", "SID", "OSID"]:
            self.assertIn(required_cookie, CRITICAL_SESSION_COOKIES)


if __name__ == "__main__":
    unittest.main()

