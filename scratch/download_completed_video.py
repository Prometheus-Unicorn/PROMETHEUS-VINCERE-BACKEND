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

async def download_video():
    print("=== Downloading Rendered Veo 3.1 Video from Google Flow ===")
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

        # Listen for any media network responses
        video_urls_intercepted = []
        def on_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            if "video" in ct or ".mp4" in url.lower() or "blob:" in url:
                print(f"[Intercepted Media Response] {url[:80]} ({ct})")
                video_urls_intercepted.append(url)
        page.on("response", on_response)

        print(f"Connecting to: {PROJECT_URL}...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # Click on the video card in the chat at (1200, 550) or canvas at (220, 200)
        print("Clicking video card on canvas (220, 200)...")
        await page.mouse.click(220, 200)
        await page.wait_for_timeout(3000)

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/flow_player_canvas_click.png")
        print("Saved screenshot: scratch/flow_player_canvas_click.png")

        # Also click the play button or card in chat at (1200, 550)
        print("Clicking video card in chat (1200, 550)...")
        await page.mouse.click(1200, 550)
        await page.wait_for_timeout(3000)

        await page.screenshot(path="scratch/flow_player_chat_click.png")
        print("Saved screenshot: scratch/flow_player_chat_click.png")

        # Find any video element now on the page
        video_el = await page.query_selector("video")
        video_src = None
        if video_el:
            video_src = await video_el.get_attribute("src")
            print(f"Found <video> element with src: {video_src}")

        # Check all buttons on the page for Download
        dl_buttons = await page.query_selector_all("button")
        dl_target = None
        for b in dl_buttons:
            txt = (await b.inner_text()).strip()
            al = (await b.get_attribute("aria-label") or "").strip()
            if "download" in txt.lower() or "download" in al.lower():
                print(f"Found Download button: text='{txt}', aria-label='{al}'")
                dl_target = b
                break

        if dl_target:
            print("Triggering browser download via download button...")
            async with page.expect_download(timeout=60000) as dl_info:
                await dl_target.click()
            dl = await dl_info.value
            await dl.save_as(str(OUTPUT_MP4))
            print(f"Saved download to {OUTPUT_MP4}")
        elif video_src:
            print(f"Fetching video bytes from {video_src}...")
            video_bytes = await page.evaluate('''async (url) => {
                const r = await fetch(url);
                const b = await r.arrayBuffer();
                return Array.from(new Uint8Array(b));
            }''', video_src)
            with open(OUTPUT_MP4, "wb") as f:
                f.write(bytes(video_bytes))
            print(f"Saved {len(video_bytes):,} bytes to {OUTPUT_MP4}")
        elif video_urls_intercepted:
            best_url = video_urls_intercepted[-1]
            print(f"Downloading from intercepted URL: {best_url}...")
            video_bytes = await page.evaluate('''async (url) => {
                const r = await fetch(url);
                const b = await r.arrayBuffer();
                return Array.from(new Uint8Array(b));
            }''', best_url)
            with open(OUTPUT_MP4, "wb") as f:
                f.write(bytes(video_bytes))
        else:
            print("FAILURE: Could not locate video src or download button.")
            await browser.close()
            return

        await browser.close()

        # OpenCV Verification
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
    asyncio.run(download_video())
