import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            'config/flow_browser_profile',
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--use-gl=angle",
                "--use-angle=d3d11",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
            viewport={"width": 1440, "height": 900}
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto('https://flow.google.com/project/0431f510-bbad-4c90-8157-f1723008eea3')
        await page.wait_for_timeout(6000)

        # Click the Always approve option
        print("Clicking '[role=\"radio\"]:has-text(\"Always approve\")'...")
        opt = await page.query_selector('[role="radio"]:has-text("Always approve"), .option-row:has-text("Always approve")')
        if opt:
            print("Found option! Clicking it...")
            await opt.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="scratch/after_clicking_always_approve.png")
            print("Screenshot saved to scratch/after_clicking_always_approve.png")
        else:
            print("Option not found!")

        await ctx.close()

if __name__ == "__main__":
    asyncio.run(check())
