"""Unit tests for FlowJobTracker credit approval resolution."""

import unittest
from unittest.mock import AsyncMock, MagicMock
from mini_run_pipeline.flow_job_tracker import FlowJobTracker


class TestFlowApprovalGate(unittest.IsolatedAsyncioTestCase):
    async def test_resolve_credit_approval_dom_eval(self):
        """Tests that resolve_credit_approval succeeds when DOM evaluation clicks the button."""
        mock_page = MagicMock()
        mock_page.evaluate = AsyncMock(return_value="Always approve")

        result = await FlowJobTracker.resolve_credit_approval(mock_page)
        self.assertEqual(result, "Always approve")
        mock_page.evaluate.assert_called_once()

    async def test_resolve_credit_approval_locator_fallback(self):
        """Tests fallback to Playwright get_by_text locator when DOM eval returns None."""
        mock_page = MagicMock()
        mock_page.evaluate = AsyncMock(return_value=None)

        mock_locator = MagicMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.click = AsyncMock()

        mock_page.get_by_text = MagicMock(return_value=MagicMock(first=mock_locator))

        result = await FlowJobTracker.resolve_credit_approval(mock_page)
        self.assertEqual(result, "Always approve")
        mock_locator.click.assert_called_once_with(force=True)

    async def test_resolve_credit_approval_none_present(self):
        """Tests that resolve_credit_approval returns None when no approval gate exists."""
        mock_page = MagicMock()
        mock_page.evaluate = AsyncMock(return_value=None)

        mock_locator = MagicMock()
        mock_locator.is_visible = AsyncMock(return_value=False)
        mock_page.get_by_text = MagicMock(return_value=MagicMock(first=mock_locator))

        result = await FlowJobTracker.resolve_credit_approval(mock_page)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
