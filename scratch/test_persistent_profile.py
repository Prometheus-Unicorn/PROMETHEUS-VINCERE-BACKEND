import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path("config/flow_browser_profile").resolve()

async def test_profile():
    async with async_playwright() as p:
        print(f"Launching persistent context with profile: {PROFILE_DIR}...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=[
                '--enable-webgl',
                '--ignore-gpu-blocklist',
                '--enable-gpu-rasterization',
                '--use-gl=angle',
                '--use-angle=d3d11',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ],
            viewport={'width': 1440, 'height': 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        print("Navigating to https://flow.google.com ...")
        await page.goto("https://flow.google.com", timeout=45000, wait_until='domcontentloaded')
        await page.wait_for_timeout(6000)
        
        print(f"Page URL: {page.url}")
        print(f"Page Title: {await page.title()}")
        await page.screenshot(path="scratch/flow_persistent_state.png")
        print("Saved scratch/flow_persistent_state.png")
        
        # Also check if logged in
        cookies = await context.cookies()
        print(f"Total cookies in context: {len(cookies)}")
        for c in cookies:
            if 'PSIDTS' in c['name']:
                print(f"Cookie {c['name']}: domain={c['domain']} expires={c['expires']}")
                
        # Save refreshed storage_state to flow_auth.json
        await context.storage_state(path="config/flow_auth.json")
        print("Refreshed storage_state saved to config/flow_auth.json!")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(test_profile())
