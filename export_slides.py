import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Config based on project rules[cite: 1]
INPUT_HTML = Path("carousel.html")
OUTPUT_DIR = Path("slides")
OUTPUT_DIR.mkdir(exist_ok=True)
TOTAL_SLIDES = 7
VIEW_W, VIEW_H = 420, 525
SCALE = 1080 / 420

async def export():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": VIEW_W, "height": VIEW_H}, device_scale_factor=SCALE)
        await page.goto(f"file://{INPUT_HTML.absolute()}")
        await page.wait_for_timeout(3000) # Wait for fonts[cite: 1]

        for i in range(TOTAL_SLIDES):
            # Move track[cite: 1]
            await page.evaluate(f"document.querySelector('.carousel-track').style.transform = 'translateX({-i * 420}px)'")
            await page.wait_for_timeout(500)
            await page.screenshot(path=str(OUTPUT_DIR / f"slide_{i+1}.png"), clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H})
            print(f"Exported {i+1}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(export())
