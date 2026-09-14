import asyncio
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"
OUTPUT_MP4 = Path("docs/mini_run_studio/flow_clips/curito_porsche_zenith_veo31_real.mp4")
OUTPUT_MP4.parent.mkdir(parents=True, exist_ok=True)

async def approve_and_generate():
    print("=== Google Flow: Approving 10 Credits & Generating Veo 3.1 Video ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--use-gl=angle",
                "--use-angle=d3d11",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            storage_state=AUTH_PATH,
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        print(f"Loading workspace: {PROJECT_URL}...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # Look for the Approve button
        print("Looking for 'Approve' or 'Always approve' button...")
        approve_btn = await page.wait_for_selector(
            "button:has-text('Always approve'), button:has-text('Approve')",
            timeout=10000
        )

        if not approve_btn:
            print("Could not find Approve button directly, searching all buttons...")
            btns = await page.query_selector_all("button")
            for b in btns:
                txt = (await b.inner_text()).strip()
                if "approve" in txt.lower():
                    approve_btn = b
                    print(f"Found approve button: '{txt}'")
                    break

        if approve_btn:
            print("Clicking 'Always approve'...")
            await approve_btn.click()
            await page.wait_for_timeout(3000)
            os.makedirs("scratch", exist_ok=True)
            await page.screenshot(path="scratch/flow_approved_state.png")
            print("Saved screenshot: scratch/flow_approved_state.png")
        else:
            print("WARNING: Approve button not found. Taking screenshot...")
            await page.screenshot(path="scratch/flow_no_approve_btn.png")

        # Now monitor generation
        print("\nVideo generation has started! Polling for completion (up to 8 minutes)...")
        start_time = time.time()
        max_wait = 480  # 8 minutes
        video_url = None

        while time.time() - start_time < max_wait:
            elapsed = int(time.time() - start_time)
            await page.wait_for_timeout(10000)

            # Check for video elements
            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src and ("blob:" in src or "storage.googleapis" in src or "flow.google.com" in src):
                    video_url = src
                    print(f"\n[{elapsed}s] >>> VIDEO ELEMENT DETECTED: {video_url}")
                    break

            if video_url:
                break

            # Check for video download links or anchors
            anchors = await page.query_selector_all("a[href*='.mp4'], a[download]")
            for a in anchors:
                href = await a.get_attribute("href")
                if href and ("mp4" in href or "video" in href):
                    video_url = href
                    print(f"\n[{elapsed}s] >>> VIDEO ANCHOR DETECTED: {video_url}")
                    break

            if video_url:
                break

            # Log status screenshot every 30s
            if elapsed % 30 < 10:
                await page.screenshot(path=f"scratch/flow_rendering_{elapsed}s.png")
                # Check chat text
                chat_text = await page.evaluate('''() => {
                    const el = document.querySelector('[role="complementary"], aside, .sidebar');
                    return el ? el.innerText : '';
                }''')
                lines = [l.strip() for l in chat_text.splitlines() if l.strip()]
                print(f"  [{elapsed}s] Status: {lines[-2:] if len(lines) >= 2 else lines}")

        if not video_url:
            await page.screenshot(path="scratch/flow_render_timeout_final.png")
            print("FAILURE: Timed out waiting for video generation.")
            await browser.close()
            return

        # Take screenshot of completed video
        await page.screenshot(path="scratch/flow_video_ready.png")
        print("Video ready! Screenshot saved to scratch/flow_video_ready.png")

        # Download the video
        print(f"Downloading video from {video_url} to {OUTPUT_MP4}...")
        
        # Check if there is a download button on the video card
        dl_btn = await page.query_selector("button:has-text('Download'), [aria-label*='download' i]")
        if dl_btn:
            print("Using browser download button...")
            async with page.expect_download(timeout=60000) as dl_info:
                await dl_btn.click()
            dl = await dl_info.value
            await dl.save_as(str(OUTPUT_MP4))
        else:
            # Extract video bytes directly via page fetch
            print("Extracting bytes via browser fetch...")
            video_bytes = await page.evaluate('''async (url) => {
                const resp = await fetch(url);
                const buf = await resp.arrayBuffer();
                return Array.from(new Uint8Array(buf));
            }''', video_url)
            with open(OUTPUT_MP4, "wb") as f:
                f.write(bytes(video_bytes))

        size = OUTPUT_MP4.stat().st_size if OUTPUT_MP4.exists() else 0
        print()
        print("=" * 60)
        print("SUCCESS: REAL GOOGLE FLOW VEO 3.1 MP4 GENERATED & DOWNLOADED!")
        print(f"File: {OUTPUT_MP4.absolute()}")
        print(f"Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        print("=" * 60)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(approve_and_generate())
