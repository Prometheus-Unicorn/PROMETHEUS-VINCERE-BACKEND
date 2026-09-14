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

async def trigger_generation():
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
        await page.wait_for_timeout(8000)

        # Find the prompt input
        inputs = await page.query_selector_all('input, textarea, [contenteditable="true"]')
        target_el = None
        for el in inputs:
            rect = await el.bounding_box()
            if rect and rect['x'] > 800 and rect['y'] > 600:
                target_el = el
                break

        if not target_el:
            print("Could not find prompt input.")
            await browser.close()
            return

        print("Focusing prompt input...")
        await target_el.click()
        await page.wait_for_timeout(500)

        # Clear any existing text
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.wait_for_timeout(300)

        print("Typing prompt...")
        await page.keyboard.type(PROMPT, delay=5)
        await page.wait_for_timeout(1000)

        # Find the circular send button (it's the furthest right button at the bottom)
        send_btn_pos = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
            let maxRightBtn = null;
            let maxX = 0;
            for (const b of btns) {
                const r = b.getBoundingClientRect();
                if (r.x > 1250 && r.y > 750 && r.width > 0) {
                    if (r.x > maxX) {
                        maxX = r.x;
                        maxRightBtn = { x: r.x + r.width/2, y: r.y + r.height/2, w: r.width, h: r.height };
                    }
                }
            }
            return maxRightBtn;
        }''')

        print("Target Send Button position:", send_btn_pos)
        if send_btn_pos:
            print(f"Clicking send button at ({send_btn_pos['x']}, {send_btn_pos['y']})...")
            await page.mouse.click(send_btn_pos['x'], send_btn_pos['y'])
        else:
            print("Sending Enter key...")
            await page.keyboard.press("Enter")

        print("Submitted! Monitoring workspace for generation...")
        os.makedirs("scratch", exist_ok=True)
        
        # Poll for 30 seconds to observe generation state
        for sec in range(6):
            await page.wait_for_timeout(5000)
            elapsed = (sec + 1) * 5
            print(f"Elapsed: {elapsed}s...")
            await page.screenshot(path=f"scratch/flow_gen_sec_{elapsed}.png")
            
            # Check for video elements or progress indicators
            video = await page.query_selector("video")
            if video:
                src = await video.get_attribute("src")
                print(f">>> FOUND VIDEO at {elapsed}s: {src}")
                break

            # Check text in the right sidebar for status
            chat_text = await page.evaluate('''() => {
                const el = document.querySelector('[role="complementary"], aside, .sidebar');
                return el ? el.innerText : '';
            }''')
            if chat_text:
                lines = [l.strip() for l in chat_text.splitlines() if l.strip()]
                print(f"Sidebar status lines ({elapsed}s): {lines[-3:]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(trigger_generation())
