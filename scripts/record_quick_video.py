import asyncio
import os
import glob
import shutil
from playwright.async_api import async_playwright

OUT_DIR = os.path.abspath("docs/presentation")
VIDEO_DIR = os.path.join(OUT_DIR, "vrec")
os.makedirs(VIDEO_DIR, exist_ok=True)

async def record():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        print("1. Overview...")
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        print("2. Integrations...")
        await page.locator("button:has-text('API Integrations')").click()
        await page.wait_for_timeout(2000)

        print("3. Connectors...")
        await page.locator("button:has-text('Connectors')").click()
        await page.wait_for_timeout(2000)

        print("4. Crash Tests (Fault Scenario)...")
        await page.locator("button:has-text('Crash Tests')").click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Timeout After Commit')").click()
        await page.wait_for_timeout(800)

        await page.locator("button:has-text('Unsafe Blind Retry')").click()
        await page.wait_for_timeout(800)

        await page.locator("button:has-text('RUN CRASH TEST')").click()
        await page.wait_for_timeout(3000)

        # Scroll to diagnosis & trace
        diag = page.locator("text=Root Cause Diagnosis").first
        if await diag.count() > 0:
            await diag.scroll_into_view_if_needed()
            await page.wait_for_timeout(2500)

        trace = page.locator("text=Chronological Trace Evidence").first
        if await trace.count() > 0:
            await trace.scroll_into_view_if_needed()
            await page.wait_for_timeout(2500)

        # Safe Remediated Run
        top = page.locator("text=Test Execution Control").first
        if await top.count() > 0:
            await top.scroll_into_view_if_needed()
            await page.wait_for_timeout(800)

        await page.locator("button:has-text('Idempotent Key (Safe)')").click()
        await page.wait_for_timeout(800)

        await page.locator("button:has-text('RUN CRASH TEST')").click()
        await page.wait_for_timeout(3000)

        print("5. Remediation Diff...")
        await page.locator("button:has-text('Remediation Diff')").click()
        await page.wait_for_timeout(3000)

        print("6. Reliability...")
        await page.locator("button:has-text('Reliability')").click()
        await page.wait_for_timeout(2500)

        await page.close()
        await context.close()
        await browser.close()

    files = glob.glob(os.path.join(VIDEO_DIR, "*.webm"))
    if files:
        src = files[0]
        dst_webm = os.path.join(OUT_DIR, "agent-crash-test-end-to-end-demo.webm")
        dst_mp4 = os.path.join(OUT_DIR, "agent-crash-test-end-to-end-demo.mp4")
        shutil.copy2(src, dst_webm)
        shutil.copy2(src, dst_mp4)
        print(f"Video saved: {dst_webm} & {dst_mp4}")
    shutil.rmtree(VIDEO_DIR, ignore_errors=True)
    print("DEMO RECORDING COMPLETE!")

if __name__ == "__main__":
    asyncio.run(record())
