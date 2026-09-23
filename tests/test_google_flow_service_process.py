"""Tests for FlowProcessManager and FlowSessionValidator."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from mini_run_pipeline.google_flow_service import FlowProcessManager, FlowSessionValidator


class TestFlowProcessManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_stale_locks(self):
        lock_file = self.temp_dir / "SingletonLock"
        lock_file.write_text("dummy-lock")
        self.assertTrue(lock_file.exists())

        FlowProcessManager.cleanup_stale_locks(self.temp_dir)
        self.assertFalse(lock_file.exists())

    def test_cleanup_stale_lock_dir(self):
        lock_dir = self.temp_dir / "SingletonCookie"
        lock_dir.mkdir()
        self.assertTrue(lock_dir.exists())

        FlowProcessManager.cleanup_stale_locks(self.temp_dir)
        self.assertFalse(lock_dir.exists())


class TestFlowSessionValidator(unittest.IsolatedAsyncioTestCase):
    async def test_redirect_to_signin_raises_permission_error(self):
        mock_page = MagicMock()
        mock_page.url = "https://accounts.google.com/signin/v2/identifier"
        mock_page.screenshot = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.wait_for_timeout = AsyncMock()

        with self.assertRaises(PermissionError) as ctx:
            await FlowSessionValidator.validate_session_active(mock_page, timeout_ms=500)
        self.assertIn("Google Flow session expired", str(ctx.exception))

    async def test_workspace_detected_immediately(self):
        mock_page = MagicMock()
        mock_page.url = "https://flow.google.com/project/0431f510-bbad-4c90-8157-f1723008eea3"
        mock_elem = MagicMock()
        mock_elem.is_visible = AsyncMock(return_value=True)
        mock_page.query_selector = AsyncMock(return_value=mock_elem)

        result = await FlowSessionValidator.validate_session_active(mock_page, timeout_ms=2000)
        self.assertTrue(result)

    async def test_about_page_transition_to_workspace(self):
        mock_page = MagicMock()
        urls = [
            "https://flow.google.com/about",
            "https://flow.google.com/project/0431f510-bbad-4c90-8157-f1723008eea3",
        ]
        def get_url():
            return urls[1] if mock_btn.click.called else urls[0]

        type(mock_page).url = property(lambda self: get_url())
        mock_btn = MagicMock()
        mock_btn.click = AsyncMock()
        mock_ws = MagicMock()
        mock_ws.is_visible = AsyncMock(return_value=True)

        async def mock_qs(selector):
            if "Create with Google Flow" in selector:
                return mock_btn
            if "ProseMirror" in selector:
                return mock_ws if mock_btn.click.called else None
            return None

        mock_page.query_selector = AsyncMock(side_effect=mock_qs)
        mock_page.wait_for_url = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        result = await FlowSessionValidator.validate_session_active(mock_page, timeout_ms=4000)
        self.assertTrue(result)
        self.assertTrue(mock_btn.click.called)

    async def test_timeout_raises_timeout_error(self):
        mock_page = MagicMock()
        mock_page.url = "https://flow.google.com/unknown"
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.screenshot = AsyncMock()

        with self.assertRaises(TimeoutError) as ctx:
            await FlowSessionValidator.validate_session_active(mock_page, timeout_ms=200)
        self.assertIn("Workspace hydration timed out", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
