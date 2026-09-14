"""Google Flow Browser Automation Engine.

Drives Google Flow (https://flow.google.com) directly using Playwright:
- Launches Chrome in headless or headed mode with dedicated automation directory
- Supports Playwright storage_state (cookies/tokens) for cloud and local parity
- Navigates to Flow, creates project, submits prompt, waits for generation, and downloads MP4
- No fake fallbacks, zero synthetic mocks: exposes exact page state and errors on failure
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from playwright.async_api import async_playwright, BrowserContext, Page, TimeoutError as PWTimeout

from mini_run_pipeline.google_flow_session import GoogleFlowSessionManager, DEFAULT_PROFILE_DIR

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
AUTOMATION_DATA_DIR = r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData"
FLOW_URL = "https://flow.google.com"
DEFAULT_OUTPUT_DIR = Path("docs/mini_run_studio/flow_clips")


class GoogleFlowBrowserEngine:
    """Automates Google Flow web application via Playwright."""

    def __init__(
        self,
        user_data_dir: str = AUTOMATION_DATA_DIR,
        chrome_path: str = CHROME_PATH,
        headless: bool = True,
        storage_state_path: Optional[str] = None,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
    ):
        self.user_data_dir = user_data_dir
        self.chrome_path = chrome_path
        self.headless = headless
        self.storage_state_path = storage_state_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_mgr = GoogleFlowSessionManager(
            profile_dir=Path(self.user_data_dir),
            auth_json_path=Path(self.storage_state_path) if self.storage_state_path else Path("config/flow_auth.json")
        )

    async def generate_video(
        self,
        prompt: str,
        output_filename: str = "flow_video.mp4",
        duration_sec: int = 6,
        aspect_ratio: str = "9:16",
        timeout_sec: int = 600,
    ) -> Path:
        """Executes full browser automation lifecycle to generate and download a video."""
        dest_path = self.output_dir / output_filename
        print(f"=== Starting Google Flow Video Generation ===")
        print(f"Prompt: {prompt[:80]}...")
        print(f"Target Output: {dest_path}")
        print(f"Headless Mode: {self.headless}")

        async with async_playwright() as p:
            launch_args = [
                "--start-maximized",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--use-gl=angle",
                "--use-angle=d3d11",
                "--disable-blink-features=AutomationControlled",
            ]

            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                executable_path=self.chrome_path,
                channel="chrome",
                headless=self.headless,
                args=launch_args,
                no_viewport=True,
            )

            # Only seed external storage state if context currently has no active cookies
            existing_cookies = await context.cookies()
            if not existing_cookies and self.storage_state_path and os.path.exists(self.storage_state_path):
                print(f"Seeding persistent context from {self.storage_state_path}...")
                with open(self.storage_state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    if "cookies" in state:
                        await context.add_cookies(state["cookies"])

            page = context.pages[0] if context.pages else await context.new_page()

            try:
                # 1. Navigate to Flow
                print(f"Navigating to {FLOW_URL} ...")
                await page.goto(FLOW_URL, timeout=45000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)

                current_url = page.url
                title = await page.title()
                print(f"Current Page: title='{title}', url='{current_url}'")

                # Check for sign-in redirect
                if "accounts.google.com" in current_url:
                    os.makedirs("scratch", exist_ok=True)
                    await page.screenshot(path="scratch/flow_auth_required.png")
                    raise PermissionError(
                        f"AUTHENTICATION REQUIRED: Google Flow redirected to {current_url}. "
                        "The browser automation profile is not signed in to Google Flow. "
                        "Sign in once or provide storage_state.json with active cookies."
                    )

                # 2. Check for landing page 'Create with Google Flow' button
                create_btn = await page.query_selector("button:has-text('Create with Google Flow')")
                if create_btn:
                    print("Clicking 'Create with Google Flow'...")
                    await create_btn.click()
                    await page.wait_for_timeout(5000)

                # Check again if redirected to login
                if "accounts.google.com" in page.url:
                    os.makedirs("scratch", exist_ok=True)
                    await page.screenshot(path="scratch/flow_auth_required.png")
                    raise PermissionError(
                        f"AUTHENTICATION REQUIRED: Google Flow requires sign-in. Redirected to: {page.url}"
                    )

                # 3. Locate prompt input
                print("Locating prompt input...")
                input_selectors = [
                    "textarea[placeholder*='describe' i]",
                    "textarea[placeholder*='prompt' i]",
                    "div[contenteditable='true']",
                    "textarea",
                ]
                prompt_el = None
                for sel in input_selectors:
                    try:
                        el = await page.wait_for_selector(sel, timeout=5000)
                        if el and await el.is_visible():
                            prompt_el = el
                            break
                    except Exception:
                        continue

                if not prompt_el:
                    os.makedirs("scratch", exist_ok=True)
                    await page.screenshot(path="scratch/flow_missing_input.png")
                    raise RuntimeError("Could not find prompt textarea on Google Flow workspace.")

                print("Typing prompt into Google Flow...")
                await prompt_el.click()
                await prompt_el.fill("")
                await prompt_el.type(prompt, delay=15)

                # 4. Click Generate
                print("Locating generate button...")
                generate_selectors = [
                    "button:has-text('Generate')",
                    "button[aria-label*='Generate' i]",
                    "button:has-text('Create')",
                ]
                gen_btn = None
                for sel in generate_selectors:
                    try:
                        btn = await page.wait_for_selector(sel, timeout=4000)
                        if btn and await btn.is_visible():
                            gen_btn = btn
                            break
                    except Exception:
                        continue

                if not gen_btn:
                    os.makedirs("scratch", exist_ok=True)
                    await page.screenshot(path="scratch/flow_missing_gen_btn.png")
                    raise RuntimeError("Could not find Generate button on Google Flow workspace.")

                await gen_btn.click()
                print("Generation triggered successfully! Waiting for output...")

                # 5. Wait for video generation and extract URL / download
                start_time = time.time()
                video_url = None
                video_selectors = [
                    "video[src]",
                    "video source",
                    "a[download][href*='.mp4']",
                    "a[href*='storage.googleapis.com']",
                ]

                while time.time() - start_time < timeout_sec:
                    elapsed = int(time.time() - start_time)

                    for v_sel in video_selectors:
                        try:
                            el = await page.query_selector(v_sel)
                            if el:
                                src = await el.get_attribute("src") or await el.get_attribute("href")
                                if src and ("mp4" in src or "blob:" in src or "storage.googleapis" in src):
                                    video_url = src
                                    print(f"\nVideo detected at {elapsed}s: {video_url[:80]}...")
                                    break
                        except Exception:
                            continue

                    if video_url:
                        break

                    await page.wait_for_timeout(5000)

                if not video_url:
                    os.makedirs("scratch", exist_ok=True)
                    await page.screenshot(path="scratch/flow_generation_timeout.png")
                    raise TimeoutError(f"Video generation timed out after {timeout_sec} seconds.")

                # 6. Download MP4
                print(f"Downloading MP4 to {dest_path}...")
                dl_btn = await page.query_selector("button:has-text('Download'), [aria-label*='download' i]")
                if dl_btn:
                    async with page.expect_download() as dl_info:
                        await dl_btn.click()
                    dl = await dl_info.value
                    await dl.save_as(str(dest_path))
                else:
                    import urllib.request
                    urllib.request.urlretrieve(video_url, str(dest_path))

                size = dest_path.stat().st_size if dest_path.exists() else 0
                if size < 10000:
                    raise RuntimeError(f"Downloaded video file is corrupt or empty ({size} bytes).")

                print(f"SUCCESS: Real Google Flow video downloaded: {dest_path} ({size:,} bytes)")
                return dest_path

            finally:
                try:
                    await self.session_mgr.sync_context_cookies(context)
                except Exception:
                    pass
                await context.close()


def launch_one_time_signin_window():
    """Launches a visible Chrome window pointing to Google Flow so the user can sign in once."""
    print("Launching visible Chrome window with AutomationData profile...")
    subprocess.Popen([
        CHROME_PATH,
        f"--user-data-dir={AUTOMATION_DATA_DIR}",
        "https://flow.google.com",
    ])
    print("Chrome window opened. Please sign in to ipsasummagnitudo@gmail.com.")
    print("Once signed in, close the window or leave it open for headless Playwright execution.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--signin":
        launch_one_time_signin_window()
    else:
        engine = GoogleFlowBrowserEngine(headless=True)
        asyncio.run(engine.generate_video(
            prompt="Porsche 911 GT3 RS cinematic commercial",
            output_filename="test_flow.mp4"
        ))
