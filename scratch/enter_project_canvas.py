import asyncio
from playwright.async_api import async_playwright

async def enter_tile():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--enable-webgl', '--no-sandbox'])
        context = await browser.new_context(storage_state='config/flow_auth.json', viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        await page.goto('https://flow.google.com', timeout=45000, wait_until='domcontentloaded')
        await page.wait_for_timeout(4000)
        
        # In screenshot, the leftmost card is at x ~ 180, y ~ 750
        print("Clicking project card...")
        await page.mouse.click(180, 750)
        await page.wait_for_timeout(8000)
        
        print("Workspace URL:", page.url)
        await page.screenshot(path="scratch/flow_project_canvas_live.png")
        
        inputs = await page.query_selector_all('input, textarea, [contenteditable="true"]')
        print(f"Detected {len(inputs)} inputs in canvas workspace!")
        for i, inp in enumerate(inputs):
            ph = await inp.get_attribute('placeholder') or ''
            tag = await inp.evaluate('e => e.tagName')
            print(f"  Input #{i}: tag={tag}, placeholder='{ph}'")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(enter_tile())
