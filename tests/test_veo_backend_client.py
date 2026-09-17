"""tests/test_veo_backend_client.py - Unit test suite for native headless Veo 3.1 client."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from mini_run_pipeline.curito_animation_dna import CuritoWordSyncSchema, CuritoStitchedPrompt
from mini_run_pipeline.veo_backend_client import VeoBackendClient, VeoGenerationResult


class VeoBackendClientTests(unittest.TestCase):
    """Test suite ensuring the VeoBackendClient operates headlessly and fails fast
    without synthetic mocks or browser dependencies.
    """

    def test_client_initialization_resolves_key(self):
        """Verify: Client successfully resolves API key from environment."""
        with patch.dict("os.environ", {"GOOGLE_AI_STUDIO_API_KEY": "test-key-12345"}):
            client = VeoBackendClient()
            self.assertEqual(client.api_key, "test-key-12345")

    def test_client_raises_without_key(self):
        """Verify: Fails fast if no API key is provided or configured."""
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(VeoBackendClient, "_resolve_api_key", return_value=None):
                with self.assertRaises(RuntimeError) as ctx:
                    VeoBackendClient()
                self.assertIn("GOOGLE_AI_STUDIO_API_KEY", str(ctx.exception))

    def test_generate_video_dispatches_with_compliant_config(self):
        """Verify: Correctly formats 9:16 vertical broadcast parameters for Veo 3.1."""
        client = VeoBackendClient(api_key="mock-key")
        
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.name = "operations/veo-test-op-123"
        mock_operation.error = None
        
        mock_video = MagicMock()
        mock_video.video.video_bytes = b"0" * 2048
        mock_result = MagicMock()
        mock_result.generated_videos = [mock_video]
        mock_operation.result = mock_result

        client.client.models.generate_videos = MagicMock(return_value=mock_operation)

        out_path = Path("scratch/test_veo_output.mp4")
        try:
            res = client.generate_curito_video(
                prompt="Cinematic Porsche GT3 RS in high-contrast chiaroscuro lighting",
                output_path=out_path,
                duration_sec=5,
                aspect_ratio="9:16",
                fps=24,
            )

            self.assertIsInstance(res, VeoGenerationResult)
            self.assertEqual(res.duration_sec, 5)
            self.assertEqual(res.aspect_ratio, "9:16")
            self.assertEqual(res.model, "veo-3.1-fast-generate-preview")
            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.read_bytes(), b"0" * 2048)

            # Verify generate_videos arguments
            call_kwargs = client.client.models.generate_videos.call_args.kwargs
            self.assertEqual(call_kwargs["model"], "veo-3.1-fast-generate-preview")
            self.assertEqual(call_kwargs["config"].aspect_ratio, "9:16")
            self.assertEqual(call_kwargs["config"].duration_seconds, 6)
        finally:
            if out_path.exists():
                out_path.unlink()

    def test_generate_video_handles_quota_error_with_actionable_guidance(self):
        """Verify: 429 RESOURCE_EXHAUSTED raises clean PermissionError with billing URL (No fake mocks!)."""
        client = VeoBackendClient(api_key="mock-key")
        client.client.models.generate_videos = MagicMock(
            side_effect=Exception("429 RESOURCE_EXHAUSTED: You exceeded your current quota")
        )

        out_path = Path("scratch/test_veo_quota_output.mp4")
        with self.assertRaises(PermissionError) as ctx:
            client.generate_curito_video(
                prompt="Test prompt",
                output_path=out_path,
            )

        self.assertIn("VEO 3.1 API QUOTA EXHAUSTED", str(ctx.exception))
        self.assertIn("Google Cloud Billing", str(ctx.exception))
        # Ensure no fake mock was created
        self.assertFalse(out_path.exists())


if __name__ == "__main__":
    unittest.main()
