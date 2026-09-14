import asyncio
import os
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
FLOW_URL = "https://flow.google.com"

async def click_new_project():
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

        print("Navigating to https://flow.google.com ...")
        await page.goto(FLOW_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        print("Looking for '+ New project' button...")
        # Try multiple selectors for New project button
        new_proj_btn = await page.wait_for_selector(
            "button:has-text('New project'), [aria-label*='New project' i], div:has-text('New project')",
            timeout=10000
        )
        
        if new_proj_btn:
            print("Clicking '+ New project'...")
            await new_proj_btn.click()
            await page.wait_for_timeout(6000)

            print(f"Post-click URL: {page.url}")
            print(f"Post-click Title: {await page.title()}")

            os.makedirs("scratch", exist_ok=True)
            ss_path = "scratch/flow_new_project_workspace.png"
            await page.screenshot(path=ss_path)
            print(f"Saved workspace screenshot to {ss_path}")

            # Inspect all interactive elements in the workspace
            textareas = await page.query_selector_all("textarea, input, [contenteditable='true']")
            print(f"Found {len(textareas)} text inputs:")
            for i, ta in enumerate(textareas):
                tag = await ta.evaluate("el => el.tagName")
                ph = await ta.get_attribute("placeholder") or ""
                al = await ta.get_attribute("aria-label") or ""
                cl = await ta.get_attribute("class") or ""
                print(f"  Input #{i+1} [{tag}]: placeholder='{ph}', aria-label='{al}', class='{cl[:40]}'")

            buttons = await page.query_selector_all("button")
            print(f"\nFound {len(buttons)} buttons:")
            for b in buttons:
                txt = (await b.inner_text()).strip()
                al = await b.get_attribute("aria-label") or ""
                if txt or al:
                    print(f"  Button: text='{txt}', aria-label='{al}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(click_new_project())
