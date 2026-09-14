import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--use-gl=angle",
                "--use-angle=d3d11",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            storage_state="config/flow_auth.json",
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        await page.goto("https://flow.google.com/about", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)
        btn = await page.query_selector("button:has-text('Create with Google Flow')")
        if btn:
            print("Found 'Create with Google Flow' button. Clicking...")
            await btn.click()
            await page.wait_for_timeout(6000)
            print("Current URL:", page.url)
            print("Page Title:", await page.title())
            await page.screenshot(path="scratch/after_click_create.png")
        else:
            print("No button found. URL:", page.url)
            await page.screenshot(path="scratch/no_button.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
