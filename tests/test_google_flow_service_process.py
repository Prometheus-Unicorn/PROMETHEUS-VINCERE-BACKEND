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

        with self.assertRaises(PermissionError) as ctx:
            await FlowSessionValidator.validate_session_active(mock_page, timeout_ms=500)
        self.assertIn("Google Flow session expired", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
