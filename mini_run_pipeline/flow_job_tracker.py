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
            approve_btn = await page.query_selector("button:has-text('Always approve'), button:has-text('Approve')")
            if approve_btn and await approve_btn.is_visible():
                btn_txt = (await approve_btn.inner_text()).strip()
                logger.info(f"[{elapsed}s] Credit approval gate detected: Clicking '{btn_txt}'...")
                await approve_btn.click()
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
                    if "blob:" in src or "storage.googleapis" in src or "http" in src:
                        logger.info(f"[{elapsed}s] Verified new video asset detected: {src[:75]}...")
                        return src

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
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading video to {dest_path}...")

        # 1. Try download button and handle 720p dropdown menu
        downloaded = False
        dl_btn = await page.query_selector(
            "button:has-text('Download'), [aria-label*='download' i], button:has(mat-icon:has-text('download'))"
        )
        if dl_btn:
            try:
                await dl_btn.click()
                await page.wait_for_timeout(1000)

                # Look for 720p menu item in popover / dropdown
                dl_720p = await page.query_selector(
                    "[role='menuitem']:has-text('720p'), button:has-text('720p'), button:has-text('Original size')"
                )
                if dl_720p and await dl_720p.is_visible():
                    logger.info("Found 720p Original size option, initiating browser download...")
                    async with page.expect_download(timeout=20000) as dl_info:
                        await dl_720p.click()
                    dl = await dl_info.value
                    await dl.save_as(str(dest_path))
                    downloaded = True
                    logger.info("Downloaded via 720p menu browser download event.")
                else:
                    async with page.expect_download(timeout=10000) as dl_info:
                        await dl_btn.click()
                    dl = await dl_info.value
                    await dl.save_as(str(dest_path))
                    downloaded = True
                    logger.info("Downloaded directly via toolbar download button.")
            except Exception as dl_err:
                logger.warning(f"Browser download event failed or timed out: {dl_err}")

        # 2. Try sniffed media URLs from network stream
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

        # 3. Fallback: Context HTTP request fetch with video_url
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

        # 4. Deterministic verification
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
