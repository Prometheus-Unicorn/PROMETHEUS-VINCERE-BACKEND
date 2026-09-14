import asyncio
import sys
from pathlib import Path

sys.path.insert(0, ".")
from mini_run_pipeline.google_flow_session import launch_persistent_flow_context

async def inspect():
    profile_dir = Path(r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData")
    context = await launch_persistent_flow_context(profile_dir=profile_dir, headless=True)
    page = context.pages[0] if context.pages else await context.new_page()
    
    print("Navigating to https://flow.google.com/ ...")
    await page.goto("https://flow.google.com/", timeout=45000, wait_until="domcontentloaded")
    print("Waiting 10 seconds for webgl and dynamic components to render...")
    await page.wait_for_timeout(10000)
    
    print(f"Final URL: {page.url}")
    print(f"Page Title: {await page.title()}")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print(f"Body Text Preview (first 500 chars):\n{body_text[:500]}")
    
    await page.screenshot(path="scratch/flow_dom_check.png")
    print("Screenshot saved to scratch/flow_dom_check.png")
    
    # Check buttons
    buttons = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('button, a, div[role="button"]')).map(b => (b.innerText || b.getAttribute('aria-label') || '').trim()).filter(Boolean);
    }''')
    print("Interactive Elements found:", buttons[:20])
    
    await context.close()

if __name__ == "__main__":
    asyncio.run(inspect())
