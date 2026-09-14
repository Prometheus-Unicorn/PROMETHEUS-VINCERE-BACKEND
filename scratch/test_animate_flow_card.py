import asyncio
import os
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

async def inspect_card_actions():
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

        print(f"Navigating to {PROJECT_URL} ...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # Hover over the media card on the left
        print("Looking for media card...")
        images = await page.query_selector_all("img")
        print(f"Found {len(images)} images on page:")
        for i, img in enumerate(images):
            src = await img.get_attribute("src") or ""
            al = await img.get_attribute("alt") or ""
            rect = await img.bounding_box()
            print(f"  Img #{i+1}: alt='{al}', src='{src[:60]}...', rect={rect}")

        # Hover over the main canvas card (rect around x=200, y=200)
        for img in images:
            rect = await img.bounding_box()
            if rect and rect['x'] < 400 and rect['width'] > 100:
                print("Hovering over canvas image card...")
                await img.hover()
                await page.wait_for_timeout(1500)
                os.makedirs("scratch", exist_ok=True)
                await page.screenshot(path="scratch/flow_card_hover.png")
                print("Saved screenshot: scratch/flow_card_hover.png")
                break

        # Also let's ask the chat: "Animate this into a 6-second video"
        print("Sending prompt: 'Animate this into a 6-second video'...")
        inputs = await page.query_selector_all('input, textarea, [contenteditable="true"]')
        target_el = None
        for el in inputs:
            rect = await el.bounding_box()
            if rect and rect['x'] > 800 and rect['y'] > 600:
                target_el = el
                break

        if target_el:
            await target_el.click()
            await page.keyboard.type("Animate this image into a 6-second cinematic video with Veo, showing the radial compass needles rotating smoothly and the Porsche accelerating forward", delay=5)
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
                print("Clicked send for video animation!")

            # Poll for video generation
            print("Monitoring for video generation (polling up to 60s)...")
            for i in range(12):
                await page.wait_for_timeout(5000)
                elapsed = (i + 1) * 5
                print(f"Elapsed: {elapsed}s...")
                await page.screenshot(path=f"scratch/flow_anim_sec_{elapsed}.png")
                
                # Check for video
                videos = await page.query_selector_all("video")
                if videos:
                    for v in videos:
                        vsrc = await v.get_attribute("src") or ""
                        print(f">>> FOUND VIDEO ELEMENT at {elapsed}s: {vsrc}")
                    break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_card_actions())
