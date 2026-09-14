import asyncio
import os
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

async def inspect_loaded_workspace():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            storage_state=AUTH_PATH,
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        print(f"Navigating directly to project: {PROJECT_URL} ...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        
        # Wait up to 20 seconds for Loading... to disappear
        print("Waiting for workspace to finish loading...")
        for sec in range(20):
            await page.wait_for_timeout(1000)
            content = await page.content()
            if "Loading..." not in content:
                print(f"Workspace loaded at sec {sec+1}!")
                break
            print(f"Still loading ({sec+1}/20)...")

        await page.wait_for_timeout(3000)

        os.makedirs("scratch", exist_ok=True)
        ss_path = "scratch/flow_workspace_ready.png"
        await page.screenshot(path=ss_path)
        print(f"Saved workspace screenshot to {ss_path}")

        # Find all inputs, buttons, and editable elements
        inputs = await page.query_selector_all("textarea, input, [contenteditable='true']")
        print(f"\nFound {len(inputs)} input elements:")
        for i, el in enumerate(inputs):
            tag = await el.evaluate("e => e.tagName")
            ph = await el.get_attribute("placeholder") or ""
            al = await el.get_attribute("aria-label") or ""
            txt = (await el.inner_text()).strip()[:40]
            print(f"  #{i+1} [{tag}]: placeholder='{ph}', aria-label='{al}', text='{txt}'")

        buttons = await page.query_selector_all("button, [role='button']")
        print(f"\nFound {len(buttons)} buttons:")
        for i, b in enumerate(buttons):
            txt = (await b.inner_text()).strip().replace("\n", " ")
            al = await b.get_attribute("aria-label") or ""
            if txt or al:
                print(f"  #{i+1}: text='{txt[:50]}', aria-label='{al}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_loaded_workspace())
