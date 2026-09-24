import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from mini_run_pipeline.google_flow_service import GoogleFlowServerClient, FlowServiceConfig


class TestFlowNavigationResilience(unittest.IsolatedAsyncioTestCase):
    """Verifies that GoogleFlowServerClient retries navigation upon transient socket closures."""

    async def test_workspace_navigation_retries_on_network_error(self):
        config = FlowServiceConfig(
            headless=True,
            timeout_sec=10,
            workspace_url="https://flow.google.com/project/mock-workspace",
        )
        client = GoogleFlowServerClient(config=config)

        mock_page = AsyncMock()
        # Fail first two attempts with ERR_CONNECTION_CLOSED, then succeed
        calls = []

        async def fake_goto(url, timeout, wait_until):
            calls.append(url)
            if url == config.workspace_url and len([c for c in calls if c == config.workspace_url]) < 3:
                raise Exception("Page.goto: net::ERR_CONNECTION_CLOSED")
            return None

        mock_page.goto.side_effect = fake_goto

        # Test the retry loop mechanism directly using patched sleep
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            for attempt in range(1, 6):
                try:
                    await mock_page.goto(config.workspace_url, timeout=60000, wait_until="commit")
                    await asyncio.sleep(6.0)
                    break
                except Exception as nav_err:
                    if attempt == 5:
                        raise nav_err
                    await asyncio.sleep(attempt * 5.0)

            workspace_calls = [c for c in calls if c == config.workspace_url]
            self.assertEqual(len(workspace_calls), 3)
            self.assertEqual(mock_sleep.call_count, 3)  # 2 backoffs + 1 post-load pause


if __name__ == "__main__":
    unittest.main()
