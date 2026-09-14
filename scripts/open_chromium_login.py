import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path("config/flow_browser_profile").resolve()
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
AUTH_JSON = Path("config/flow_auth.json").resolve()

async def main():
    print("=" * 60)
    print("OPENING DEDICATED CHROMIUM WINDOW FOR GOOGLE FLOW SIGN-IN")
    print(f"Profile: {PROFILE_DIR}")
    print("=" * 60)
    sys.stdout.flush()

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
            no_viewport=True,
        )

        page = context.pages[0] if context.pages else await context.new_page()
        print("Navigating directly to https://flow.google.com ...")
        sys.stdout.flush()
        
        await page.goto("https://flow.google.com", timeout=60000)
        print("\n>>> CHROMIUM WINDOW IS NOW OPEN ON YOUR SCREEN. <<<")
        print("Please log in with ipsasummagnitudo@gmail.com and approve 2FA.")
        print("Once you are inside Google Flow, your session will be locked and saved automatically.")
        sys.stdout.flush()

        # Monitor login state
        saved = False
        while len(context.pages) > 0 and not page.is_closed():
            try:
                current_url = page.url
                # When user enters project or main tool workspace
                if ("/project/" in current_url or ("accounts.google.com" not in current_url and "about" not in current_url and "signin" not in current_url)):
                    if not saved:
                        await context.storage_state(path=str(AUTH_JSON))
                        print(f"\n[SUCCESS] Active session detected and permanently saved to {AUTH_JSON}!")
                        print(f"Current Workspace URL: {current_url}")
                        sys.stdout.flush()
                        saved = True
            except Exception:
                pass
            await asyncio.sleep(2)

        print("\nBrowser closed. Session state saved.")

if __name__ == "__main__":
    asyncio.run(main())
