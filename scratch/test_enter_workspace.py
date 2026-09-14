import asyncio
import os
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"

async def click_create_with_flow():
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

        print("Navigating to https://flow.google.com/about ...")
        await page.goto("https://flow.google.com/about", timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        create_btn = await page.query_selector("button:has-text('Create with Google Flow')")
        if create_btn:
            print("Found 'Create with Google Flow' button. Clicking...")
            await create_btn.click()
            await page.wait_for_timeout(5000)

            print(f"URL after click: {page.url}")
            print(f"Title after click: {await page.title()}")

            os.makedirs("scratch", exist_ok=True)
            await page.screenshot(path="scratch/after_create_click.png")

            # Check if recent project link exists
            links = await page.query_selector_all("a[href*='project']")
            print(f"Found {len(links)} project links:")
            for l in links:
                href = await l.get_attribute("href")
                print(f"  Project link: {href}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(click_create_with_flow())
