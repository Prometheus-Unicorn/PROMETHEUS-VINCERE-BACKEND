import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_URL = "https://flow.google.com/project/36832888-b965-464f-be7c-5252a59910ad"

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--enable-webgl',
                '--ignore-gpu-blocklist',
                '--enable-gpu-rasterization',
                '--use-gl=angle',
                '--use-angle=d3d11',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        context = await browser.new_context(
            storage_state='config/flow_auth.json',
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        print(f"Connecting to {PROJECT_URL} ...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until='domcontentloaded')
        print("Waiting 12s for canvas hydration...")
        await page.wait_for_timeout(12000)
        
        # Check all clickable buttons at the bottom right
        btn_info = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button, [role="button"], mat-icon, span'));
            return btns.map(b => {
                const r = b.getBoundingClientRect();
                return {
                    tag: b.tagName,
                    text: (b.innerText || '').trim(),
                    aria: b.getAttribute('aria-label') || '',
                    x: Math.round(r.x),
                    y: Math.round(r.y),
                    w: Math.round(r.width),
                    h: Math.round(r.height),
                    visible: r.width > 0 && r.height > 0 && r.x > 1000 && r.y > 700
                };
            }).filter(b => b.visible);
        }''')
        
        print(f"Buttons in prompt dock ({len(btn_info)} found):")
        for b in btn_info:
            print(f"  pos=({b['x']}, {b['y']}) size=({b['w']}x{b['h']}) tag={b['tag']} text='{b['text']}' aria='{b['aria']}'")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
