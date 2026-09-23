"""Unit tests for cross-platform browser resolution and process cleanup in Google Flow automation."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mini_run_pipeline.flow_session_manager import FlowProcessManager
from mini_run_pipeline.google_flow_service import (
    FlowServiceConfig,
    resolve_browser_executable,
)


class TestGoogleFlowCrossPlatform(unittest.TestCase):
    def test_flow_service_config_defaults(self):
        """FlowServiceConfig defaults chrome_path to None for automatic dynamic cross-platform resolution."""
        config = FlowServiceConfig()
        self.assertIsNone(config.chrome_path)
        self.assertTrue(config.headless)
        self.assertEqual(config.expected_account, "ipsasummagnitudo@gmail.com")

    def test_resolve_browser_executable_with_custom_path(self):
        """Custom executable path is respected if provided."""
        dummy_path = sys.executable  # python.exe is guaranteed to exist
        resolved = resolve_browser_executable(dummy_path)
        self.assertEqual(resolved, dummy_path)

    def test_resolve_browser_executable_with_env_var(self):
        """CHROME_PATH environment variable overrides default search."""
        dummy_path = sys.executable
        with patch.dict(os.environ, {"CHROME_PATH": dummy_path}):
            resolved = resolve_browser_executable()
            self.assertEqual(resolved, dummy_path)

    def test_resolve_browser_executable_linux_discovery(self):
        """Simulates Linux environment finding google-chrome via which."""
        with patch.object(sys, "platform", "linux"):
            with patch("shutil.which", return_value="/usr/bin/google-chrome"):
                resolved = resolve_browser_executable()
                self.assertEqual(resolved, "/usr/bin/google-chrome")

    def test_resolve_browser_executable_fallback_none(self):
        """Returns None if no browser is found, enabling Playwright bundled Chromium fallback."""
        with patch.object(sys, "platform", "linux"):
            with patch.dict(os.environ, {}, clear=True):
                with patch("shutil.which", return_value=None):
                    with patch("pathlib.Path.exists", return_value=False):
                        resolved = resolve_browser_executable()
                        self.assertIsNone(resolved)

    def test_kill_stale_chrome_processes_posix(self):
        """FlowProcessManager.kill_stale_chrome_processes successfully invokes pgrep and kill on POSIX."""
        with patch.object(sys, "platform", "linux"):
            with patch("subprocess.check_output", return_value="101\n102\n"):
                with patch("subprocess.run") as mock_run:
                    profile_dir = Path("/tmp/flow_profile")
                    killed = FlowProcessManager.kill_stale_chrome_processes(profile_dir)
                    self.assertEqual(killed, 2)
                    self.assertEqual(mock_run.call_count, 2)
                    mock_run.assert_any_call(["kill", "-9", "101"], check=True, stdout=-3, stderr=-3)
                    mock_run.assert_any_call(["kill", "-9", "102"], check=True, stdout=-3, stderr=-3)


if __name__ == "__main__":
    unittest.main()
