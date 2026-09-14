import asyncio
from playwright.async_api import async_playwright

PROJECT_URL = "https://flow.google.com/project/36832888-b965-464f-be7c-5252a59910ad"

PROMPT = "Top-down orthographic zenith view of Porsche GT3 RS with carbon bonnet stripes flanked by 4 rotating clock hands, featuring Heavy solid gunmetal 3D block typography with razor-sharp beveled edges, micro-machined brushed metal textures, and dynamic metallic specular reflections, The Slap-Drop asset introduction pushing downward along Z-axis with exponential decrescendo, executing a 2-frame 3% scale squash on impact followed by subtle contact bounce and pendulum settle, timed so that at +5.0s into the sequence the asset achieves locked contact bounce and physical impact synchronously with the cue words 'This isn't just a car, it's a statement.', Pristine matte off-white (#ECECEC) tactile paper canvas with subtle fibrous grain texture, isolated by clean geometric negative space, bounded by delicate sinuous vector guide curves, Dramatic chiaroscuro contrast with intense warm 3200K tungsten spotlight, volumetric shafts of light cutting through dusty darkroom air, and razor cool cyan rim backlighting, diffuse high-key ambient studio illumination with zero grungy shadows, projecting a crisp double-layer drop shadow (60% AO + 25% diffuse drop) beneath foreground elements, Vertical 9:16 composition captured on 35mm anamorphic lens with shallow depth of field, smooth oval anamorphic bokeh, continuous anti-stagnation sub-pixel drift (scaling 100% to 101.8%), 24fps cadence, and subtle Kodak 5219 film grain, vertical 9:16 framing with dynamic depth layering, Authentic Curito Swiss editorial motion design, Neue Haas Grotesk Black bold headlines, Editorial New italic serif accents, interactive dashed Figma bounding boxes with circular corner anchor nodes, four-point starburst corner anchors, vertical barcode stamp, and 24fps native cinema cadence."

async def main():
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
        print(f"Opening {PROJECT_URL}...")
        await page.goto(PROJECT_URL, timeout=45000, wait_until='domcontentloaded')
        print("Waiting 15s for canvas hydration...")
        await page.wait_for_timeout(15000)

        # Click at the prompt input area: x=1150, y=850
        print("Clicking prompt input area at (1150, 850)...")
        await page.mouse.click(1150, 850)
        await page.wait_for_timeout(1000)

        # Type prompt using page.keyboard.type
        print("Typing prompt via keyboard...")
        # Type the prompt with a fast delay
        await page.keyboard.type(PROMPT, delay=5)
        await page.wait_for_timeout(2000)

        await page.screenshot(path="scratch/flow_prompt_typed_live.png")
        print("Screenshot saved to scratch/flow_prompt_typed_live.png")

        # Now locate the send button or check its state
        # In screenshot, the arrow button is near (1365, 950) or in viewport: (1365, 875)
        # Let's inspect elements around (1365, 875)
        btn_around = await page.evaluate('''() => {
            const els = document.elementsFromPoint(1365, 875);
            return els.map(e => ({
                tag: e.tagName,
                aria: e.getAttribute('aria-label') || '',
                text: e.innerText || '',
                disabled: e.hasAttribute('disabled')
            }));
        }''')
        print("Elements at send button point (1365, 875):", btn_around)

        # Let's also check elements at (1365, 945) in case y is lower
        btn_lower = await page.evaluate('''() => {
            const els = document.elementsFromPoint(1365, 850);
            return els.map(e => ({
                tag: e.tagName,
                aria: e.getAttribute('aria-label') || '',
                text: e.innerText || '',
                disabled: e.hasAttribute('disabled')
            }));
        }''')
        print("Elements at send button point (1365, 850):", btn_lower)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
