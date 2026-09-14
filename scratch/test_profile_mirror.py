import os
import shutil
import subprocess
import time
import urllib.request
import json
import asyncio
from playwright.async_api import async_playwright

SRC_USER_DATA = r"C:\Users\HomePC\AppData\Local\Google\Chrome\User Data"
DST_USER_DATA = r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def setup_automation_profile():
    os.makedirs(DST_USER_DATA, exist_ok=True)
    
    # 1. Copy Local State (contains DPAPI encryption key)
    src_local_state = os.path.join(SRC_USER_DATA, "Local State")
    dst_local_state = os.path.join(DST_USER_DATA, "Local State")
    if os.path.exists(src_local_state):
        shutil.copy2(src_local_state, dst_local_state)
        print("Copied Local State.")

    # 2. Copy Profile 12 to 'Default' in AutomationData
    src_p12 = os.path.join(SRC_USER_DATA, "Profile 12")
    dst_default = os.path.join(DST_USER_DATA, "Default")
    
    if os.path.exists(dst_default):
        shutil.rmtree(dst_default, ignore_errors=True)
    
    print("Copying Profile 12 to AutomationData/Default...")
    shutil.copytree(
        src_p12,
        dst_default,
        ignore=shutil.ignore_patterns("Cache*", "Code Cache*", "GPUCache*", "*.tmp")
    )
    print("Profile 12 successfully mirrored!")

async def inspect_google_session():
    cmd = [
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={DST_USER_DATA}",
        "--headless=new",
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(3)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = await context.new_page()

            print("Navigating to https://accounts.google.com ...")
            await page.goto("https://accounts.google.com", timeout=30000)
            await page.wait_for_timeout(3000)

            title = await page.title()
            url = page.url
            print(f"Loaded page: title='{title}', url='{url}'")

            # Check for account email in page content
            content = await page.content()
            if "ipsasummagnitudo@gmail.com" in content:
                print("FOUND ACCOUNT: ipsasummagnitudo@gmail.com is present in session!")
            elif "Sign in" in title or "accounts.google.com/v3/signin" in url:
                print("Google requested sign-in (session cookies may require full session/device bind).")
            else:
                print("Session loaded without sign-in prompt!")

            # Check Google Flow page
            print("Navigating to https://labs.google/fx/tools/flow ...")
            await page.goto("https://labs.google/fx/tools/flow", timeout=30000)
            await page.wait_for_timeout(5000)
            flow_title = await page.title()
            flow_url = page.url
            print(f"Flow page: title='{flow_title}', url='{flow_url}'")
            
            # Take a screenshot to inspect the exact UI state
            os.makedirs("scratch", exist_ok=True)
            await page.screenshot(path="scratch/flow_page_state.png")
            print("Saved screenshot to scratch/flow_page_state.png")

            await browser.close()
    finally:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)

if __name__ == "__main__":
    setup_automation_profile()
    asyncio.run(inspect_google_session())
