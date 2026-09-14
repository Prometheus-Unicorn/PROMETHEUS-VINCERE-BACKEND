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

def mirror_profile12():
    print("Stopping any chrome...")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(2)

    os.makedirs(DST_USER_DATA, exist_ok=True)

    # Copy Local State
    shutil.copy2(os.path.join(SRC_USER_DATA, "Local State"), os.path.join(DST_USER_DATA, "Local State"))
    print("Copied Local State.")

    # Copy Profile 12 exactly into Profile 12
    dst_p12 = os.path.join(DST_USER_DATA, "Profile 12")
    if os.path.exists(dst_p12):
        shutil.rmtree(dst_p12, ignore_errors=True)
    
    src_p12 = os.path.join(SRC_USER_DATA, "Profile 12")
    print(f"Copying {src_p12} -> {dst_p12} ...")
    shutil.copytree(
        src_p12,
        dst_p12,
        ignore=shutil.ignore_patterns("Cache*", "Code Cache*", "GPUCache*", "*.tmp")
    )
    print("Profile 12 copy complete!")

async def test_flow():
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
            print("Connecting Playwright over CDP to port 9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected! Contexts:", len(browser.contexts))
            ctx = browser.contexts[0]
            page = await ctx.new_page()

            print("Navigating to https://labs.google/fx/tools/flow ...")
            await page.goto("https://labs.google/fx/tools/flow", timeout=45000, wait_until="domcontentloaded")
            await page.wait_for_timeout(6000)

            title = await page.title()
            url = page.url
            print(f"Result URL: {url}")
            print(f"Result Title: {title}")

            # Take screenshot to see UI
            os.makedirs("scratch", exist_ok=True)
            ss_path = "scratch/flow_exact_mirror_state.png"
            await page.screenshot(path=ss_path)
            print(f"Saved screenshot: {ss_path}")

            # Inspect elements
            content = await page.content()
            if "ipsasummagnitudo" in content:
                print(">>> SUCCESS: ipsasummagnitudo is verified in the page!")
            
            # Look for prompt box
            textareas = await page.query_selector_all("textarea, div[contenteditable='true']")
            print(f"Found {len(textareas)} text inputs/textareas on page.")
            for i, ta in enumerate(textareas):
                ph = await ta.get_attribute("placeholder") or ""
                al = await ta.get_attribute("aria-label") or ""
                print(f"  Input #{i+1}: placeholder='{ph}', aria-label='{al}'")

            buttons = await page.query_selector_all("button")
            print(f"Found {len(buttons)} buttons on page.")
            btn_texts = [await b.inner_text() for b in buttons[:15]]
            print(f"  Sample buttons: {btn_texts}")

            await browser.close()
    finally:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)

if __name__ == "__main__":
    mirror_profile12()
    asyncio.run(test_flow())
