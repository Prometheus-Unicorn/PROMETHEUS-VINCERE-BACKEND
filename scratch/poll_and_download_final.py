import asyncio
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright
import cv2

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"
OUTPUT_MP4 = Path("docs/mini_run_studio/flow_clips/curito_porsche_zenith_veo31_real.mp4")
OUTPUT_MP4.parent.mkdir(parents=True, exist_ok=True)

async def poll_and_download():
    print("=== Google Flow: Monitoring Render Completion & Downloading MP4 ===")
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

        print(f"Connecting to project: {PROJECT_URL}...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        start_time = time.time()
        timeout = 600  # 10 minutes max
        video_src = None

        print("Polling progress...")
        os.makedirs("scratch", exist_ok=True)

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)

            # Check for completed video element
            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src and ("blob:" in src or "storage.googleapis" in src or "http" in src):
                    video_src = src
                    print(f"\n[{elapsed}s] >>> VIDEO ELEMENT DETECTED: {video_src}")
                    break

            if video_src:
                break

            # Check percentage on the canvas card
            percent_text = await page.evaluate('''() => {
                const els = document.querySelectorAll('*');
                for (const el of els) {
                    const txt = el.innerText || '';
                    if (/\\d+%/.test(txt) && el.children.length === 0) {
                        return txt.trim();
                    }
                }
                return null;
            }''')

            if percent_text:
                print(f"  [{elapsed}s] Render Progress: {percent_text}")
            else:
                print(f"  [{elapsed}s] Checking video tiles...")

            # Check if there is a completed video tile on the canvas or sidebar
            completed_tile = await page.query_selector("div:has-text('Videos'), [aria-label*='video' i]")

            # Take periodic screenshots
            if elapsed % 30 < 10:
                await page.screenshot(path=f"scratch/poll_render_{elapsed}s.png")

            await page.wait_for_timeout(10000)

        # If video element not immediately found, click on the video tile on canvas
        if not video_src:
            print("Checking canvas video tile...")
            # In screenshot, video card is at x ~ 220, y ~ 150
            await page.mouse.click(220, 200)
            await page.wait_for_timeout(3000)
            await page.screenshot(path="scratch/flow_video_tile_clicked.png")

            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src:
                    video_src = src
                    break

        if not video_src:
            # Check all network or media elements
            media_urls = await page.evaluate('''() => {
                const urls = [];
                document.querySelectorAll('video, source, a[download], a[href*=".mp4"]').forEach(el => {
                    const src = el.src || el.href || el.getAttribute('src');
                    if (src) urls.push(src);
                });
                return urls;
            }''')
            print("Detected media URLs:", media_urls)
            if media_urls:
                video_src = media_urls[0]

        if not video_src:
            await page.screenshot(path="scratch/flow_poll_timeout.png")
            print("FAILURE: Render timed out or could not find video URL.")
            await browser.close()
            return

        print(f"\nProceeding to download video from: {video_src[:80]}...")
        await page.screenshot(path="scratch/flow_final_render_success.png")

        # Download via browser download button or fetch
        dl_btn = await page.query_selector("button:has-text('Download'), [aria-label*='download' i], button:has(span:has-text('download'))")
        if dl_btn:
            print("Clicking download button...")
            async with page.expect_download(timeout=60000) as dl_info:
                await dl_btn.click()
            dl = await dl_info.value
            await dl.save_as(str(OUTPUT_MP4))
        else:
            print("Fetching video bytes via browser context...")
            video_bytes = await page.evaluate('''async (url) => {
                const res = await fetch(url);
                const buf = await res.arrayBuffer();
                return Array.from(new Uint8Array(buf));
            }''', video_src)
            with open(OUTPUT_MP4, "wb") as f:
                f.write(bytes(video_bytes))

        await browser.close()

        # Verify downloaded MP4
        size = OUTPUT_MP4.stat().st_size if OUTPUT_MP4.exists() else 0
        if size < 10000:
            print(f"FAILURE: File size is {size} bytes.")
            return

        cap = cv2.VideoCapture(str(OUTPUT_MP4))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frames / fps if fps > 0 else 0
        cap.release()

        print()
        print("=" * 65)
        print("★ SUCCESS: REAL GOOGLE FLOW VEO 3.1 MP4 DOWNLOADED & VERIFIED! ★")
        print(f"Output File: {OUTPUT_MP4.absolute()}")
        print(f"File Size:   {size:,} bytes ({size/1024/1024:.2f} MB)")
        print(f"Resolution:  {width}x{height}")
        print(f"Duration:    {duration:.2f} seconds ({frames} frames @ {fps} fps)")
        print("=" * 65)

if __name__ == "__main__":
    asyncio.run(poll_and_download())
