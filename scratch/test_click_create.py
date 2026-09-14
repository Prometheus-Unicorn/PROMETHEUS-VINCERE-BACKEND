import os
import subprocess
import time
import asyncio
from playwright.async_api import async_playwright

DST_USER_DATA = r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def click_create():
    cmd = [
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={DST_USER_DATA}",
        "--profile-directory=Profile 12",
        "--remote-allow-origins=*",
        "--headless=new",
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(3)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            ctx = browser.contexts[0]
            page = await ctx.new_page()

            print("Navigating to https://flow.google.com/about ...")
            await page.goto("https://flow.google.com/about", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            print("Looking for 'Create with Google Flow' button...")
            btn = await page.wait_for_selector("button:has-text('Create with Google Flow')", timeout=10000)
            if btn:
                print("Clicking 'Create with Google Flow'...")
                await btn.click()
                await page.wait_for_timeout(6000)

                print(f"Post-click URL: {page.url}")
                print(f"Post-click Title: {await page.title()}")

                # Check for sign-in vs app interface
                if "accounts.google.com" in page.url:
                    print("Google redirected to Accounts Sign-in.")
                else:
                    print("App opened! Checking inputs...")
                    tas = await page.query_selector_all("textarea, input, [contenteditable='true']")
                    print(f"Found {len(tas)} input elements.")

            await browser.close()
    finally:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)

if __name__ == "__main__":
    asyncio.run(click_create())
