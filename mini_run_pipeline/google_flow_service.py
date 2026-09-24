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


def is_cdp_endpoint_alive(url: str = "http://127.0.0.1:9222", timeout_sec: float = 1.0) -> bool:
    """Returns True if a Chrome DevTools Protocol endpoint is responding to /json/version."""
    import urllib.request
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/json/version")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode())
            return "webSocketDebuggerUrl" in data or "Browser" in data
    except Exception:
        return False


def launch_dedicated_chrome_cdp(
    profile_dir: Path,
    chrome_path: Optional[str] = None,
    headless: bool = True,
    port: int = 9222,
) -> Optional[subprocess.Popen]:
    if chrome_path:
        resolved_chrome = resolve_browser_executable(chrome_path)
        if not resolved_chrome:
            return None
    else:
        resolved_chrome = resolve_browser_executable() or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not (Path(resolved_chrome).exists() or shutil.which(resolved_chrome)):
        return None

    profile_dir = Path(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)

    args = [
        str(resolved_chrome),
        f"--user-data-dir={profile_dir.resolve()}",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    if headless:
        args.append("--headless=new")
    if sys.platform == "win32":
        args.extend(["--use-gl=angle", "--use-angle=d3d11"])

    args.append("about:blank")
    logger.info(f"Launching native Chrome with dedicated profile {profile_dir} on CDP port {port}...")
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    except Exception as exc:
        logger.warning(f"Failed to launch native Chrome CDP: {exc}")
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
    cdp_url: Optional[str] = field(default_factory=lambda: os.environ.get("FLOW_CDP_URL"))
    dedicated_profile_dir: Optional[Path] = field(
        default_factory=lambda: Path(os.environ["FLOW_DEDICATED_PROFILE"])
        if "FLOW_DEDICATED_PROFILE" in os.environ
        else (Path(r"C:\Users\HomePC\.prometheus_flow_user_data") if sys.platform == "win32" and Path(r"C:\Users\HomePC\.prometheus_flow_user_data").exists() else None)
    )


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

        logger.info("Generation dispatch executed. Checking for instant credit approval...")
        from .flow_job_tracker import FlowJobTracker
        for _ in range(8):
            await page.wait_for_timeout(1000)
            approved = await FlowJobTracker.resolve_credit_approval(page)
            if approved:
                logger.info(f"Instant credit approval resolved: Clicked '{approved}'")
                await page.wait_for_timeout(1500)
                break


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
            
            # Step 1: Connection Strategy: Active CDP -> Dedicated Profile Chrome -> Persistent Context
            cdp_target = self.config.cdp_url or "http://127.0.0.1:9222"
            dedicated_proc: Optional[subprocess.Popen] = None
            is_cdp_mode = False

            if is_cdp_endpoint_alive(cdp_target):
                logger.info(f"Active CDP endpoint detected at {cdp_target}. Utilizing live browser session.")
                is_cdp_mode = True
            elif self.config.dedicated_profile_dir and self.config.dedicated_profile_dir.exists() and sys.platform == "win32":
                dedicated_proc = launch_dedicated_chrome_cdp(
                    profile_dir=self.config.dedicated_profile_dir,
                    chrome_path=self.config.chrome_path,
                    headless=self.config.headless,
                )
                if dedicated_proc:
                    for _ in range(12):
                        await asyncio.sleep(0.5)
                        if is_cdp_endpoint_alive(cdp_target):
                            is_cdp_mode = True
                            logger.info(f"Dedicated native Chrome CDP online at {cdp_target}.")
                            break

            if not is_cdp_mode:
                FlowProcessManager.kill_stale_chrome_processes(self.config.profile_dir)
                FlowProcessManager.cleanup_stale_locks(self.config.profile_dir)

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
                browser = None
                if is_cdp_mode:
                    browser = await p.chromium.connect_over_cdp(cdp_target)
                    context = browser.contexts[0] if browser.contexts else await browser.new_context(
                        viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
                        accept_downloads=True,
                    )
                else:
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
                    for attempt in range(1, 4):
                        try:
                            await page.goto("https://flow.google.com/", timeout=45000, wait_until="commit")
                            await asyncio.sleep(5.0)
                            break
                        except Exception as e_root:
                            logger.warning(f"Root domain navigation attempt {attempt}/3 warning: {e_root}")
                            if attempt == 3:
                                break
                            await asyncio.sleep(attempt * 3.0)

                    logger.info(f"Navigating to workspace: {self.config.workspace_url}")
                    for attempt in range(1, 6):
                        try:
                            logger.info(f"Workspace navigation attempt {attempt}/5...")
                            await page.goto(self.config.workspace_url, timeout=60000, wait_until="commit")
                            await asyncio.sleep(6.0)
                            break
                        except Exception as nav_err:
                            logger.warning(f"Workspace navigation attempt {attempt}/5 failed: {nav_err}")
                            if attempt == 5:
                                raise nav_err
                            backoff = attempt * 5.0
                            logger.info(f"Retrying workspace navigation in {backoff}s...")
                            await asyncio.sleep(backoff)

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
                    if is_cdp_mode and browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass
                        if dedicated_proc:
                            try:
                                dedicated_proc.terminate()
                                dedicated_proc.wait(timeout=3)
                            except Exception:
                                pass
                    else:
                        await context.close()
