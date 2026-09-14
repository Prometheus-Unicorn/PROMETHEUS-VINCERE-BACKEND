import asyncio
import os
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

async def test_webgl_flags():
    async with async_playwright() as p:
        # Launch Chromium with full WebGL & GPU support
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

        # Listen to console messages to see any React or WebGL errors
        page.on("console", lambda msg: print(f"[Browser Console {msg.type}] {msg.text[:120]}"))
        page.on("pageerror", lambda err: print(f"[Page Error] {err}"))

        print(f"Navigating to {PROJECT_URL} ...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="networkidle")
        await page.wait_for_timeout(5000)

        os.makedirs("scratch", exist_ok=True)
        ss_path = "scratch/flow_workspace_webgl.png"
        await page.screenshot(path=ss_path)
        print(f"Saved screenshot to {ss_path}")

        # Check DOM elements
        content = await page.content()
        print(f"Page HTML length: {len(content)}")

        # Find buttons, textareas, canvases
        canvases = await page.query_selector_all("canvas")
        print(f"Found {len(canvases)} canvas elements.")

        inputs = await page.query_selector_all("textarea, input, [contenteditable='true']")
        print(f"Found {len(inputs)} text inputs.")
        for i, el in enumerate(inputs):
            ph = await el.get_attribute("placeholder") or ""
            al = await el.get_attribute("aria-label") or ""
            print(f"  Input #{i+1}: ph='{ph}', aria='{al}'")

        buttons = await page.query_selector_all("button, [role='button']")
        print(f"Found {len(buttons)} buttons.")
        for i, b in enumerate(buttons[:15]):
            txt = (await b.inner_text()).strip().replace("\n", " ")
            al = await b.get_attribute("aria-label") or ""
            if txt or al:
                print(f"  Btn #{i+1}: text='{txt[:40]}', aria='{al}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_webgl_flags())
