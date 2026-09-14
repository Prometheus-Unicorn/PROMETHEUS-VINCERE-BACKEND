import asyncio
from playwright.async_api import async_playwright

async def verify_workspace():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--enable-webgl', '--no-sandbox'])
        context = await browser.new_context(storage_state='config/flow_auth.json', viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        print('1. Navigating to https://flow.google.com ...')
        await page.goto('https://flow.google.com', timeout=45000, wait_until='domcontentloaded')
        await page.wait_for_timeout(4000)
        
        print('2. Locating "+ New project" button...')
        new_proj_btn = await page.query_selector('button:has-text("New project"), div:has-text("+ New project")')
        if not new_proj_btn:
            # Try finding any element containing "New project"
            new_proj_btn = await page.wait_for_selector('text="New project"', timeout=10000)
            
        if new_proj_btn:
            print('Found "+ New project" button! Clicking...')
            await new_proj_btn.click()
            await page.wait_for_timeout(8000)
            
            current_url = page.url
            print(f'Workspace URL: {current_url}')
            await page.screenshot(path='scratch/flow_new_workspace_ready.png')
            
            # Check prompt input
            input_box = await page.query_selector('textarea, [contenteditable="true"], input[placeholder*="prompt" i]')
            print('Prompt input box detected:', input_box is not None)
            print('GATEWAY STATUS: READY FOR PROMPT DISPATCH!')
        else:
            print('Could not find New project button')
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_workspace())
