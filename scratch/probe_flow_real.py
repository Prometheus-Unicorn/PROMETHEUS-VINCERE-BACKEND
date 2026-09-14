import asyncio
import os
import sys
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

async def main():
    print("Launching Chromium...")
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
        print(f"Navigating to {PROJECT_URL}...")
        try:
            await page.goto(PROJECT_URL, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(6000)
            print(f"Current URL: {page.url}")
            print(f"Page Title: {await page.title()}")
            os.makedirs("scratch", exist_ok=True)
            await page.screenshot(path="scratch/flow_probe_state.png")
            print("Saved scratch/flow_probe_state.png")
        except Exception as e:
            print(f"ERROR: {e}")
            await page.screenshot(path="scratch/flow_probe_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
