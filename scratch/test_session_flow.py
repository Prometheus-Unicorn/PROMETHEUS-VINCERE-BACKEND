import asyncio
import sys
from pathlib import Path

sys.path.insert(0, ".")
from mini_run_pipeline.google_flow_session import GoogleFlowSessionManager, launch_persistent_flow_context

async def run_check():
    print("Testing launch_persistent_flow_context with config/flow_browser_profile...")
    profile_dir = Path("config/flow_browser_profile")
    mgr = GoogleFlowSessionManager(profile_dir=profile_dir)
    
    context = await launch_persistent_flow_context(profile_dir=profile_dir, headless=True)
    page = context.pages[0] if context.pages else await context.new_page()
    
    await page.goto("https://flow.google.com/about", timeout=30000, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    health = await mgr.verify_session_health(page)
    print(f"Session Health Result: {health}")
    
    cookies = await mgr.sync_context_cookies(context)
    print(f"Synced {len(cookies)} cookies to disk.")
    
    await context.close()

if __name__ == "__main__":
    asyncio.run(run_check())
