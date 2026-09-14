import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path("config/flow_browser_profile").resolve()

async def click_next():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            viewport={'width': 1440, 'height': 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://flow.google.com", timeout=45000, wait_until='domcontentloaded')
        await page.wait_for_timeout(4000)
        
        print("Current URL:", page.url)
        if "confirmidentifier" in page.url or "signin" in page.url:
            print("Clicking 'Next' button...")
            next_btn = await page.query_selector("button:has-text('Next')")
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(5000)
                print("After clicking Next, URL:", page.url)
                await page.screenshot(path="scratch/flow_after_next.png")
                print("Screenshot saved to scratch/flow_after_next.png")
                
                # Check for password field or phone prompt
                body_text = await page.evaluate("() => document.body.innerText")
                print("Page Text Summary:")
                for line in body_text.split('\n')[:15]:
                    if line.strip():
                        print("  >", line.strip())
        await context.close()

if __name__ == "__main__":
    asyncio.run(click_next())
