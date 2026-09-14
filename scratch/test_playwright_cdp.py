import asyncio
from playwright.async_api import async_playwright

async def test_cdp():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected successfully!")
            print("Contexts:", len(browser.contexts))
            for ctx in browser.contexts:
                print("Pages:", len(ctx.pages))
                for page in ctx.pages:
                    print("Page:", page.url)
            await browser.close()
        except Exception as e:
            print("CDP Connect Failed:", type(e), e)

asyncio.run(test_cdp())
