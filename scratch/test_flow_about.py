import os
import subprocess
import time
import asyncio
from playwright.async_api import async_playwright

DST_USER_DATA = r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def inspect_flow_about():
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
            await page.wait_for_timeout(4000)

            print(f"URL: {page.url}")
            print(f"Title: {await page.title()}")

            # Find all links and buttons
            links = await page.query_selector_all("a[href]")
            print(f"Found {len(links)} links:")
            for a in links:
                href = await a.get_attribute("href")
                text = (await a.inner_text()).strip()
                if any(w in (text + href).lower() for w in ["sign", "launch", "flow", "start", "try", "app", "fx"]):
                    print(f"  Link: text='{text}', href='{href}'")

            buttons = await page.query_selector_all("button")
            print(f"\nFound {len(buttons)} buttons:")
            for b in buttons:
                text = (await b.inner_text()).strip()
                if text:
                    print(f"  Button: '{text}'")

            await browser.close()
    finally:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)

if __name__ == "__main__":
    asyncio.run(inspect_flow_about())
