import asyncio
import os
import time
import urllib.request
from pathlib import Path
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"
OUTPUT_MP4 = Path("docs/mini_run_studio/flow_clips/curito_porsche_zenith_veo31_real.mp4")
OUTPUT_MP4.parent.mkdir(parents=True, exist_ok=True)

async def run_veo_video_generation():
    print("=== Google Flow Veo 3.1 Video Generation ===")
    print(f"Connecting to session at {PROJECT_URL}...")

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

        print("Loading workspace...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        # Focus prompt input
        inputs = await page.query_selector_all('input, textarea, [contenteditable="true"]')
        target_el = None
        for el in inputs:
            rect = await el.bounding_box()
            if rect and rect['x'] > 800 and rect['y'] > 600:
                target_el = el
                break

        if not target_el:
            print("FAILURE: Could not find prompt input.")
            await browser.close()
            return

        print("Replying to Google Flow: '1. Use an 8-second duration with Veo 3.1 - Lite instead'...")
        await target_el.click()
        await page.keyboard.type("1. Use an 8-second duration with Veo 3.1 - Lite instead.", delay=5)
        await page.wait_for_timeout(500)

        # Click send
        send_pos = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
            let maxRight = null, maxX = 0;
            for (const b of btns) {
                const r = b.getBoundingClientRect();
                if (r.x > 1250 && r.y > 750 && r.width > 0 && r.x > maxX) {
                    maxX = r.x;
                    maxRight = { x: r.x + r.width/2, y: r.y + r.height/2 };
                }
            }
            return maxRight;
        }''')

        if send_pos:
            await page.mouse.click(send_pos['x'], send_pos['y'])
            print("Send button clicked!")
        else:
            await page.keyboard.press("Enter")
            print("Enter pressed!")

        print("\nGeneration triggered! Polling for video completion (up to 5 minutes)...")
        os.makedirs("scratch", exist_ok=True)

        video_src = None
        start_time = time.time()
        timeout = 360  # 6 minutes

        for poll in range(int(timeout / 10)):
            await page.wait_for_timeout(10000)
            elapsed = int(time.time() - start_time)
            print(f"  [{elapsed}s] Polling for video...")

            # Check for any video element
            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src and ("blob:" in src or "http" in src or "storage" in src):
                    video_src = src
                    print(f"\n>>> VIDEO DETECTED: {video_src}")
                    break

            if video_src:
                break

            # Save status screenshot every 30s
            if elapsed % 30 < 10:
                await page.screenshot(path=f"scratch/flow_render_status_{elapsed}s.png")

            # Check sidebar text for progress updates
            chat_text = await page.evaluate('''() => {
                const el = document.querySelector('[role="complementary"], aside, .sidebar');
                return el ? el.innerText : '';
            }''')
            if chat_text:
                lines = [l.strip() for l in chat_text.splitlines() if l.strip()]
                last_line = lines[-1] if lines else ""
                print(f"    Status: {last_line[:80]}")

        if not video_src:
            await page.screenshot(path="scratch/flow_render_timeout.png")
            print("FAILURE: Timed out waiting for video generation.")
            await browser.close()
            return

        # Screenshot completed video
        await page.screenshot(path="scratch/flow_video_completed.png")
        print("Video completed! Screenshot saved to scratch/flow_video_completed.png")

        # Extract download URL or use browser download
        print(f"Attempting download of video: {video_src} ...")
        
        # Look for download button
        dl_btn = await page.query_selector("button[aria-label*='download' i], button:has-text('Download'), [data-action*='download' i]")
        if dl_btn:
            print("Found download button, triggering download...")
            async with page.expect_download(timeout=60000) as dl_info:
                await dl_btn.click()
            dl = await dl_info.value
            await dl.save_as(str(OUTPUT_MP4))
        else:
            # If blob or direct URL
            print("Extracting video bytes directly from page...")
            video_bytes = await page.evaluate('''async (src) => {
                const resp = await fetch(src);
                const buf = await resp.arrayBuffer();
                return Array.from(new Uint8Array(buf));
            }''', video_src)
            with open(OUTPUT_MP4, "wb") as f:
                f.write(bytes(video_bytes))

        size = OUTPUT_MP4.stat().st_size if OUTPUT_MP4.exists() else 0
        print("=" * 60)
        print("SUCCESS: Real Google Flow / Veo MP4 generated and saved!")
        print(f"File: {OUTPUT_MP4.absolute()}")
        print(f"Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        print("=" * 60)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_veo_video_generation())
