import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path("config/flow_browser_profile").resolve()

async def complete_verify():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            viewport={'width': 1440, 'height': 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        print("Navigating to https://flow.google.com ...")
        await page.goto("https://flow.google.com", timeout=45000)
        await page.wait_for_timeout(4000)
        
        print("Clicking 'Create with Google Flow'...")
        create_btn = await page.query_selector("button:has-text('Create with Google Flow')")
        if create_btn:
            await create_btn.click()
            await page.wait_for_timeout(6000)
            
        print("Current URL:", page.url)
        await page.screenshot(path="scratch/verify_step1.png")
        
        # Check if Next button is present on Verify it's you
        next_btn = await page.query_selector("button:has-text('Next')")
        if next_btn:
            print("Found Next button! Clicking Next...")
            await next_btn.click()
            await page.wait_for_timeout(6000)
            print("URL after Next:", page.url)
            await page.screenshot(path="scratch/verify_step2.png")
            
            body = await page.evaluate("() => document.body.innerText")
            print("Screen text after Next:")
            for l in body.split('\n')[:15]:
                if l.strip():
                    print("  >", l.strip())
        else:
            print("Next button not found.")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(complete_verify())
