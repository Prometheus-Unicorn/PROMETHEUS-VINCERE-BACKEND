"""Unit tests for FlowJobTracker and FlowVideoDownloader subsystems."""

import asyncio
import cv2
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from mini_run_pipeline.flow_job_tracker import FlowJobTracker, FlowVideoDownloader


class TestFlowJobTracker(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_job_tracker_delta_video_detection(self):
        mock_page = MagicMock()
        initial_sources = {"https://flow.google.com/old_video_1.mp4"}

        # First query returns only old video
        video_old = MagicMock()
        video_old.get_attribute = AsyncMock(return_value="https://flow.google.com/old_video_1.mp4")

        # Second query returns old video + new video
        video_new = MagicMock()
        video_new.get_attribute = AsyncMock(return_value="https://flow.google.com/new_render_123.mp4")

        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [video_old],
            [video_old, video_new],
        ])
        mock_page.evaluate = AsyncMock(return_value="50%")

        detected_url = await FlowJobTracker.wait_for_new_video(
            page=mock_page,
            initial_sources=initial_sources,
            timeout_sec=5,
            poll_interval_sec=0.05,
        )
        self.assertEqual(detected_url, "https://flow.google.com/new_render_123.mp4")

    @patch("mini_run_pipeline.flow_job_tracker.cv2.VideoCapture")
    async def test_video_downloader_sniffed_stream(self, mock_cv2):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 720,
            cv2.CAP_PROP_FRAME_HEIGHT: 1280,
            cv2.CAP_PROP_FPS: 24.0,
            cv2.CAP_PROP_FRAME_COUNT: 192,
        }.get(prop, 0)
        mock_cv2.return_value = mock_cap

        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        mock_context = MagicMock()
        mock_response = MagicMock()
        mock_response.body = AsyncMock(return_value=b"fake-video-bytes" * 1000)
        mock_context.request.get = AsyncMock(return_value=mock_response)

        dest_file = self.temp_dir / "downloaded_test.mp4"
        meta = await FlowVideoDownloader.download_and_verify(
            page=mock_page,
            video_url="https://flow-content.google/video/fallback.mp4",
            dest_path=dest_file,
            context=mock_context,
            sniffed_media_urls=["https://flow-content.google/video/sniffed_exact.mp4"],
        )
        self.assertTrue(dest_file.exists())
        self.assertEqual(meta["width"], 720)
        self.assertEqual(meta["height"], 1280)
        self.assertEqual(meta["durationSec"], 8.0)
        mock_context.request.get.assert_called_with("https://flow-content.google/video/sniffed_exact.mp4")

    @patch("mini_run_pipeline.flow_job_tracker.cv2.VideoCapture")
    async def test_video_downloader_menu_720p(self, mock_cv2):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 720,
            cv2.CAP_PROP_FRAME_HEIGHT: 1280,
            cv2.CAP_PROP_FPS: 24.0,
            cv2.CAP_PROP_FRAME_COUNT: 192,
        }.get(prop, 0)
        mock_cv2.return_value = mock_cap

        mock_page = MagicMock()
        mock_dl_btn = MagicMock()
        mock_dl_btn.click = AsyncMock()

        mock_dl_720p = MagicMock()
        mock_dl_720p.is_visible = AsyncMock(return_value=True)
        mock_dl_720p.click = AsyncMock()

        async def fake_query_selector(selector):
            if "Download" in selector or "download" in selector:
                return mock_dl_btn
            if "720p" in selector:
                return mock_dl_720p
            return None

        mock_page.query_selector = AsyncMock(side_effect=fake_query_selector)
        mock_page.wait_for_timeout = AsyncMock()

        mock_dl_val = MagicMock()
        mock_dl_val.save_as = AsyncMock()

        class FakeExpectDownload:
            def __init__(self, val):
                self.value = asyncio.Future()
                self.value.set_result(val)
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        mock_page.expect_download = MagicMock(return_value=FakeExpectDownload(mock_dl_val))

        dest_file = self.temp_dir / "menu_720p_test.mp4"
        dest_file.write_bytes(b"downloaded-720p-bytes" * 500)

        meta = await FlowVideoDownloader.download_and_verify(
            page=mock_page,
            video_url="",
            dest_path=dest_file,
            context=MagicMock(),
        )
        self.assertEqual(meta["width"], 720)
        self.assertEqual(meta["height"], 1280)
        mock_dl_720p.click.assert_called_once()

    @patch("mini_run_pipeline.flow_job_tracker.cv2.VideoCapture")
    async def test_video_downloader_cdp_file_retrieval(self, mock_cv2):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 720,
            cv2.CAP_PROP_FRAME_HEIGHT: 1280,
            cv2.CAP_PROP_FPS: 24.0,
            cv2.CAP_PROP_FRAME_COUNT: 192,
        }.get(prop, 0)
        mock_cv2.return_value = mock_cap

        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.wait_for_timeout = AsyncMock()

        # Simulate CDP writing a new mp4 file into the folder
        cdp_file = self.temp_dir / "cdp_downloaded_render.mp4"
        cdp_file.write_bytes(b"cdp-stream-bytes" * 5000)

        dest_file = self.temp_dir / "final_target.mp4"
        meta = await FlowVideoDownloader.download_and_verify(
            page=mock_page,
            video_url="",
            dest_path=dest_file,
            context=MagicMock(),
        )
        self.assertTrue(dest_file.exists())
        self.assertEqual(meta["width"], 720)
        self.assertEqual(meta["height"], 1280)
        self.assertEqual(dest_file.stat().st_size, cdp_file.stat().st_size)


if __name__ == "__main__":
    unittest.main()

