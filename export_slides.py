"""
export_slides.py
----------------
Exports each slide of carousel.html as a 1080×1350 px PNG.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python export_slides.py
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_HTML  = Path(__file__).parent / "carousel.html"
OUTPUT_DIR  = Path(__file__).parent / "slides"

TOTAL_SLIDES = 7
VIEW_W, VIEW_H = 420, 525          # logical px (4:5 aspect ratio)
SCALE = 1080 / 420                 # ≈ 2.5714 → output becomes 1080×1350 px


# ── Export Routine ────────────────────────────────────────────────────────────
async def export() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(
            viewport={"width": VIEW_W, "height": VIEW_H},
            device_scale_factor=SCALE,
        )

        await page.goto(f"file://{INPUT_HTML.resolve()}")
        # Wait for all resources (including Google Fonts) to finish loading
        await page.wait_for_load_state("networkidle")

        for i in range(TOTAL_SLIDES):
            # Snap the carousel track to slide i and wait for the CSS transition to settle
            await page.evaluate(
                """offset => {
                    const track = document.querySelector('.carousel-track');
                    track.style.transform = `translateX(${offset}px)`;
                    return new Promise(resolve => {
                        const onEnd = () => { track.removeEventListener('transitionend', onEnd); resolve(); };
                        track.addEventListener('transitionend', onEnd);
                        // Fallback: resolve after transition duration + buffer
                        setTimeout(resolve, 500);
                    });
                }""",
                -i * VIEW_W,
            )

            out_path = OUTPUT_DIR / f"slide_{i + 1:02d}.png"
            await page.screenshot(
                path=str(out_path),
                clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
            )
            print(f"  ✓  slide {i + 1}/{TOTAL_SLIDES} → {out_path.name}")

        await browser.close()

    print(f"\nDone! {TOTAL_SLIDES} slides saved to '{OUTPUT_DIR}/'")


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(export())
