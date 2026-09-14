import asyncio
import os
import time
from playwright.async_api import async_playwright

AUTH_PATH = "config/flow_auth.json"
PROJECT_URL = "https://flow.google.com/project/379a5a1c-4f58-4e14-bc0c-16e55ead68d6"

PROMPT = (
    "Top-down orthographic zenith perspective of a sculpted white Porsche 911 GT3 RS "
    "with carbon fiber dual hood vents and massive rear wing, anchored by deep ambient "
    "occlusion floor contact shadows, flanked by radial clock hands and precision compass "
    "needles sweeping dynamically and snapping to magnetic lock. "
    "Dramatic chiaroscuro contrast with intense warm 3200K tungsten spotlight, "
    "volumetric shafts of light cutting through dusty studio air, "
    "razor cool cyan rim backlighting throwing sharp directional highlights across bodywork. "
    "Vertical 9:16 composition, 35mm anamorphic lens, shallow depth of field, "
    "smooth oval anamorphic bokeh, continuous anti-stagnation sub-pixel drift, "
    "24fps cadence, subtle Kodak 5219 film grain, "
    "high-agency luxury automotive editorial motion design, crisp vector edges."
)

async def test_input_and_settings():
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
        await page.goto(PROJECT_URL, timeout=45000, wait_until="networkidle")
        await page.wait_for_timeout(4000)

        # 1. Locate the prompt input at bottom right
        print("Looking for 'What do you want to create?' input...")
        prompt_input = await page.wait_for_selector(
            "textarea, [contenteditable='true'], input[placeholder*='create' i], div[placeholder*='create' i]",
            timeout=10000
        )

        if not prompt_input:
            # Fallback: search by placeholder text in all elements
            prompt_input = await page.query_selector("[placeholder*='What do you want to create' i]")

        print("Found prompt input element:", prompt_input)

        # Inspect element details
        tag = await prompt_input.evaluate("el => el.tagName")
        ph = await prompt_input.get_attribute("placeholder")
        print(f"Input tag: {tag}, placeholder: '{ph}'")

        # Type the prompt
        await prompt_input.click()
        await prompt_input.fill("")
        await prompt_input.type(PROMPT, delay=10)
        print("Prompt typed successfully!")

        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/flow_prompt_typed.png")
        print("Screenshot saved: scratch/flow_prompt_typed.png")

        # Check settings button (sliders icon next to submit arrow)
        settings_btns = await page.query_selector_all("button:has(span:has-text('tune')), button:has(span:has-text('settings')), button[aria-label*='setting' i], button[aria-label*='model' i]")
        print(f"Found {len(settings_btns)} candidate settings buttons.")

        # Find submit button (the arrow pointing right next to the input)
        submit_btns = await page.query_selector_all("button:has(span:has-text('arrow_forward')), button[aria-label*='Send' i], button[aria-label*='Submit' i], button[aria-label*='Generate' i]")
        print(f"Found {len(submit_btns)} candidate submit buttons.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_input_and_settings())
