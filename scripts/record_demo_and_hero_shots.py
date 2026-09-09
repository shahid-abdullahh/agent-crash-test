import asyncio
import os
import shutil
import glob
from playwright.async_api import async_playwright

DOCS_DIR = os.path.abspath("docs/presentation")
SCREENSHOT_DIR = os.path.abspath("docs/presentation/screenshots")
VIDEO_TMP_DIR = os.path.abspath("docs/presentation/video_tmp")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_TMP_DIR, exist_ok=True)

async def record_demo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=VIDEO_TMP_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        print("1. Loading Overview Dashboard...")
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        print("2. Showing API Integrations...")
        await page.locator("button:has-text('API Integrations')").click()
        await page.wait_for_timeout(3000)

        # Inspect generated code modal/view
        inspect_btn = page.locator("button:has-text('Inspect'), button:has-text('View Code'), button:has-text('Tools')").first
        if await inspect_btn.count() > 0:
            await inspect_btn.click()
            await page.wait_for_timeout(2500)

        print("3. Showing Connectors...")
        await page.locator("button:has-text('Connectors')").click()
        await page.wait_for_timeout(3000)

        print("4. Showing Crash Test Console...")
        await page.locator("button:has-text('Crash Tests')").click()
        await page.wait_for_timeout(2000)

        # 4 & 5. Configure Timeout After Commit + Unsafe Blind Retry
        print("Selecting Timeout After Commit + Unsafe Retry...")
        await page.locator("button:has-text('Timeout After Commit')").click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Unsafe Blind Retry')").click()
        await page.wait_for_timeout(1000)

        print("Running Crash Test (Failure Mode)...")
        await page.locator("button:has-text('RUN CRASH TEST')").click()
        await page.wait_for_timeout(3500)

        # 6, 7, 8, 9, 10, 11: Show Failure Evidence
        print("Capturing 11-hero-failure-evidence.png...")
        # Capture full viewport of test results + evaluation + diagnosis
        await page.screenshot(
            path=os.path.join(SCREENSHOT_DIR, "11-hero-failure-evidence.png"),
            full_page=False
        )

        # Scroll down slightly to showcase full trace & diagnosis in video
        diag_heading = page.locator("text=Root Cause Diagnosis").first
        if await diag_heading.count() > 0:
            await diag_heading.scroll_into_view_if_needed()
            await page.wait_for_timeout(3000)

        trace_heading = page.locator("text=Chronological Trace Evidence").first
        if await trace_heading.count() > 0:
            await trace_heading.scroll_into_view_if_needed()
            await page.wait_for_timeout(3000)

        # Now run Safe Remediated Test to capture 12-remediated-success.png
        print("Configuring Idempotent Safe Retry for Remediation...")
        top_view = page.locator("text=Test Execution Control").first
        if await top_view.count() > 0:
            await top_view.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Idempotent Key (Safe)')").click()
        await page.wait_for_timeout(1000)

        print("Running Crash Test (Remediated Safe Mode)...")
        await page.locator("button:has-text('RUN CRASH TEST')").click()
        await page.wait_for_timeout(3500)

        print("Capturing 12-remediated-success.png...")
        await page.screenshot(
            path=os.path.join(SCREENSHOT_DIR, "12-remediated-success.png"),
            full_page=False
        )
        await page.wait_for_timeout(2000)

        # 12. Show Remediation Diff
        print("12. Showing Remediation Diff...")
        await page.locator("button:has-text('Remediation Diff')").click()
        await page.wait_for_timeout(4000)

        # 13. Show Reliability Analytics
        print("13. Showing Reliability Analytics...")
        await page.locator("button:has-text('Reliability')").click()
        await page.wait_for_timeout(3500)

        print("Completing demo recording...")
        await page.close()
        await context.close()
        await browser.close()

    # Move recorded video to final path
    video_files = glob.glob(os.path.join(VIDEO_TMP_DIR, "*.webm"))
    if video_files:
        src_video = video_files[0]
        dst_webm = os.path.join(DOCS_DIR, "agent-crash-test-end-to-end-demo.webm")
        dst_mp4 = os.path.join(DOCS_DIR, "agent-crash-test-end-to-end-demo.mp4")
        shutil.copy2(src_video, dst_webm)
        
        # Check if ffmpeg exists to convert or copy
        ffmpeg_bin = r"C:\Users\Mantique\AppData\Local\ms-playwright\ffmpeg-1011\ffmpeg-win64.exe"
        if os.path.exists(ffmpeg_bin):
            os.system(f'"{ffmpeg_bin}" -y -i "{src_video}" -c:v libx264 -pix_fmt yuv420p "{dst_mp4}"')
        else:
            shutil.copy2(src_video, dst_mp4)
            
        print(f"Video saved to: {dst_mp4} and {dst_webm}")

    # Clean tmp dir
    shutil.rmtree(VIDEO_TMP_DIR, ignore_errors=True)
    print("ALL DEMO EVIDENCE CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(record_demo())
