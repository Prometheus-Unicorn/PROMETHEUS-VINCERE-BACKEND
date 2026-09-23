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
    def cleanup_stale_locks(profile_dir: Path | str) -> None:
        """Removes orphaned Chromium lock files that cause ProcessSingleton crashes."""
        profile_dir = Path(profile_dir)
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
    async def validate_session_active(page: Page, timeout_ms: int = 45000) -> bool:
        """Checks if the workspace is active or handles landing page and account selection redirects."""
        start_time = time.time()
        deadline = start_time + (timeout_ms / 1000.0)
        workspace_selectors = "div.ProseMirror, .prosemirror-editor, canvas, app-root, [contenteditable='true'], [role='main']"

        while time.time() < deadline:
            # Check if a new tab / popup was opened by an entry link
            if hasattr(page, "context") and hasattr(page.context, "pages") and len(page.context.pages) > 1:
                latest_page = page.context.pages[-1]
                if latest_page != page and not latest_page.is_closed():
                    try:
                        logger.info(f"Switching active target to latest tab: {latest_page.url}")
                        page = latest_page
                        await page.bring_to_front()
                    except Exception:
                        pass

            current_url = page.url
            try:
                title = await page.title()
            except Exception:
                title = "unknown"
            logger.info(f"Validating session... Current URL: {current_url}, Title: {title}")

            # 1. Workspace is active
            if "/about" not in current_url and "accounts.google.com" not in current_url:
                try:
                    ws_elem = await page.query_selector(workspace_selectors)
                    if ws_elem and await ws_elem.is_visible():
                        logger.info(f"Workspace validated active: {current_url}")
                        return True
                except Exception:
                    pass

            # Dismiss cookie consent dialogs if present
            try:
                consent_btn = await page.query_selector("button:has-text('Accept all'), button:has-text('I agree'), [aria-label*='Accept all' i]")
                if consent_btn:
                    await page.evaluate("el => el.click()", consent_btn)
                    await page.wait_for_timeout(1000)
            except Exception:
                pass

            # 2. Landed on /about landing page -> click entry button
            if "/about" in current_url:
                logger.info("Landed on /about, attempting to click entry button...")
                create_selectors = [
                    "button:has-text('Create with Google Flow')",
                    "a:has-text('Create with Google Flow')",
                    "button:has-text('Open Flow')",
                    "a:has-text('Open Flow')",
                    "a:has-text('Sign in')",
                    "button:has-text('Sign in')",
                ]
                for sel in create_selectors:
                    try:
                        create_btn = await page.query_selector(sel)
                        if create_btn:
                            logger.info(f"Clicking entry button: '{sel}'")
                            try:
                                await page.evaluate("el => el.click()", create_btn)
                            except Exception:
                                try:
                                    await create_btn.click(force=True, no_wait_after=True, timeout=5000)
                                except Exception as ce:
                                    logger.warning(f"Create button click warning: {ce}")
                            try:
                                await page.wait_for_url(lambda u: "/about" not in u, timeout=8000)
                            except Exception:
                                await page.wait_for_timeout(2000)
                            break
                    except Exception:
                        continue

            # 3. Google Account Chooser -> automatically select account
            current_url = page.url
            has_acct_elem = False
            try:
                has_acct_elem = bool(await page.query_selector("[data-email*='ipsasummagnitudo'], [data-identifier*='ipsasummagnitudo']"))
            except Exception:
                pass

            if "accountchooser" in current_url or has_acct_elem:
                logger.info("Landed on Google Account Chooser. Attempting automatic account selection...")
                account_selectors = [
                    "[data-email*='ipsasummagnitudo'], [data-identifier*='ipsasummagnitudo']",
                    "div:has-text('ipsasummagnitudo@gmail.com'), li:has-text('ipsasummagnitudo@gmail.com')",
                    "[data-email], [data-identifier]",
                    "div[role='link']:has(div[data-email])",
                    "li:has([data-email])",
                    "ul li:first-child",
                ]
                for sel in account_selectors:
                    try:
                        btn = await page.wait_for_selector(sel, timeout=3000)
                        if btn:
                            logger.info(f"Found account item with selector '{sel}', clicking...")
                            try:
                                await page.evaluate("el => el.click()", btn)
                            except Exception:
                                try:
                                    await btn.click(force=True, no_wait_after=True, timeout=5000)
                                except Exception as be:
                                    logger.warning(f"Account button click warning: {be}")
                            try:
                                await page.wait_for_url(lambda u: "accountchooser" not in u, timeout=8000)
                            except Exception:
                                await page.wait_for_timeout(2000)
                            break
                    except Exception:
                        continue

            # 4. Google ServiceLogin in progress -> wait for redirect
            current_url = page.url
            if "ServiceLogin" in current_url:
                logger.info("Google ServiceLogin in progress, waiting for redirect...")
                try:
                    await page.wait_for_url(lambda u: "ServiceLogin" not in u, timeout=10000)
                except Exception:
                    await page.wait_for_timeout(2000)

            # 5. Redirected to password challenge or rejected auth
            current_url = page.url
            if (
                ("accounts.google.com" in current_url or "signin" in current_url)
                and "accountchooser" not in current_url
                and "ServiceLogin" not in current_url
            ):
                scratch_dir = REPO_ROOT / "scratch"
                scratch_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = scratch_dir / "flow_auth_challenge.png"
                try:
                    await page.screenshot(path=str(screenshot_path), timeout=5000)
                except Exception as se:
                    logger.warning(f"Diagnostic screenshot failed: {se}")
                raise PermissionError(
                    f"Google Flow session expired or redirected to sign-in: {current_url}. "
                    f"Diagnostic screenshot saved to {screenshot_path}"
                )

            await page.wait_for_timeout(2000)

        # Timeout reached
        scratch_dir = REPO_ROOT / "scratch"
        scratch_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = scratch_dir / "flow_hydration_failed.png"
        try:
            await page.screenshot(path=str(screenshot_path), timeout=5000)
        except Exception as se:
            logger.warning(f"Hydration screenshot failed: {se}")
        raise TimeoutError(
            f"Workspace hydration timed out after {timeout_ms}ms. URL: {page.url}. "
            f"Screenshot: {screenshot_path}"
        )
