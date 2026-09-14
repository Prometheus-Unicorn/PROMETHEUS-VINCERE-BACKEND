"""
Google Flow Browser Automation — Real End-to-End Video Generation.

Strategy:
  - Use Playwright launch_persistent_context() with the real Chrome Profile 12
  - Navigate to labs.google/fx/tools/flow
  - Type the Curito prompt into the Flow UI
  - Click Generate
  - Poll until the video appears
  - Download the MP4

No API keys. No mocks. No fallback. Explicit failure if anything breaks.
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# --- Config ---
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\Users\HomePC\AppData\Local\Google\Chrome\User Data"
PROFILE_DIR = "Profile 12"
FLOW_URL = "https://labs.google/fx/tools/flow"
OUTPUT_DIR = Path("docs/mini_run_studio/flow_clips")
OUTPUT_MP4 = OUTPUT_DIR / "curito_porsche_zenith_flow_real.mp4"
GENERATION_TIMEOUT_MS = 600_000  # 10 minutes

# --- Curito Prompt ---
PROMPT = (
    "Top-down orthographic zenith perspective of a sculpted white Porsche 911 GT3 RS "
    "with carbon fiber dual hood vents and massive rear wing, anchored by deep ambient "
    "occlusion floor contact shadows, flanked by radial clock hands and precision compass "
    "needles sweeping dynamically and snapping to magnetic lock. "
    "Dramatic chiaroscuro contrast with intense warm 3200K tungsten spotlight, "
    "volumetric shafts of light cutting through dusty studio air, "
    "razor cool cyan rim backlighting throwing sharp directional highlights across bodywork. "
    "Vertical 9:16 composition, 35mm anamorphic lens, shallow depth of field, "
    "smooth oval anamorphic bokeh, continuous anti-stagnation sub-pixel drift, "
    "24fps cadence, subtle Kodak 5219 film grain, "
    "high-agency luxury automotive editorial motion design, crisp vector edges."
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def run_flow_generation():
    print("=== Google Flow Browser Automation ===")
    print(f"Profile: {PROFILE_DIR} (ipsasummagnitudo@gmail.com)")
    print(f"URL: {FLOW_URL}")
    print()

    # Kill any running Chrome to free the profile lock
    print("Stopping any running Chrome instances to free profile lock...")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    await asyncio.sleep(2)

    async with async_playwright() as p:
        print("Launching Chrome with persistent context (Profile 12)...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            executable_path=CHROME_PATH,
            args=[
                f"--profile-directory={PROFILE_DIR}",
                "--start-maximized",
            ],
            headless=False,   # visible so we can debug if needed
            no_viewport=True,
        )
        print("Browser launched.")

        page = context.pages[0] if context.pages else await context.new_page()

        # --- Step 1: Navigate to Google Flow ---
        print(f"\nNavigating to {FLOW_URL} ...")
        try:
            await page.goto(FLOW_URL, timeout=60_000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)
        except PWTimeout:
            print("FAILURE: Timed out navigating to Google Flow (60s).")
            await context.close()
            sys.exit(1)

        current_url = page.url
        title = await page.title()
        print(f"Page: title='{title}', url='{current_url}'")

        # --- Step 2: Check authentication ---
        if "accounts.google.com" in current_url or "signin" in current_url.lower():
            print()
            print("=" * 60)
            print("FAILURE: Google is requesting sign-in.")
            print("The session for ipsasummagnitudo@gmail.com is not active in Profile 12.")
            print("Action required: Manually sign in to this account in Chrome Profile 12,")
            print("then rerun this script.")
            print("=" * 60)
            await context.close()
            sys.exit(1)

        print("Session looks active — no sign-in redirect.")
        
        # Screenshot the initial state
        await page.screenshot(path="scratch/flow_step1_loaded.png")
        print("Screenshot saved: scratch/flow_step1_loaded.png")

        # --- Step 3: Find and fill the prompt input ---
        print("\nLooking for the Flow prompt input field...")
        
        # Google Flow prompt input selectors (try multiple)
        prompt_selectors = [
            "textarea[placeholder*='prompt' i]",
            "textarea[placeholder*='describe' i]",
            "textarea[aria-label*='prompt' i]",
            "div[contenteditable='true']",
            "textarea",
            "input[type='text']",
        ]
        
        prompt_input = None
        for selector in prompt_selectors:
            try:
                el = await page.wait_for_selector(selector, timeout=5000)
                if el:
                    prompt_input = el
                    print(f"Found prompt input: '{selector}'")
                    break
            except PWTimeout:
                continue

        if prompt_input is None:
            # Take a screenshot to see what's on screen
            await page.screenshot(path="scratch/flow_step2_no_input.png")
            print("FAILURE: Could not find the prompt input field on the page.")
            print("Screenshot saved: scratch/flow_step2_no_input.png")
            print("The page structure may have changed, or Google Flow requires additional setup.")
            await context.close()
            sys.exit(1)

        # Clear and type the prompt
        await prompt_input.click()
        await prompt_input.fill("")
        await prompt_input.type(PROMPT, delay=10)
        print(f"Prompt typed ({len(PROMPT)} chars).")
        
        await page.screenshot(path="scratch/flow_step3_prompt_typed.png")
        print("Screenshot saved: scratch/flow_step3_prompt_typed.png")

        # --- Step 4: Click Generate ---
        print("\nLooking for the Generate button...")
        generate_selectors = [
            "button:has-text('Generate')",
            "button[aria-label*='Generate' i]",
            "button[data-action*='generate' i]",
            "[role='button']:has-text('Generate')",
            "button:has-text('Create')",
        ]
        
        generate_btn = None
        for sel in generate_selectors:
            try:
                btn = await page.wait_for_selector(sel, timeout=5000)
                if btn:
                    generate_btn = btn
                    print(f"Found generate button: '{sel}'")
                    break
            except PWTimeout:
                continue

        if generate_btn is None:
            await page.screenshot(path="scratch/flow_step4_no_button.png")
            print("FAILURE: Could not find the Generate button.")
            print("Screenshot saved: scratch/flow_step4_no_button.png")
            await context.close()
            sys.exit(1)

        await generate_btn.click()
        print("Generate clicked. Video generation started.")
        print(f"Waiting up to {GENERATION_TIMEOUT_MS // 1000}s for video to appear...")

        await page.screenshot(path="scratch/flow_step5_generating.png")
        print("Screenshot saved: scratch/flow_step5_generating.png")

        # --- Step 5: Wait for video to appear ---
        video_selectors = [
            "video[src]",
            "video source",
            "a[download][href*='.mp4']",
            "a[href*='storage.googleapis.com'][href*='.mp4']",
            "button:has-text('Download')",
            "[aria-label*='download' i]",
        ]

        video_url = None
        start = time.time()

        while time.time() - start < GENERATION_TIMEOUT_MS / 1000:
            elapsed = int(time.time() - start)

            for sel in video_selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        href = await el.get_attribute("href") or await el.get_attribute("src")
                        if href and ("mp4" in href.lower() or "storage.googleapis" in href.lower()):
                            video_url = href
                            print(f"\n[{elapsed}s] Video URL found: {video_url[:80]}...")
                            break
                except Exception:
                    continue

            if video_url:
                break

            # Check for error messages
            for err_sel in ["[role='alert']", ".error-message", "[aria-live='assertive']"]:
                try:
                    err = await page.query_selector(err_sel)
                    if err:
                        err_text = await err.inner_text()
                        if err_text.strip():
                            print(f"[{elapsed}s] Error message on page: {err_text[:200]}")
                except Exception:
                    pass

            print(f"  [{elapsed}s] Still generating...", end="\r")
            await page.wait_for_timeout(5000)

        if not video_url:
            await page.screenshot(path="scratch/flow_step6_timeout.png")
            print(f"\nFAILURE: Video did not appear within {GENERATION_TIMEOUT_MS // 1000}s.")
            print("Screenshot saved: scratch/flow_step6_timeout.png")
            await context.close()
            sys.exit(1)

        # --- Step 6: Download the MP4 ---
        print(f"\nDownloading MP4 from: {video_url[:100]}...")

        import urllib.request
        try:
            urllib.request.urlretrieve(video_url, str(OUTPUT_MP4))
        except Exception as e:
            # Try via page download
            print(f"Direct download failed ({e}). Trying browser download...")
            async with page.expect_download() as dl_info:
                # Click download button or navigate to URL
                download_btn = await page.query_selector("button:has-text('Download'), [aria-label*='download' i]")
                if download_btn:
                    await download_btn.click()
                else:
                    await page.goto(video_url)
            dl = await dl_info.value
            await dl.save_as(str(OUTPUT_MP4))

        await context.close()

        size = OUTPUT_MP4.stat().st_size if OUTPUT_MP4.exists() else 0
        if size < 10000:
            print(f"FAILURE: Output file is {size} bytes — corrupt or missing.")
            sys.exit(1)

        print()
        print("=" * 60)
        print("SUCCESS: Real Google Flow / Veo MP4 generated and saved.")
        print(f"File: {OUTPUT_MP4.absolute()}")
        print(f"Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        print("=" * 60)


asyncio.run(run_flow_generation())
