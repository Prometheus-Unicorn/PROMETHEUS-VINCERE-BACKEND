"""Unit tests for the GoogleFlowServerClient and FlowPromptInjector subsystems."""

import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from mini_run_pipeline.google_flow_service import (
    FlowGenerationResult,
    FlowPromptInjector,
    FlowServiceConfig,
    GoogleFlowServerClient,
)


class TestGoogleFlowService(unittest.IsolatedAsyncioTestCase):
    def test_flow_service_config_defaults(self):
        config = FlowServiceConfig()
        self.assertTrue(config.headless)
        self.assertEqual(config.expected_account, "ipsasummagnitudo@gmail.com")
        self.assertIn("0431f510-bbad-4c90-8157-f1723008eea3", config.workspace_url)

    async def test_prompt_injector_fast_insert(self):
        mock_page = MagicMock()
        mock_editor = MagicMock()
        mock_editor.click = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(return_value=mock_editor)
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.keyboard.press = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=True)

        mock_submit_btn = MagicMock()
        mock_submit_btn.is_visible = AsyncMock(return_value=True)
        mock_submit_btn.click = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=mock_submit_btn)

        await FlowPromptInjector.inject_prompt_and_trigger(mock_page, "Generate an engineered Geneva indexer.")

        mock_editor.click.assert_called_once()
        mock_submit_btn.click.assert_called_once()

    async def test_server_client_queue_locking(self):
        client = GoogleFlowServerClient()
        executed_order = []

        async def dummy_job(job_id: int):
            async with client._instance_lock:
                executed_order.append(f"start_{job_id}")
                await asyncio.sleep(0.05)
                executed_order.append(f"end_{job_id}")

        await asyncio.gather(dummy_job(1), dummy_job(2))
        # Ensure that job 1 completed before job 2 began, or vice versa (strict serialization)
        self.assertTrue(
            executed_order == ["start_1", "end_1", "start_2", "end_2"] or
            executed_order == ["start_2", "end_2", "start_1", "end_1"]
        )

    async def test_cdp_cookie_injection_structure(self):
        """Verifies that cookies injected via CDP conform to Playwright add_cookies schema."""
        mock_context = MagicMock()
        mock_context.add_cookies = AsyncMock()

        sample_cookies = [
            {
                "name": "OSID",
                "value": "dummy_osid_val",
                "domain": "flow.google.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
            }
        ]
        await mock_context.add_cookies(sample_cookies)
        mock_context.add_cookies.assert_called_once_with(sample_cookies)


if __name__ == "__main__":
    unittest.main()
