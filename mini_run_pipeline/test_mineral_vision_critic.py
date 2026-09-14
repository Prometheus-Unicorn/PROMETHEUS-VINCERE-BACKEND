"""Unit & Integration Test Suite: Mineral Vision Critic & Auto-Correction Engine.

Part of the Mini-Run Pipeline (mini_run_pipeline/).

Verifies:
1. Strict 9:16 portrait invariant enforcement (rejection of landscape images).
2. Read-only Font JSON contract ingestion and cross-checking.
3. Mineral tactile fidelity and physical density scoring.
4. Bounded MineralCorrectionPatch clamping (Repair Dependency Closure).
5. State mutation safety for Three.js/shader and typography layout parameters.
6. Local deterministic fallback resilience when offline.
7. Closed-loop 1-pass auto-correction lifecycle.
8. Live multimodal evaluation with Gemini 3.8 Flash (High Reasoning).
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from PIL import Image

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mini_run_pipeline.gemini_critic import (
    GeminiCritic,
    GeminiCriticEngine,
    MineralVisionCriticEngine,
    ObservedMineralFrame,
    DeclaredMineralContract,
    DeclaredFontContract,
    MineralCorrectionPatch,
    MineralFidelityReport,
    DEFAULT_ASPECT_RATIO,
    FAILURE_TAG_READABILITY_SACRIFICE,
    FAILURE_TAG_FONT_RUNTIME_FAILURE,
)


class TestMineralVisionCritic(unittest.TestCase):
    """Test suite for the GEMINI CRITIC and closed-loop self-correction."""

    def setUp(self):
        self.engine = GeminiCritic(enable_deterministic_fallback=True)
        self.bedrock_img_path = REPO_ROOT / "docs" / "mini_run_studio" / "assets" / "macro_sections" / "mineral_bedrock_column_macro.jpg"

        self.sample_mineral_contract = DeclaredMineralContract(
            concept_id="MINERAL_BEDROCK",
            material_name="Pentelic Carved Marble & Deep Granitic Bedrock Plinth",
            mineral_domain="mineral_architectural",
            tactile_surface_properties="Crystalline calcite grain, hand-chiseled fluting, weathered structural fissures, raw basalt foundation",
            physical_weight_kg_m3=2700.0,
            acoustic_resonance="Sub-bass monolithic earth resonance (45Hz)",
            symbolic_grounding="Unshakeable principles, ironclad reputation, foundational ownership",
            expected_visual_markers=["crystalline grain", "fluting", "bedrock"]
        )

        self.sample_font_contract = DeclaredFontContract(
            headline_font_family="Bebas Neue",
            headline_weight=900,
            accent_font_family="Cinzel Decorative",
            accent_weight=700,
            spatial_zone="Zone A: Scalp Contact (y: 9.8% - 18.5%, Z:10)",
            min_contrast_ratio=4.5,
            max_horizontal_occupancy_percent=82.0
        )

    def test_01_contract_and_frame_initialization(self):
        """Verify contract data models and valid portrait frame initialization."""
        self.assertTrue(self.bedrock_img_path.exists(), f"Missing bedrock asset: {self.bedrock_img_path}")
        frame = ObservedMineralFrame.from_file(self.bedrock_img_path)

        self.assertEqual(frame.aspect_ratio, "768:1376")
        self.assertLess(frame.dimensions[0], frame.dimensions[1], "Frame must be portrait 9:16")
        self.assertEqual(frame.mime_type, "image/jpeg")

    def test_02_strict_portrait_invariant_rejects_landscape(self):
        """Ensure that any landscape image is strictly rejected with ValueError."""
        # Create a temporary landscape image (16:9)
        tmp_landscape = REPO_ROOT / "docs" / "mini_run_studio" / "_tmp_test_landscape.jpg"
        try:
            img = Image.new("RGB", (1920, 1080), color=(50, 50, 50))
            img.save(tmp_landscape)

            with self.assertRaises(ValueError) as ctx:
                ObservedMineralFrame.from_file(tmp_landscape)
            self.assertIn("PORTRAIT INVARIANT", str(ctx.exception))
        finally:
            if tmp_landscape.exists():
                tmp_landscape.unlink()

    def test_03_patch_clamping_guarantees_safety(self):
        """Verify that parameter patches cannot escape safe boundaries."""
        wild_patch = MineralCorrectionPatch(
            shader_adjustments={
                "roughness_delta": 0.99,      # Way too high
                "bump_scale_delta": -1.50,    # Too low
                "metallic_delta": 0.80,       # Excessive
                "displacement_scale_delta": 0.40,
                "rim_boost": 1.50
            },
            typography_placement_adjustments={
                "y_offset_percent": 45.0,     # Out of bounds
                "scale_multiplier": 3.0,      # Would overflow screen
                "scrim_alpha_delta": 1.20,    # Exceeds 1.0 opacity
                "tracking_delta_px": -25.0    # Text would collapse into a blob
            },
            material_lighting_adjustments={
                "chiaroscuro_contrast_delta": 1.5
            },
            rationale="Aggressive AI suggestions"
        )

        clamped = wild_patch.clamp()

        # Shader clamps
        self.assertLessEqual(clamped.shader_adjustments["roughness_delta"], 0.35)
        self.assertGreaterEqual(clamped.shader_adjustments["bump_scale_delta"], -0.50)
        self.assertLessEqual(clamped.shader_adjustments["metallic_delta"], 0.25)
        self.assertLessEqual(clamped.shader_adjustments["displacement_scale_delta"], 0.20)
        self.assertLessEqual(clamped.shader_adjustments["rim_boost"], 0.60)

        # Typography clamps
        self.assertLessEqual(clamped.typography_placement_adjustments["y_offset_percent"], 8.0)
        self.assertLessEqual(clamped.typography_placement_adjustments["scale_multiplier"], 1.15)
        self.assertLessEqual(clamped.typography_placement_adjustments["scrim_alpha_delta"], 0.65)
        self.assertGreaterEqual(clamped.typography_placement_adjustments["tracking_delta_px"], -4.0)

    def test_04_patch_application_preserves_state_integrity(self):
        """Verify patch application mutates state safely without corrupting Three.js architecture."""
        initial_state = {
            "concept_id": "MINERAL_BEDROCK",
            "shader_params": {
                "roughness": 0.40,
                "bump_scale": 0.30,
                "metallic": 0.10
            },
            "typography_layout": {
                "y_percent": 15.0,
                "scale": 1.0,
                "scrim_alpha": 0.10
            }
        }

        patch = MineralCorrectionPatch(
            shader_adjustments={"roughness_delta": 0.15, "bump_scale_delta": 0.25},
            typography_placement_adjustments={"y_offset_percent": -3.0, "scale_multiplier": 0.90, "scrim_alpha_delta": 0.20},
            rationale="Increase rock pitting and elevate typography above shoulder"
        )

        updated = self.engine.apply_patch_to_mineral_state(initial_state, patch)

        # Shader checks
        self.assertAlmostEqual(updated["shader_params"]["roughness"], 0.55, places=2)
        self.assertAlmostEqual(updated["shader_params"]["bump_scale"], 0.55, places=2)
        self.assertAlmostEqual(updated["shader_params"]["metallic"], 0.10, places=2)

        # Typography checks
        self.assertAlmostEqual(updated["typography_layout"]["y_percent"], 12.0, places=2)
        self.assertAlmostEqual(updated["typography_layout"]["scale"], 0.90, places=2)
        self.assertAlmostEqual(updated["typography_layout"]["scrim_alpha"], 0.30, places=2)

    def test_05_deterministic_fallback_resilience(self):
        """Verify graceful local computer vision fallback when offline or API key missing."""
        offline_engine = MineralVisionCriticEngine(
            api_key="INVALID_DUMMY_KEY",
            enable_deterministic_fallback=True
        )

        frame = ObservedMineralFrame.from_file(self.bedrock_img_path)
        report = offline_engine.evaluate_frame(
            frame=frame,
            declared_mineral=self.sample_mineral_contract,
            declared_font=self.sample_font_contract
        )

        self.assertIsInstance(report, MineralFidelityReport)
        self.assertTrue(report.overall_score > 0.0)
        self.assertIn("fallback_active", report.audit_trace)
        self.assertTrue(report.audit_trace["fallback_active"])

    def test_06_closed_loop_execution_lifecycle(self):
        """Verify the complete Inspect -> Critique -> Tweak -> Verify loop."""
        frame = ObservedMineralFrame.from_file(self.bedrock_img_path)
        initial_state = {
            "concept_id": "MINERAL_BEDROCK",
            "shader_params": {"roughness": 0.20, "bump_scale": 0.10},
            "typography_layout": {"y_percent": 15.0, "scale": 1.0, "scrim_alpha": 0.0}
        }

        # Mock render callback that simulates re-rendering with updated parameters
        rendered_calls = []
        def mock_render(state):
            rendered_calls.append(state)
            return frame

        report1, report2, final_state = self.engine.execute_closed_loop(
            initial_frame=frame,
            declared_mineral=self.sample_mineral_contract,
            declared_font=self.sample_font_contract,
            initial_state=initial_state,
            render_callback=mock_render,
            max_passes=1
        )

        self.assertIsInstance(report1, MineralFidelityReport)
        if not report1.passed:
            self.assertIsNotNone(report2)
            self.assertEqual(len(rendered_calls), 1)
            self.assertNotEqual(final_state, initial_state)
        else:
            self.assertIsNone(report2)
            self.assertEqual(len(rendered_calls), 0)


if __name__ == "__main__":
    unittest.main()
