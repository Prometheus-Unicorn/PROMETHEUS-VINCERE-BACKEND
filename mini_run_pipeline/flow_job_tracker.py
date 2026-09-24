"""Job progress tracking, video asset detection, and stream download verification for Google Flow."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import cv2
from playwright.async_api import BrowserContext, Page

logger = logging.getLogger("flow_job_tracker")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [FlowTracker] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

REPO_ROOT = Path(__file__).resolve().parent.parent


class FlowJobTracker:
    """Tracks generation card lifecycle, monitors progress percentage, and retrieves MP4."""

    @staticmethod
    async def snapshot_video_sources(page: Page) -> Set[str]:
        """Snapshots all existing video sources in the workspace before generation."""
        sources = set()
        videos = await page.query_selector_all("video")
        for v in videos:
            src = await v.get_attribute("src")
            if src:
                sources.add(src)
        return sources

    @staticmethod
    async def resolve_credit_approval(page: Page) -> Optional[str]:
        """Detects and clicks 'Always approve' or 'Approve' credit gates in Flow session."""
        try:
            # First try evaluating in DOM to find text node and closest clickable element
            clicked = await page.evaluate('''() => {
                for (const text of ['Always approve', 'Approve']) {
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                    let node;
                    while (node = walker.nextNode()) {
                        const val = (node.nodeValue || '').trim();
                        if (val === text || (val.includes(text) && val.length < text.length + 15)) {
                            const btn = node.parentElement ? (node.parentElement.closest('button, [role="button"], div[tabindex], div') || node.parentElement) : null;
                            if (btn && btn.offsetParent !== null) {
                                btn.click();
                                return text;
                            }
                        }
                    }
                }
                return null;
            }''')
            if clicked in ("Always approve", "Approve"):
                return clicked
        except Exception:
            pass

        # Fallback to Playwright get_by_text locators
        for text_target in ["Always approve", "Approve"]:
            try:
                loc = page.get_by_text(text_target, exact=False).first
                if await loc.is_visible(timeout=500):
                    await loc.click(force=True)
                    return text_target
            except Exception:
                pass
        return None

    @staticmethod
    async def wait_for_new_video(
        page: Page,
        initial_sources: Set[str],
        timeout_sec: int = 600,
        poll_interval_sec: float = 2.0,
    ) -> str:
        """Polls until a newly generated video appears with completed progress."""
        logger.info(f"Monitoring generation progress (timeout={timeout_sec}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout_sec:
            elapsed = int(time.time() - start_time)

            # Check for model/duration disambiguation options (e.g., Veo 3.1 - Fast 8s tier requirement)
            opt_btn = await page.query_selector(
                "button:has-text('Use 8s duration'), [role='radio']:has-text('8s'), button:has-text('Switch to Omni')"
            )
            if opt_btn and await opt_btn.is_visible():
                btn_txt = (await opt_btn.inner_text()).strip()
                logger.info(f"[{elapsed}s] Resolving model option: Clicking '{btn_txt}'...")
                await opt_btn.click()
                await asyncio.sleep(2.0)

            # Check for credit approval modal
            approved_text = await FlowJobTracker.resolve_credit_approval(page)
            if approved_text:
                logger.info(f"[{elapsed}s] Credit approval gate detected & resolved: Clicked '{approved_text}'")
                await asyncio.sleep(2.0)

            # Check for fatal agent error cards in session
            error_card = await page.query_selector("div:has-text('Something went wrong'), div:has-text('Failed')")
            if error_card and await error_card.is_visible():
                err_text = (await error_card.inner_text()).strip()
                if "Something went wrong" in err_text or "Failed" in err_text:
                    logger.error(f"[{elapsed}s] Google Flow Agent error card: {err_text}")
                    scratch_dir = REPO_ROOT / "scratch"
                    scratch_dir.mkdir(parents=True, exist_ok=True)
                    err_png = scratch_dir / f"flow_agent_error_{int(time.time())}.png"
                    await page.screenshot(path=str(err_png))
                    raise RuntimeError(f"Google Flow Agent returned fatal error: '{err_text}'. Screenshot: {err_png}")

            # Check for new video elements
            videos = await page.query_selector_all("video")
            for v in videos:
                src = await v.get_attribute("src")
                if src and src not in initial_sources:
                    if "blob:" in src or "storage.googleapis" in src or "flow" in src or "googlevideo" in src or "http" in src:
                        logger.info(f"[{elapsed}s] Verified new video asset detected: {src[:75]}...")
                        return src

            # Fallback DOM property check for currentSrc / src set via JS
            try:
                dom_vids = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('video')).map(v => v.src || v.currentSrc).filter(Boolean);
                }''')
                for d_src in dom_vids:
                    if d_src and d_src not in initial_sources:
                        if "blob:" in d_src or "storage.googleapis" in d_src or "flow" in d_src or "googlevideo" in d_src or "http" in d_src:
                            logger.info(f"[{elapsed}s] Verified new video asset detected via DOM property: {d_src[:75]}...")
                            return d_src
            except Exception:
                pass

            # Extract percentage progress from UI cards
            progress_pct = await page.evaluate('''() => {
                const els = document.querySelectorAll('*');
                for (const el of els) {
                    const txt = (el.innerText || '').trim();
                    if (/^\\d{1,3}%$/.test(txt) && el.children.length === 0) {
                        return txt;
                    }
                }
                return null;
            }''')

            if progress_pct:
                logger.info(f"[{elapsed}s] Google Flow Render Progress: {progress_pct}")
                if progress_pct == "100%":
                    # Render complete on Google Flow servers: activate card to mount video in DOM
                    await asyncio.sleep(2.0)
                    try:
                        await page.mouse.dblclick(300, 200)
                        await asyncio.sleep(1.0)
                    except Exception:
                        pass
            elif elapsed % 20 == 0:
                logger.info(f"[{elapsed}s] Waiting for generative render queue...")

            await asyncio.sleep(poll_interval_sec)

        # Fallback check on canvas tiles
        videos = await page.query_selector_all("video")
        for v in videos:
            src = await v.get_attribute("src")
            if src and src not in initial_sources:
                return src

        scratch_dir = REPO_ROOT / "scratch"
        scratch_dir.mkdir(parents=True, exist_ok=True)
        timeout_png = scratch_dir / "flow_generation_timeout.png"
        await page.screenshot(path=str(timeout_png))
        raise TimeoutError(f"Video generation timed out after {timeout_sec}s. Screenshot: {timeout_png}")


class FlowVideoDownloader:
    """Downloads video stream and validates video geometry and metadata via OpenCV."""

    @staticmethod
    async def download_and_verify(
        page: Page,
        video_url: str,
        dest_path: Path,
        context: BrowserContext,
        sniffed_media_urls: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Downloads the video file and validates its physical attributes."""
        dest_path = Path(dest_path)
        dest_dir = dest_path.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        existing_mp4s = set(dest_dir.glob("*.mp4"))

        logger.info(f"Downloading video to {dest_path}...")

        # If dest_path was already populated by background download listener, verify directly
        if dest_path.exists() and dest_path.stat().st_size > 50000:
            downloaded = True
        else:
            downloaded = False

        # 1. Try download button (editor view or card toolbar)
        if not downloaded:
            dl_btn = await page.query_selector(
                "button[aria-label*='Download' i], [mattooltip*='Download' i], button:has(mat-icon:has-text('download')), [role='menuitem']:has-text('Download'), button:has-text('Download')"
            )
            if not dl_btn:
                # If still on grid, activate newest card to open editor view
                try:
                    await page.mouse.dblclick(300, 200)
                    await page.wait_for_timeout(2000)
                    dl_btn = await page.query_selector(
                        "button[aria-label*='Download' i], [mattooltip*='Download' i], button:has(mat-icon:has-text('download')), [role='menuitem']:has-text('Download'), button:has-text('Download')"
                    )
                except Exception:
                    pass

            if dl_btn:
                try:
                    await dl_btn.click()
                    await page.wait_for_timeout(1000)

                    # Look for 720p menu item in popover / dropdown
                    dl_720p = await page.query_selector(
                        "[role='menuitem']:has-text('720p'), button:has-text('720p'), button:has-text('Original size'), [role='menuitem']:has-text('Original')"
                    )
                    if dl_720p and await dl_720p.is_visible():
                        logger.info("Found 720p Original size option, clicking...")
                        try:
                            async with page.expect_download(timeout=10000) as dl_info:
                                await dl_720p.click()
                            dl = await dl_info.value
                            await dl.save_as(str(dest_path))
                            downloaded = True
                            logger.info("Downloaded via 720p menu browser download event.")
                        except Exception:
                            # If expect_download times out, CDP or stream download handler picks it up
                            pass
                    else:
                        try:
                            async with page.expect_download(timeout=5000) as dl_info:
                                await dl_btn.click()
                            dl = await dl_info.value
                            await dl.save_as(str(dest_path))
                            downloaded = True
                            logger.info("Downloaded directly via toolbar download button.")
                        except Exception:
                            pass
                except Exception as dl_err:
                    logger.warning(f"Browser download button trigger: {dl_err}")

        # 2. Check for CDP-saved files in dest_dir
        if not downloaded or not dest_path.exists() or dest_path.stat().st_size == 0:
            for _ in range(12):
                cr_files = list(dest_dir.glob("*.crdownload"))
                if cr_files:
                    await asyncio.sleep(0.5)
                    continue
                new_mp4s = [f for f in dest_dir.glob("*.mp4") if f != dest_path and f not in existing_mp4s]
                if not new_mp4s:
                    new_mp4s = [f for f in dest_dir.glob("*.mp4") if f != dest_path and f.stat().st_size > 10000]
                if new_mp4s:
                    newest = max(new_mp4s, key=lambda f: f.stat().st_mtime)
                    if newest.stat().st_size > 10000:
                        import shutil
                        if newest != dest_path:
                            shutil.copy(newest, dest_path)
                        downloaded = True
                        logger.info(f"Retrieved CDP-downloaded file: {newest.name} ({dest_path.stat().st_size:,} bytes)")
                        break
                await asyncio.sleep(0.2)

        # 3. Try sniffed media URLs from network stream
        if not downloaded or not dest_path.exists() or dest_path.stat().st_size == 0:
            if sniffed_media_urls:
                logger.info(f"Attempting download from {len(sniffed_media_urls)} network-sniffed media URLs...")
                for url in reversed(sniffed_media_urls):
                    try:
                        logger.info(f"Fetching sniffed stream: {url[:80]}...")
                        response = await context.request.get(url)
                        body = await response.body()
                        if len(body) > 10000:
                            dest_path.write_bytes(body)
                            downloaded = True
                            logger.info(f"Successfully saved {len(body):,} bytes from sniffed stream.")
                            break
                    except Exception as s_err:
                        logger.warning(f"Failed fetching sniffed URL {url[:60]}: {s_err}")

        # 4. Fallback: Context HTTP request fetch with video_url
        if not downloaded or not dest_path.exists() or dest_path.stat().st_size == 0:
            if video_url:
                try:
                    logger.info(f"Fetching video via authenticated context HTTP request: {video_url[:80]}...")
                    response = await context.request.get(video_url)
                    body = await response.body()
                    if len(body) > 10000:
                        dest_path.write_bytes(body)
                        downloaded = True
                        logger.info(f"Saved {len(body):,} bytes directly from video URL.")
                except Exception as req_err:
                    logger.warning(f"Context request fetch failed: {req_err}")

        # 5. Deterministic verification
        if not dest_path.exists() or dest_path.stat().st_size == 0:
            raise FileNotFoundError(f"Failed saving video to {dest_path}")

        cap = cv2.VideoCapture(str(dest_path))
        if not cap.isOpened():
            raise ValueError(f"Downloaded file {dest_path} is not a valid video container.")

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        dur = cnt / fps if fps > 0 else 0
        cap.release()

        info = {
            "path": str(dest_path),
            "sizeBytes": dest_path.stat().st_size,
            "width": w,
            "height": h,
            "fps": fps,
            "frameCount": cnt,
            "durationSec": dur,
        }
        logger.info(f"Asset Verified: {w}x{h} @ {fps:.2f}fps, {cnt} frames ({dur:.2f}s), {info['sizeBytes']:,} bytes")
        return info
