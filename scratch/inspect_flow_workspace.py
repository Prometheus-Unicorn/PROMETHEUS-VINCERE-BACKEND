import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

WORKSPACE_URL = "https://flow.google.com/project/0431f510-bbad-4c90-8157-f1723008eea3"
USER_DATA_DIR = Path("config/flow_browser_profile").resolve()

async def inspect():
    print(f"Inspecting workspace: {WORKSPACE_URL}")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--use-gl=angle",
                "--use-angle=d3d11",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        )
        page = context.pages[0] if context.pages else await context.new_page()

        print(f"Navigating to {WORKSPACE_URL} ...")
        await page.goto(WORKSPACE_URL, timeout=60000, wait_until="domcontentloaded")
        print("Waiting 10s for workspace to load...")
        await page.wait_for_timeout(10000)

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/workspace_current_state.png")
        print("Saved screenshot: scratch/workspace_current_state.png")

        # Inspect all buttons and their texts
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button, [role="button"]')).map(b => ({
                text: b.innerText ? b.innerText.trim() : '',
                aria: b.getAttribute('aria-label') || '',
                visible: b.offsetWidth > 0 && b.offsetHeight > 0
            })).filter(b => b.visible && (b.text || b.aria));
        }''')
        print("\nVisible Buttons in Workspace:")
        for b in buttons[:25]:
            print(f"  btn: text='{b['text']}' | aria='{b['aria']}'")

        # Check for dialogs or modals
        dialogs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('[role="dialog"], mat-dialog-container, .modal, .dialog')).map(d => ({
                text: d.innerText ? d.innerText.slice(0, 200).replace(/\\n+/g, ' ') : ''
            }));
        }''')
        print(f"\nDialogs found: {len(dialogs)}")
        for d in dialogs:
            print(f"  dialog: {d['text']}")

        # Check video elements
        videos = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('video')).map(v => ({
                src: v.getAttribute('src') || '',
                currentSrc: v.currentSrc || '',
                duration: v.duration,
                paused: v.paused
            }));
        }''')
        print(f"\nVideos found: {len(videos)}")
        for v in videos:
            print(f"  video: src='{v['src']}' currentSrc='{v['currentSrc']}' duration={v['duration']}")

        # Check for card elements or generated tiles on canvas
        tiles = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('[data-node-id], .flow-card, .canvas-card, [role="article"]')).map(c => ({
                text: c.innerText ? c.innerText.slice(0, 100).replace(/\\n+/g, ' ') : ''
            }));
        }''')
        print(f"\nCanvas tiles/nodes found: {len(tiles)}")
        for t in tiles[:10]:
            print(f"  tile: {t['text']}")

        # Look for download or video links
        links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href*="video"], a[href*=".mp4"], a[download]')).map(a => ({
                href: a.href,
                download: a.getAttribute('download')
            }));
        }''')
        print(f"\nVideo/download links found: {len(links)}")
        for l in links:
            print(f"  link: href='{l['href']}' download='{l['download']}'")

        await context.close()

if __name__ == "__main__":
    asyncio.run(inspect())
