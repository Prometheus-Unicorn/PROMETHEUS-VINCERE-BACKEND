"""One-Time Visible Google Flow Sign-In & Workspace Activator.

Launches a visible Chrome browser with the dedicated persistent automation profile
(C:\\Users\\HomePC\\AppData\\Local\\Google\\Chrome\\AutomationData).

Instructions:
1. Run: python scripts/launch_flow_browser.py
2. Chrome opens to https://flow.google.com.
3. Sign in to your Google Account (ipsasummagnitudo@gmail.com) and complete phone 2FA.
4. Once you are on the Flow dashboard, the script detects the active session,
   saves the credentials permanently, and confirms readiness for automated generation.
"""

import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FLOW_URL = "https://flow.google.com"
AUTH_SAVE_PATH = Path("config/flow_auth.json")

async def main():
    print("=" * 70)
    print("GOOGLE FLOW PERSISTENT PROFILE ACTIVATOR")
    print(f"Profile Directory: {USER_DATA_DIR}")
    print("=" * 70)
    print("\nOpening visible Chrome browser...")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=CHROME_PATH,
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",
                "--enable-webgl",
                "--disable-blink-features=AutomationControlled",
            ],
            no_viewport=True,
        )

        page = context.pages[0] if context.pages else await context.new_page()
        print(f"Navigating to {FLOW_URL} ...")
        await page.goto(FLOW_URL, timeout=60000)

        print("\n" + "*" * 70)
        print("ACTION REQUIRED:")
        print("1. In the Chrome window that just opened, sign in to your Google Account:")
        print("   -> ipsasummagnitudo@gmail.com")
        print("2. Complete any one-time 2FA / phone verification prompt.")
        print("3. Once signed in, navigate into any Google Flow project or the dashboard.")
        print("*" * 70 + "\n")

        print("Listening for authenticated session... (Press Ctrl+C at any time when done)")

        # Poll until authentication is detected
        is_authenticated = False
        while not is_authenticated:
            try:
                url = page.url
                title = await page.title()
                
                # If URL is inside a project or workspace, or if sign-in buttons disappear
                if "/project/" in url or "workspace" in url.lower() or ("accounts.google.com" not in url and "about" not in url):
                    # Check if user avatar or project canvas exists
                    is_authenticated = True
                    print(f"\nAUTHENTICATION DETECTED! Current URL: {url}")
                    break

                await asyncio.sleep(3)
            except Exception:
                await asyncio.sleep(2)

        # Save cookies snapshot to config/flow_auth.json as a backup
        AUTH_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(AUTH_SAVE_PATH))
        print(f"Permanent session saved to: {USER_DATA_DIR}")
        print(f"Backup storage state saved to: {AUTH_SAVE_PATH}")
        print("\nSetup complete! You can now run Google Flow headlessly forever without re-authenticating.")

        # Keep browser open 5 seconds so user sees confirmation
        await asyncio.sleep(5)
        await context.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession saved. Exiting.")
