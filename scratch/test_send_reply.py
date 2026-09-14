import asyncio
import os
import time
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

async def test_reply():
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

        # 1. Click directly at the input field coordinates (1100, 900)
        print("Clicking into prompt field at (1100, 900)...")
        await page.mouse.click(1100, 900)
        await page.wait_for_timeout(500)

        # Also find any contenteditable or textarea
        inputs = await page.query_selector_all('[contenteditable="true"], textarea, input')
        for el in inputs:
            r = await el.bounding_box()
            if r and r['x'] > 800 and r['y'] > 750:
                print(f"Found input element at ({r['x']}, {r['y']}). Focusing...")
                await el.click()
                break

        print("Typing message...")
        reply_msg = "Use an 8-second duration with Veo 3.1 - Lite instead."
        await page.keyboard.type(reply_msg, delay=10)
        await page.wait_for_timeout(1000)

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/flow_reply_typed.png")
        print("Saved screenshot: scratch/flow_reply_typed.png")

        # Check send button (round button on bottom right)
        print("Clicking send button or pressing Enter...")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)

        # Also click at (1395, 945) where the send button is
        await page.mouse.click(1395, 945)
        await page.wait_for_timeout(3000)

        await page.screenshot(path="scratch/flow_reply_sent.png")
        print("Saved screenshot: scratch/flow_reply_sent.png")

        # Monitor for 30s to see generation kickoff
        for s in range(6):
            await page.wait_for_timeout(5000)
            print(f"Polling ({(s+1)*5}s)...")
            await page.screenshot(path=f"scratch/flow_reply_step_{(s+1)*5}s.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_reply())
