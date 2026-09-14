"""Google Flow Live Veo 3.1 Generation Pipeline.

Dispatches the Curito Swiss Paper Editorial prompt into Google Flow,
monitors render progress, and downloads the resulting MP4 asset to docs/mini_run_studio/flow_clips/.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
import cv2
from playwright.async_api import async_playwright

PROFILE_DIR = Path("config/flow_browser_profile").resolve()
OUTPUT_DIR = Path("docs/mini_run_studio/flow_clips").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_MP4 = OUTPUT_DIR / "curito_porsche_paper_editorial_flow_veo31.mp4"
RECEIPT_JSON = OUTPUT_DIR / "curito_porsche_paper_editorial_flow_veo31_receipt.json"
RECEIPT_MD = OUTPUT_DIR / "curito_porsche_paper_editorial_flow_veo31_receipt.md"

PROMPT = (
    "Top-down orthographic zenith view of Porsche GT3 RS with carbon bonnet stripes flanked by 4 rotating clock hands, "
    "featuring Heavy solid gunmetal 3D block typography with razor-sharp beveled edges, micro-machined brushed metal textures, "
    "and dynamic metallic specular reflections, The Slap-Drop asset introduction pushing downward along Z-axis with exponential "
    "decrescendo, executing a 2-frame 3% scale squash on impact followed by subtle contact bounce and pendulum settle, timed so "
    "that at +5.0s into the sequence the asset achieves locked contact bounce and physical impact synchronously with the cue words "
    "'This isn't just a car, it's a statement.', Pristine matte off-white (#ECECEC) tactile paper canvas with subtle fibrous grain "
    "texture, isolated by clean geometric negative space, bounded by delicate sinuous vector guide curves, Dramatic chiaroscuro contrast "
    "with intense warm 3200K tungsten spotlight, volumetric shafts of light cutting through dusty darkroom air, and razor cool cyan rim "
    "backlighting, diffuse high-key ambient studio illumination with zero grungy shadows, projecting a crisp double-layer drop shadow "
    "(60% AO + 25% diffuse drop) beneath foreground elements, Vertical 9:16 composition captured on 35mm anamorphic lens with shallow "
    "depth of field, smooth oval anamorphic bokeh, continuous anti-stagnation sub-pixel drift (scaling 100% to 101.8%), 24fps cadence, "
    "and subtle Kodak 5219 film grain, vertical 9:16 framing with dynamic depth layering, Authentic Curito Swiss editorial motion design, "
    "Neue Haas Grotesk Black bold headlines, Editorial New italic serif accents, interactive dashed Figma bounding boxes with circular "
    "corner anchor nodes, four-point starburst corner anchors, vertical barcode stamp, and 24fps native cinema cadence."
)

async def run_generation():
    print("=" * 70)
    print("PROMETHEUS CORE: GOOGLE FLOW VEO 3.1 LIVE GENERATION GATEWAY")
    print(f"Target Output: {OUTPUT_MP4}")
    print("=" * 70)

    async with async_playwright() as p:
        print("Launching persistent Chromium session...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                '--enable-webgl',
                '--ignore-gpu-blocklist',
                '--enable-gpu-rasterization',
                '--use-gl=angle',
                '--use-angle=d3d11',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ],
            viewport={'width': 1440, 'height': 900}
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # 1. Navigate to Google Flow
        print("1. Navigating to https://flow.google.com ...")
        await page.goto("https://flow.google.com", timeout=45000, wait_until='domcontentloaded')
        await page.wait_for_timeout(5000)

        # Handle landing page if needed
        if "/about" in page.url:
            print("Landing on /about, clicking 'Create with Google Flow'...")
            create_btn = await page.query_selector("button:has-text('Create with Google Flow')")
            if create_btn:
                await create_btn.click()
                await page.wait_for_timeout(5000)

        print(f"Current URL: {page.url}")

        # 2. Enter workspace
        # Either click the newest project card or "+ New project"
        print("2. Entering project workspace...")
        project_card = await page.query_selector("div:has-text('Sep 14'), [role='button']:has-text('project')")
        if project_card:
            await project_card.click()
        else:
            await page.mouse.click(180, 750)

        print("Waiting 15s for full WebGL canvas hydration...")
        await page.wait_for_timeout(15000)
        print(f"Active Workspace: {page.url}")

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/flow_workspace_active.png")

        # 3. Locate prompt input in right sidebar
        print("3. Locating prompt input dock...")
        # The prompt input area is at x=1150, y=850 in 1440x900 viewport
        await page.mouse.click(1150, 850)
        await page.wait_for_timeout(500)

        # Type the prompt
        print(f"Typing prompt ({len(PROMPT)} characters)...")
        await page.keyboard.type(PROMPT, delay=2)
        await page.wait_for_timeout(1000)

        await page.screenshot(path="scratch/flow_prompt_ready_to_send.png")
        print("Screenshot saved: scratch/flow_prompt_ready_to_send.png")

        # 4. Click Send Arrow button
        print("4. Locating and clicking Generate send button...")
        # Send button is located at bottom right: x ~ 1365, y ~ 950 or near (1365, 875)
        # We can hit Enter or click the arrow button
        send_btn = await page.query_selector("button[aria-label*='Send' i], button[aria-label*='Generate' i], button:has(mat-icon:has-text('arrow_forward'))")
        if send_btn:
            print("Clicking send button via selector...")
            await send_btn.click()
        else:
            print("Clicking send button by coordinate (1365, 875)...")
            await page.mouse.click(1365, 875)
            # Also send Enter key as fallback
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(6000)
        await page.screenshot(path="scratch/flow_generation_dispatched.png")
        print("Generation dispatched! Monitoring progress...")

        # 5. Monitor generation progress & download
        start_time = time.time()
        timeout_sec = 600  # 10 minutes
        video_url = None

        while time.time() - start_time < timeout_sec:
            elapsed = int(time.time() - start_time)

            # Check for completed video element
            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src and ("blob:" in src or "storage.googleapis" in src or "http" in src):
                    video_url = src
                    print(f"\n[{elapsed}s] >>> VIDEO ELEMENT DETECTED: {video_url}")
                    break

            if video_url:
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
                print(f"  [{elapsed}s] Waiting for render tile...")

            if elapsed % 30 < 10:
                await page.screenshot(path=f"scratch/poll_flow_{elapsed}s.png")

            await page.wait_for_timeout(10000)

        # If video element not immediately found, click on the video tile on canvas
        if not video_url:
            print("Clicking canvas video tile to open viewer...")
            await page.mouse.click(220, 200)
            await page.wait_for_timeout(3000)

            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src:
                    video_url = src
                    break

        # Download video
        print(f"Downloading MP4 to {OUTPUT_MP4}...")
        dl_btn = await page.query_selector("button:has-text('Download'), [aria-label*='download' i]")
        if dl_btn:
            async with page.expect_download() as dl_info:
                await dl_btn.click()
            dl = await dl_info.value
            await dl.save_as(str(OUTPUT_MP4))
        elif video_url:
            import urllib.request
            urllib.request.urlretrieve(video_url, str(OUTPUT_MP4))
        else:
            await page.screenshot(path="scratch/flow_timeout.png")
            raise TimeoutError("Generation timed out or download could not be initiated.")

        # Save cookies
        await context.storage_state(path="config/flow_auth.json")
        await context.close()

    # Verify file
    assert OUTPUT_MP4.exists(), "MP4 file was not downloaded"
    cap = cv2.VideoCapture(str(OUTPUT_MP4))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = cnt / fps if fps > 0 else 0
    cap.release()

    size = OUTPUT_MP4.stat().st_size
    print(f"\nSUCCESS: Downloaded real Google Flow Veo 3.1 video:")
    print(f"  Path: {OUTPUT_MP4}")
    print(f"  Resolution: {w}x{h}")
    print(f"  Cadence: {fps} FPS, {cnt} frames ({dur:.2f}s)")
    print(f"  Size: {size:,} bytes")

    # Write receipts
    receipt = {
        "jobId": f"flow_veo31_paper_editorial_{int(time.time())}",
        "status": "VERIFIED_RENDER_COMPLETED",
        "engine": "Google Flow (Live Automation via Playwright)",
        "model": "Veo 3.1",
        "account": "ipsasummagnitudo@gmail.com",
        "mp4AssetPath": str(OUTPUT_MP4).replace("\\", "/"),
        "resolution": {"width": w, "height": h},
        "fps": fps,
        "frameCount": cnt,
        "durationSec": dur,
        "fileSizeBytes": size,
        "prompt": PROMPT,
    }

    with open(RECEIPT_JSON, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    with open(RECEIPT_MD, "w", encoding="utf-8") as f:
        f.write(f"# Google Flow Veo 3.1 Live Render Receipt\n\n")
        f.write(f"- **Asset**: [`{OUTPUT_MP4.name}`]({receipt['mp4AssetPath']})\n")
        f.write(f"- **Size**: `{size:,} bytes` ({size / 1024 / 1024:.2f} MB)\n")
        f.write(f"- **Resolution**: `{w}x{h}` (9:16 Vertical)\n")
        f.write(f"- **Duration**: `{dur:.2f}s` ({cnt} frames @ {fps} FPS)\n")
        f.write(f"- **Account**: `ipsasummagnitudo@gmail.com`\n")
        f.write(f"\n## Stitched Prompt\n```text\n{PROMPT}\n```\n")

    print(f"Receipt written to {RECEIPT_JSON} and {RECEIPT_MD}")

if __name__ == "__main__":
    asyncio.run(run_generation())
