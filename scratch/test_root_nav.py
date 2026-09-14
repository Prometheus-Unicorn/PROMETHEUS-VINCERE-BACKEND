import asyncio
import os
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"

async def test_nav():
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

        print("1. Navigating to root: https://flow.google.com/ ...")
        await page.goto("https://flow.google.com/", timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        print(f"Root URL: {page.url}, title: {await page.title()}")

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/check_root_nav.png")

        # Now click into the recent project
        recent_proj = await page.query_selector("div:has-text('Sep 13 - 21:32'), div:has-text('Untitled session'), [aria-label*='project' i]")
        print("Recent project tile:", recent_proj)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_nav())
