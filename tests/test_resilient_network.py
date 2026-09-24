import asyncio
import tempfile
import unittest
from pathlib import Path
from mini_run_pipeline.resilient_network import (
    calculate_backoff,
    resilient_retry,
    resilient_action,
    TaskCheckpointManager,
)


class TestResilientNetwork(unittest.TestCase):

    def test_calculate_backoff_bounds(self):
        val = calculate_backoff(attempt=2, initial_backoff=1.0, factor=2.0, max_backoff=10.0, jitter=False)
        self.assertEqual(val, 4.0)

        # Max backoff clamp
        val_clamped = calculate_backoff(attempt=10, initial_backoff=1.0, factor=2.0, max_backoff=10.0, jitter=False)
        self.assertEqual(val_clamped, 10.0)

        # Jitter bound
        val_jitter = calculate_backoff(attempt=2, initial_backoff=1.0, factor=2.0, max_backoff=10.0, jitter=True)
        self.assertTrue(2.0 <= val_jitter <= 4.0)

    def test_resilient_retry_sync_success_after_failures(self):
        attempts = 0

        @resilient_retry(max_retries=3, initial_backoff=0.01, max_backoff=0.05)
        def flaky_func():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ConnectionResetError("Transient network drop")
            return "SUCCESS"

        res = flaky_func()
        self.assertEqual(res, "SUCCESS")
        self.assertEqual(attempts, 3)

    def test_resilient_retry_sync_exhaustion(self):
        @resilient_retry(max_retries=2, initial_backoff=0.01, max_backoff=0.05)
        def permanently_failing():
            raise TimeoutError("Dead socket")

        with self.assertRaises(TimeoutError):
            permanently_failing()

    def test_resilient_retry_async(self):
        attempts = 0

        @resilient_retry(max_retries=3, initial_backoff=0.01, max_backoff=0.05)
        async def flaky_async():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise TimeoutError("Async timeout")
            return "ASYNC_SUCCESS"

        res = asyncio.run(flaky_async())
        self.assertEqual(res, "ASYNC_SUCCESS")
        self.assertEqual(attempts, 2)

    def test_resilient_action_with_recovery(self):
        recovery_called = False
        action_attempts = 0

        def recovery():
            nonlocal recovery_called
            recovery_called = True

        def action():
            nonlocal action_attempts
            action_attempts += 1
            if action_attempts == 1:
                raise OSError("Socket dropped")
            return 42

        res = asyncio.run(resilient_action(action, max_retries=2, initial_backoff=0.01, recovery_callback=recovery))
        self.assertEqual(res, 42)
        self.assertTrue(recovery_called)

    def test_task_checkpoint_manager(self):
        with tempfile.TemporaryDirectory() as td:
            cp_file = Path(td) / "test_cp.json"
            mgr = TaskCheckpointManager(cp_file)
            self.assertFalse(mgr.is_completed("step1"))

            mgr.record_step("step1", {"hash": "abc"})
            self.assertTrue(mgr.is_completed("step1"))
            self.assertEqual(mgr.get_step_data("step1")["hash"], "abc")

            # Reload fresh instance from disk
            mgr2 = TaskCheckpointManager(cp_file)
            self.assertTrue(mgr2.is_completed("step1"))
            self.assertEqual(mgr2.get_step_data("step1")["hash"], "abc")


if __name__ == "__main__":
    unittest.main()
