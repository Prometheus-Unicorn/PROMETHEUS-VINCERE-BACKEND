import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
FLOW_URL = "https://flow.google.com"

async def test_session():
    print(f"Loading session from {AUTH_PATH}...")
    async with async_playwright() as p:
        # Launch headless Chromium
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        context = await browser.new_context(
            storage_state=AUTH_PATH,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        )
        
        page = await context.new_page()
        
        print(f"Navigating to {FLOW_URL} ...")
        await page.goto(FLOW_URL, timeout=45000, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)
        
        current_url = page.url
        title = await page.title()
        print(f"Page loaded!")
        print(f"Current URL: {current_url}")
        print(f"Page Title: {title}")
        
        # Save screenshot
        os.makedirs("scratch", exist_ok=True)
        ss_path = "scratch/flow_cookie_session_state.png"
        try:
            await page.screenshot(path=ss_path, timeout=10000)
            print(f"Screenshot saved to {ss_path}")
        except Exception as e:
            print(f"Screenshot warning: {e}")

        # Check if we are signed in or redirected to login
        if "accounts.google.com" in current_url:
            print("Status: REDIRECTED_TO_SIGNIN (Cookies rejected or missing additional domain binding)")
        elif "flow.google.com/about" in current_url:
            print("Status: LANDING_PAGE (Checking if there is an active session or Create button)")
            # Look for Create button
            create_btn = await page.query_selector("button:has-text('Create with Google Flow')")
            if create_btn:
                print("Found 'Create with Google Flow' button. Clicking...")
                await create_btn.click()
                await page.wait_for_timeout(5000)
                print(f"After click URL: {page.url}")
                print(f"After click Title: {await page.title()}")
        else:
            print("Status: AUTHENTICATED_WORKSPACE!")
            
        # Inspect all interactive elements
        buttons = await page.query_selector_all("button")
        btn_texts = [(await b.inner_text()).strip() for b in buttons if (await b.inner_text()).strip()]
        print(f"Visible buttons ({len(btn_texts)}): {btn_texts[:10]}")

        textareas = await page.query_selector_all("textarea, input, div[contenteditable='true']")
        print(f"Visible inputs/textareas: {len(textareas)}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_session())
