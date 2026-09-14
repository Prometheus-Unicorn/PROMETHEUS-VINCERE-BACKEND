import asyncio
from playwright.async_api import async_playwright

PROJECT_URL = "https://flow.google.com/project/36832888-b965-464f-be7c-5252a59910ad"

async def test_canvas():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--enable-webgl',
                '--ignore-gpu-blocklist',
                '--enable-gpu-rasterization',
                '--use-gl=angle',
                '--use-angle=d3d11',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        context = await browser.new_context(
            storage_state='config/flow_auth.json',
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        print(f"Navigating to {PROJECT_URL}...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until='domcontentloaded')
        print("Waiting 15s for full canvas hydration...")
        await page.wait_for_timeout(15000)
        
        await page.screenshot(path="scratch/flow_canvas_hydrated.png")
        print("Screenshot saved to scratch/flow_canvas_hydrated.png")
        
        # Check input elements
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input, textarea, [contenteditable="true"]')).map((el, idx) => {
                const r = el.getBoundingClientRect();
                return {
                    idx,
                    tag: el.tagName,
                    placeholder: el.getAttribute('placeholder') || '',
                    aria: el.getAttribute('aria-label') || '',
                    x: r.x,
                    y: r.y,
                    width: r.width,
                    height: r.height,
                    visible: r.width > 0 && r.height > 0
                };
            });
        }''')
        
        print(f"Found {len(inputs)} input fields:")
        for inp in inputs:
            print(f"  #{inp['idx']}: tag={inp['tag']} ph='{inp['placeholder']}' aria='{inp['aria']}' pos=({inp['x']}, {inp['y']}) visible={inp['visible']}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_canvas())
