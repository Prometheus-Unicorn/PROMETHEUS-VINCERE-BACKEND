"""Process management and session health validation for headless Google Flow automation."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import Page

logger = logging.getLogger("flow_session_manager")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [FlowProcess] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

REPO_ROOT = Path(__file__).resolve().parent.parent


class FlowProcessManager:
    """Manages Chrome processes, cleans stale SingletonLock files, and sanitizes state."""

    @staticmethod
    def cleanup_stale_locks(profile_dir: Path) -> None:
        """Removes orphaned Chromium lock files that cause ProcessSingleton crashes."""
        lock_names = ["SingletonLock", "SingletonSocket", "SingletonCookie"]
        for name in lock_names:
            lock_file = profile_dir / name
            if lock_file.exists():
                try:
                    if lock_file.is_file() or lock_file.is_symlink():
                        lock_file.unlink()
                    elif lock_file.is_dir():
                        shutil.rmtree(lock_file, ignore_errors=True)
                    logger.info(f"Cleaned stale lock: {lock_file}")
                except Exception as e:
                    logger.warning(f"Failed removing stale lock {lock_file}: {e}")

    @staticmethod
    def kill_stale_chrome_processes(profile_dir: Path) -> int:
        """Kills any zombie chrome processes using the profile directory across Windows and POSIX."""
        killed = 0
        profile_str = str(profile_dir)

        if sys.platform == "win32":
            profile_win = profile_str.replace("\\", "\\\\")
            cmd = f'wmic process where "name=\'chrome.exe\' and commandline like \'%{profile_win}%\'" get processid'
            try:
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                pids = [int(p.strip()) for p in out.splitlines() if p.strip().isdigit()]
                for pid in pids:
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        killed += 1
                        logger.info(f"Terminated orphan Chrome process PID: {pid}")
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            # POSIX / Linux / GHA runner
            try:
                out = subprocess.check_output(["pgrep", "-f", profile_str], text=True, stderr=subprocess.DEVNULL)
                pids = [int(p.strip()) for p in out.splitlines() if p.strip().isdigit()]
                for pid in pids:
                    try:
                        subprocess.run(["kill", "-9", str(pid)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        killed += 1
                        logger.info(f"Terminated orphan Chrome process PID: {pid}")
                    except Exception:
                        pass
            except Exception:
                pass

        if killed > 0:
            time.sleep(1.0)
        return killed


class FlowSessionValidator:
    """Validates session health, checks for Google sign-in challenges, and diagnoses issues."""

    @staticmethod
    async def validate_session_active(page: Page, timeout_ms: int = 15000) -> bool:
        """Checks if the workspace is active or if Google redirected to sign-in."""
        current_url = page.url
        if "accounts.google.com" in current_url or "signin" in current_url:
            scratch_dir = REPO_ROOT / "scratch"
            scratch_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = scratch_dir / "flow_auth_challenge.png"
            await page.screenshot(path=str(screenshot_path))
            raise PermissionError(
                f"Google Flow session expired or redirected to sign-in: {current_url}. "
                f"Diagnostic screenshot saved to {screenshot_path}"
            )

        try:
            await page.wait_for_selector(
                "div.ProseMirror, .prosemirror-editor, canvas, app-root",
                timeout=timeout_ms,
            )
            return True
        except Exception as e:
            scratch_dir = REPO_ROOT / "scratch"
            scratch_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = scratch_dir / "flow_hydration_failed.png"
            await page.screenshot(path=str(screenshot_path))
            raise TimeoutError(
                f"Workspace hydration timed out. URL: {page.url}. "
                f"Screenshot: {screenshot_path}"
            ) from e
