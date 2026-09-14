import asyncio
import os
import time
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

async def inspect_and_click_approve():
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
        print("Waiting 15s for full chat history hydration...")
        await page.wait_for_timeout(15000)

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/flow_approve_hydrated.png")
        print("Saved screenshot: scratch/flow_approve_hydrated.png")

        # Find any elements containing 'Approve'
        approve_elements = await page.evaluate('''() => {
            const results = [];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const text = el.innerText || '';
                if (text.includes('Approve') && el.children.length <= 2) {
                    const r = el.getBoundingClientRect();
                    results.push({
                        tag: el.tagName,
                        text: text.trim(),
                        className: el.className,
                        x: r.x,
                        y: r.y,
                        w: r.width,
                        h: r.height,
                        visible: r.width > 0 && r.height > 0
                    });
                }
            }
            return results;
        }''')

        print(f"Found {len(approve_elements)} elements matching 'Approve':")
        target_click = None
        for el in approve_elements:
            print(f"  [{el['tag']}] text='{el['text']}', pos=({el['x']}, {el['y']}), visible={el['visible']}")
            if el['visible'] and "approve" in el['text'].lower() and el['h'] > 15:
                target_click = el

        if target_click:
            click_x = target_click['x'] + target_click['w'] / 2
            click_y = target_click['y'] + target_click['h'] / 2
            print(f"\nClicking Approve target at ({click_x}, {click_y})...")
            await page.mouse.click(click_x, click_y)
            print("Clicked! Waiting 5s...")
            await page.wait_for_timeout(5000)

            await page.screenshot(path="scratch/flow_post_approve_click.png")
            print("Saved screenshot: scratch/flow_post_approve_click.png")

            # Check for generation progress
            print("Monitoring for 30s...")
            for s in range(6):
                await page.wait_for_timeout(5000)
                await page.screenshot(path=f"scratch/flow_gen_progress_{(s+1)*5}s.png")
                print(f"Progress checkpoint ({(s+1)*5}s)...")
        else:
            print("No visible Approve target found.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_and_click_approve())
