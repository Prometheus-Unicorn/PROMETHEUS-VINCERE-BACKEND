"""Production-Grade Headless Google Flow Automation Service.

Provides a robust, server-executable subsystem for driving Google Flow (flow.google.com)
headlessly via Playwright with:
1. FlowProcessManager: Automatic stale process / SingletonLock cleanup to prevent crashes.
2. FlowSessionValidator: Pre-flight session health and anti-bot challenge detection.
3. FlowPromptInjector: Multi-strategy resilient prompt dock resolution & instant injection.
4. FlowJobTracker & Downloader: Delta card detection, 0-100% progress tracking, and stream downloading.
5. GoogleFlowServerClient: Thread-safe, asyncio-locked FIFO queue for concurrent server dispatch.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import cv2
from playwright.async_api import BrowserContext, ElementHandle, Page, async_playwright

logger = logging.getLogger("google_flow_service")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [FlowService] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE = REPO_ROOT / "config" / "flow_browser_profile"
DEFAULT_WORKSPACE_URL = "https://flow.google.com/project/847e1afb-3351-417f-ba65-a546af6ea7bf"


def resolve_browser_executable(custom_path: Optional[str] = None) -> Optional[str]:
    """Dynamically resolves custom Chrome binary if requested, else defaults to Playwright's Chromium."""
    if custom_path and (Path(custom_path).exists() or shutil.which(custom_path)):
        return str(custom_path)

    env_path = os.environ.get("CHROME_PATH") or os.environ.get("BROWSER_PATH")
    if env_path and (Path(env_path).exists() or shutil.which(env_path)):
        return str(env_path)

    # None falls back to Playwright's bundled Chromium which cleanly supports CDP cookie injection
    # and avoids host Chrome AppBound encryption restrictions on Windows.
    return None


# ---------------------------------------------------------------------------
# Data Models & Results
# ---------------------------------------------------------------------------

@dataclass
class FlowServiceConfig:
    """Configuration for headless Google Flow automation service."""
    workspace_url: str = DEFAULT_WORKSPACE_URL
    profile_dir: Path = DEFAULT_PROFILE
    chrome_path: Optional[str] = None
    headless: bool = True
    timeout_sec: int = 600
    viewport_width: int = 1440
    viewport_height: int = 900
    expected_account: str = "ipsasummagnitudo@gmail.com"
    proxy_url: Optional[str] = field(default_factory=lambda: os.environ.get("FLOW_PROXY_URL"))


@dataclass
class FlowGenerationResult:
    """Deterministic result of a Google Flow generation job."""
    mp4_path: str
    file_size_bytes: int
    duration_sec: float
    width: int
    height: int
    fps: float
    frame_count: int
    prompt: str
    elapsed_sec: float
    workspace_url: str
    completed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


from .flow_session_manager import FlowProcessManager, FlowSessionValidator


# ---------------------------------------------------------------------------
# Component 3: FlowPromptInjector
# ---------------------------------------------------------------------------

class FlowPromptInjector:
    """Resilient prompt dock resolution, multi-strategy focus, and fast injection."""

    EDITOR_SELECTORS = [
        "div.ProseMirror",
        ".prosemirror-editor div[contenteditable='true']",
        "div[contenteditable='true']",
        "[aria-label*='prompt' i]",
        "textarea[placeholder*='prompt' i]",
    ]

    SUBMIT_SELECTORS = [
        "button[aria-label*='Start generation' i]",
        "button[aria-label*='Send' i]",
        "button:has(mat-icon:has-text('arrow_forward'))",
        "button:has-text('Generate')",
    ]

    @classmethod
    async def locate_editor(cls, page: Page, timeout_ms: int = 15000) -> ElementHandle:
        """Finds the prompt editor using priority selector hierarchy or relative anchoring."""
        for sel in cls.EDITOR_SELECTORS:
            try:
                el = await page.wait_for_selector(sel, timeout=3000, state="visible")
                if el:
                    return el
            except Exception:
                continue

        # Strategy B: Fallback query all contenteditables
        contenteditables = await page.query_selector_all("[contenteditable='true']")
        for ce in contenteditables:
            box = await ce.bounding_box()
            if box and box["y"] > 500:  # Bottom dock region
                return ce

        raise RuntimeError("Prompt editor dock could not be located via any selector strategy.")

    @classmethod
    async def inject_prompt_and_trigger(cls, page: Page, prompt_text: str) -> None:
        """Injects prompt and triggers generation without slow keystroke delays."""
        logger.info(f"Locating prompt editor for prompt ({len(prompt_text)} chars)...")
        editor = await cls.locate_editor(page)
        await editor.click()
        await page.wait_for_timeout(200)

        # Clear existing text
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")

        # Fast injection: try evaluate transaction first for instant insertion
        inserted = await page.evaluate(
            """(text) => {
                const el = document.querySelector('div.ProseMirror, div[contenteditable="true"]');
                if (!el) return false;
                el.focus();
                // Set text directly and dispatch input event
                document.execCommand('insertText', false, text);
                return el.innerText.length > 0;
            }""",
            prompt_text,
        )

        if not inserted:
            logger.info("Falling back to fast keyboard typing...")
            await page.keyboard.type(prompt_text, delay=2)

        await page.wait_for_timeout(500)

        # Locate submit button
        logger.info("Locating generation trigger button...")
        submit_btn = None
        for sel in cls.SUBMIT_SELECTORS:
            submit_btn = await page.query_selector(sel)
            if submit_btn and await submit_btn.is_visible():
                break

        if submit_btn:
            logger.info("Triggering generation via submit button...")
            await submit_btn.click()
        else:
            logger.info("Triggering generation via Enter key & editor dock coordinate...")
            box = await editor.bounding_box()
            if box:
                # Click send arrow to the right of editor
                await page.mouse.click(box["x"] + box["width"] + 25, box["y"] + (box["height"] / 2))
            await page.keyboard.press("Enter")

        logger.info("Generation dispatch executed.")


from .flow_job_tracker import FlowJobTracker, FlowVideoDownloader


# ---------------------------------------------------------------------------
# Component 5: GoogleFlowServerClient (Public Interface with FIFO Queue)
# ---------------------------------------------------------------------------

class GoogleFlowServerClient:
    """Thread-safe, FIFO-queued server client for headless Google Flow automation."""

    _instance_lock = asyncio.Lock()

    def __init__(self, config: Optional[FlowServiceConfig] = None):
        self.config = config or FlowServiceConfig()

    async def generate_video(
        self,
        prompt: str,
        output_path: Path | str,
        timeout_sec: Optional[int] = None,
    ) -> FlowGenerationResult:
        """Executes a queued generative video generation request on Google Flow.
        
        Guarantees serial execution through an asyncio Lock to prevent Chromium
        ProcessSingleton collisions.
        """
        output_path = Path(output_path)
        effective_timeout = timeout_sec or self.config.timeout_sec
        start_time = time.time()

        async with self._instance_lock:
            logger.info(f"Lock acquired. Initiating generation job for output: {output_path.name}")
            
            # Step 1: Process sanitization
            FlowProcessManager.kill_stale_chrome_processes(self.config.profile_dir)
            FlowProcessManager.cleanup_stale_locks(self.config.profile_dir)

            # Step 2: Launch persistent context with cross-platform browser resolution
            resolved_chrome = resolve_browser_executable(self.config.chrome_path)
            logger.info(f"Resolved browser executable: {resolved_chrome}")
            browser_args = [
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--disable-blink-features=AutomationControlled",
                "--dns-result-order=ipv4first",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            if sys.platform == "win32":
                browser_args.extend(["--use-gl=angle", "--use-angle=d3d11"])
            else:
                browser_args.extend([
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu-sandbox",
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                ])

            launch_kwargs: Dict[str, Any] = {
                "user_data_dir": str(self.config.profile_dir.resolve()),
                "headless": self.config.headless,
                "args": browser_args,
                "accept_downloads": True,
                "viewport": {
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height,
                },
            }
            if resolved_chrome:
                launch_kwargs["executable_path"] = resolved_chrome
            if self.config.proxy_url:
                launch_kwargs["proxy"] = {"server": self.config.proxy_url}
                logger.info(f"Routing browser traffic via proxy: {self.config.proxy_url.split('@')[-1]}")

            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(**launch_kwargs)
                try:
                    page = context.pages[0] if context.pages else await context.new_page()

                    # CDP cookie injection: prioritize repo config cookies, fallback to profile dir
                    cookies_file = REPO_ROOT / "config" / "flow_cookies.json"
                    if not cookies_file.exists():
                        cookies_file = self.config.profile_dir / "flow_cookies.json"
                    if cookies_file.exists():
                        try:
                            with open(cookies_file, "r", encoding="utf-8") as cf:
                                cookies_data = json.load(cf)
                            await context.add_cookies(cookies_data)
                            logger.info(f"Directly injected {len(cookies_data)} authentication cookies via CDP from {cookies_file}.")
                        except Exception as c_err:
                            logger.warning(f"CDP cookie injection warning: {c_err}")

                    # CDP download directory setup for direct file stream writing
                    try:
                        cdp = await context.new_cdp_session(page)
                        await cdp.send("Page.setDownloadBehavior", {
                            "behavior": "allow",
                            "downloadPath": str(output_path.parent.resolve()),
                        })
                    except Exception as cdp_err:
                        logger.debug(f"CDP download behavior: {cdp_err}")

                    # Browser download event listener
                    async def on_download(download):
                        try:
                            logger.info(f"Browser download event received: {download.suggested_filename}")
                            await download.save_as(str(output_path))
                            logger.info(f"Saved download to {output_path}")
                        except Exception as dl_err:
                            logger.warning(f"Download save_as failed: {dl_err}")

                    page.on("download", on_download)

                    # Network media response sniffer
                    sniffed_media_urls: List[str] = []

                    async def on_response(response):
                        try:
                            url = response.url
                            ct = response.headers.get("content-type", "")
                            if "video" in ct or "videoplayback" in url or "flow-content" in url or ".mp4" in url:
                                if not any(k in url for k in [".svg", ".png", ".jpg", ".jpeg", ".css", ".js"]):
                                    if url not in sniffed_media_urls:
                                        sniffed_media_urls.append(url)
                        except Exception:
                            pass

                    page.on("response", on_response)

                    # Step 3: Resilient Navigation
                    # Hydrate domain cookies and session root first
                    logger.info("Establishing Google Flow domain session...")
                    try:
                        await page.goto("https://flow.google.com/", timeout=45000, wait_until="commit")
                        await asyncio.sleep(5.0)
                    except Exception as e_root:
                        logger.warning(f"Root domain navigation warning: {e_root}")

                    logger.info(f"Navigating to workspace: {self.config.workspace_url}")
                    for attempt in range(1, 4):
                        try:
                            await page.goto(self.config.workspace_url, timeout=45000, wait_until="commit")
                            await asyncio.sleep(6.0)
                            break
                        except Exception as nav_err:
                            if attempt == 3:
                                raise nav_err
                            await asyncio.sleep(2.0)

                    # Step 4: Session Validation
                    await FlowSessionValidator.validate_session_active(page, timeout_ms=45000)
                    if len(context.pages) > 1:
                        page = context.pages[-1]

                    # Step 5: Snapshot Initial Video Sources
                    initial_sources = await FlowJobTracker.snapshot_video_sources(page)
                    logger.info(f"Baseline workspace state: {len(initial_sources)} existing video assets.")

                    # Step 6: Inject Prompt & Trigger Generation
                    await FlowPromptInjector.inject_prompt_and_trigger(page, prompt)

                    # Step 7: Track Job Completion
                    new_video_url = await FlowJobTracker.wait_for_new_video(
                        page=page,
                        initial_sources=initial_sources,
                        timeout_sec=effective_timeout,
                    )

                    # Step 8: Download & Verify MP4
                    meta = await FlowVideoDownloader.download_and_verify(
                        page=page,
                        video_url=new_video_url,
                        dest_path=output_path,
                        context=context,
                        sniffed_media_urls=sniffed_media_urls,
                    )

                    elapsed = time.time() - start_time
                    result = FlowGenerationResult(
                        mp4_path=str(output_path.resolve()),
                        file_size_bytes=meta["sizeBytes"],
                        duration_sec=meta["durationSec"],
                        width=meta["width"],
                        height=meta["height"],
                        fps=meta["fps"],
                        frame_count=meta["frameCount"],
                        prompt=prompt,
                        elapsed_sec=elapsed,
                        workspace_url=self.config.workspace_url,
                        completed_at=datetime.now(timezone.utc).isoformat(),
                    )
                    logger.info(f"Job completed successfully in {elapsed:.1f}s. Result: {result.mp4_path}")
                    return result

                finally:
                    await context.close()
