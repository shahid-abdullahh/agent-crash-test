import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = os.path.abspath("docs/presentation/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await context.new_page()

        print("1. Loading Dashboard at http://127.0.0.1:5173...")
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 01 - Overview
        print("2. Capturing 01-overview.png...")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01-overview.png"), full_page=False)

        # 02 - Integrations
        print("3. Capturing 02-integrations.png...")
        await page.locator("button:has-text('API Integrations')").click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02-integrations.png"), full_page=False)

        # 03 - Generated Tools / Code
        print("4. Capturing 03-generated-tools.png...")
        inspect_btn = page.locator("button:has-text('Inspect'), button:has-text('View Code'), button:has-text('Tools')").first
        if await inspect_btn.count() > 0:
            await inspect_btn.click()
            await page.wait_for_timeout(500)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03-generated-tools.png"), full_page=False)

        # 04 - Connectors
        print("5. Capturing 04-connectors.png...")
        await page.locator("button:has-text('Connectors')").click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04-connectors.png"), full_page=False)

        # 05 - Crash Tests
        print("6. Navigating to Crash Tests...")
        await page.locator("button:has-text('Crash Tests')").click()
        await page.wait_for_timeout(800)
        
        # Click "Timeout After Commit" scenario
        await page.locator("button:has-text('Timeout After Commit')").click()
        await page.wait_for_timeout(300)
        
        # Click "RUN CRASH TEST"
        await page.locator("button:has-text('RUN CRASH TEST')").click()
        await page.wait_for_timeout(2500)

        print("7. Capturing 05-crash-test.png...")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05-crash-test.png"), full_page=False)

        # 06 - Failure Trace
        print("8. Capturing 06-failure-trace.png...")
        trace_viewer = page.locator("text=Chronological Trace Evidence").first
        if await trace_viewer.count() > 0:
            await trace_viewer.scroll_into_view_if_needed()
            await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06-failure-trace.png"), full_page=False)

        # 07 - Diagnosis
        print("9. Capturing 07-diagnosis.png...")
        diag_viewer = page.locator("text=Root Cause Diagnosis").first
        if await diag_viewer.count() > 0:
            await diag_viewer.scroll_into_view_if_needed()
            await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07-diagnosis.png"), full_page=False)

        # 08 - Remediation Diff
        print("10. Capturing 08-before-after.png...")
        await page.locator("button:has-text('Remediation Diff')").click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08-before-after.png"), full_page=False)

        # 09 - API Documentation
        print("11. Capturing 09-documentation.png...")
        await page.locator("button:has-text('API Docs')").click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09-documentation.png"), full_page=False)

        # 10 - Reliability Analytics
        print("12. Capturing 10-reliability.png...")
        await page.locator("button:has-text('Reliability')").click()
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10-reliability.png"), full_page=False)

        await browser.close()
        print("SUCCESS: ALL 10 PRESENTATION SCREENSHOTS CAPTURED!")

if __name__ == "__main__":
    asyncio.run(capture_all())
