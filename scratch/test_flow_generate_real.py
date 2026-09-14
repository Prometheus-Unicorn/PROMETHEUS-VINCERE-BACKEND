import asyncio
import os
import time
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

PROMPT = (
    "Top-down orthographic zenith perspective of sculpted white Porsche 911 GT3 RS "
    "with carbon fiber dual hood vents and massive rear wing, flanked by radial clock hands and precision compass needles, "
    "Dramatic chiaroscuro contrast with intense warm 3200K tungsten spotlight, "
    "volumetric shafts of light cutting through dusty studio air, "
    "Vertical 9:16 composition, 35mm anamorphic lens, shallow depth of field, "
    "high-agency luxury automotive editorial motion design, 24fps"
)

async def test_generate():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--enable-gpu-rasterization",
                "--use-gl=angle",
                "--use-angle=d3d11",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            storage_state=AUTH_PATH,
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        print(f"Navigating to {PROJECT_URL} ...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until="domcontentloaded")
        print("DOM loaded. Waiting 8s for React app hydration...")
        await page.wait_for_timeout(8000)

        # Query all elements with placeholder or contenteditable
        input_info = await page.evaluate('''() => {
            const results = [];
            document.querySelectorAll('input, textarea, [contenteditable="true"]').forEach((el, idx) => {
                const rect = el.getBoundingClientRect();
                results.push({
                    idx: idx,
                    tag: el.tagName,
                    placeholder: el.getAttribute('placeholder') || '',
                    ariaLabel: el.getAttribute('aria-label') || '',
                    className: el.className,
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    visible: rect.width > 0 && rect.height > 0
                });
            });
            return results;
        }''')

        print(f"Found {len(input_info)} input elements via DOM query:")
        target_idx = None
        for info in input_info:
            print(f"  Input #{info['idx']}: tag={info['tag']}, ph='{info['placeholder']}', aria='{info['ariaLabel']}', pos=({info['x']}, {info['y']}), visible={info['visible']}")
            if "create" in info['placeholder'].lower() or (info['x'] > 800 and info['y'] > 600 and info['visible']):
                target_idx = info['idx']
                print(f"    >>> SELECTED TARGET INPUT: #{target_idx}")

        if target_idx is not None:
            # Click and type into the selected input
            print(f"Clicking input #{target_idx}...")
            inputs = await page.query_selector_all('input, textarea, [contenteditable="true"]')
            target_el = inputs[target_idx]
            await target_el.click()
            await page.wait_for_timeout(500)
            
            # Fill prompt
            print("Typing prompt into target element...")
            tag = await target_el.evaluate("e => e.tagName")
            if tag in ["INPUT", "TEXTAREA"]:
                await target_el.fill(PROMPT)
            else:
                # Contenteditable
                await page.keyboard.type(PROMPT, delay=10)

            await page.wait_for_timeout(1000)
            os.makedirs("scratch", exist_ok=True)
            await page.screenshot(path="scratch/flow_after_typing.png")
            print("Saved screenshot: scratch/flow_after_typing.png")

            # Look for send/submit button next to the input
            # Typically a button with x > 1200 and y > 750 or aria-label="Send" or icon arrow_forward
            send_btn = await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                for (const b of btns) {
                    const rect = b.getBoundingClientRect();
                    const text = b.innerText || '';
                    const al = b.getAttribute('aria-label') || '';
                    if ((rect.x > 1200 && rect.y > 750) || al.toLowerCase().includes('send') || al.toLowerCase().includes('generate') || text.includes('arrow_forward')) {
                        return { found: true, text: text, aria: al, x: rect.x, y: rect.y };
                    }
                }
                return { found: false };
            }''')

            print("Send button candidate:", send_btn)
            if send_btn['found']:
                print(f"Clicking send button at ({send_btn['x'] + 10}, {send_btn['y'] + 10})...")
                await page.mouse.click(send_btn['x'] + 10, send_btn['y'] + 10)
                print("Clicked! Waiting 10s to observe generation kickoff...")
                await page.wait_for_timeout(10000)

                await page.screenshot(path="scratch/flow_after_send.png")
                print("Saved screenshot: scratch/flow_after_send.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_generate())
