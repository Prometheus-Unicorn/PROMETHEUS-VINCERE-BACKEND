import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--enable-webgl', '--no-sandbox'])
        context = await browser.new_context(storage_state='config/flow_auth.json', viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        await page.goto('https://flow.google.com', timeout=45000, wait_until='domcontentloaded')
        await page.wait_for_timeout(5000)
        
        # Check all text elements with @ to find email
        emails = await page.evaluate('''() => {
            const matches = [];
            document.querySelectorAll('*').forEach(el => {
                const text = el.innerText || '';
                const aria = el.getAttribute('aria-label') || '';
                const title = el.getAttribute('title') || '';
                [text, aria, title].forEach(t => {
                    if (t.includes('@') && t.includes('.')) {
                        matches.push(t.trim());
                    }
                });
            });
            return Array.from(new Set(matches));
        }''')
        
        print("Emails detected on page:", emails)
        
        # Also check profile avatar tooltip
        avatar_info = await page.evaluate('''() => {
            const btn = document.querySelector('button:has-text("E"), [aria-label*="@"], [aria-label*="Account"]');
            return btn ? { text: btn.innerText, aria: btn.getAttribute('aria-label') } : null;
        }''')
        print("Avatar info:", avatar_info)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())
