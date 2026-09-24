"""Resilient network operations, jittered backoff, and uninterrupted execution manager.

Designed to survive high network volatility, socket drops, DNS failures, and transient
timeouts across Playwright automations, HTTP requests, and pipeline tasks.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import logging
import os
import random
import socket
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

logger = logging.getLogger("NetworkResilience")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [NetworkResilience] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

T = TypeVar("T")

DEFAULT_RETRYABLE_EXCEPTIONS: Tuple[Type[BaseException], ...] = (
    TimeoutError,
    ConnectionResetError,
    ConnectionRefusedError,
    ConnectionAbortedError,
    socket.timeout,
    socket.gaierror,
    OSError,
)

try:
    from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError, TargetClosedError
    DEFAULT_RETRYABLE_EXCEPTIONS += (PlaywrightTimeoutError, TargetClosedError)
except ImportError:
    pass


def calculate_backoff(
    attempt: int,
    initial_backoff: float = 1.0,
    max_backoff: float = 30.0,
    factor: float = 2.0,
    jitter: bool = True,
) -> float:
    """Calculates exponential backoff with full randomized jitter to avoid collision storms."""
    exp = min(max_backoff, initial_backoff * (factor ** attempt))
    if jitter:
        return random.uniform(0.5 * exp, exp)
    return exp


def resilient_retry(
    max_retries: int = 5,
    initial_backoff: float = 1.0,
    max_backoff: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Optional[Tuple[Type[BaseException], ...]] = None,
    on_retry: Optional[Callable[[int, BaseException, float], Any]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Universal decorator for sync and async functions to continue seamlessly across network drops."""
    exceptions = retryable_exceptions or DEFAULT_RETRYABLE_EXCEPTIONS

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc: Optional[BaseException] = None
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as exc:
                        last_exc = exc
                        if attempt >= max_retries:
                            logger.error(f"[{func.__name__}] Exhausted all {max_retries} retries. Raising: {exc}")
                            raise
                        delay = calculate_backoff(attempt, initial_backoff, max_backoff, backoff_factor)
                        logger.warning(
                            f"[{func.__name__}] Attempt {attempt + 1}/{max_retries} encountered {type(exc).__name__}: {exc}. "
                            f"Resuming after {delay:.2f}s..."
                        )
                        if on_retry:
                            try:
                                res = on_retry(attempt, exc, delay)
                                if inspect.isawaitable(res):
                                    await res
                            except Exception as hook_err:
                                logger.warning(f"on_retry hook failed: {hook_err}")
                        await asyncio.sleep(delay)
                raise last_exc or RuntimeError("Execution failed without explicit exception.")
            return async_wrapper  # type: ignore
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc: Optional[BaseException] = None
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as exc:
                        last_exc = exc
                        if attempt >= max_retries:
                            logger.error(f"[{func.__name__}] Exhausted all {max_retries} retries. Raising: {exc}")
                            raise
                        delay = calculate_backoff(attempt, initial_backoff, max_backoff, backoff_factor)
                        logger.warning(
                            f"[{func.__name__}] Attempt {attempt + 1}/{max_retries} encountered {type(exc).__name__}: {exc}. "
                            f"Resuming after {delay:.2f}s..."
                        )
                        if on_retry:
                            try:
                                on_retry(attempt, exc, delay)
                            except Exception as hook_err:
                                logger.warning(f"on_retry hook failed: {hook_err}")
                        time.sleep(delay)
                raise last_exc or RuntimeError("Execution failed without explicit exception.")
            return sync_wrapper  # type: ignore

    return decorator


async def resilient_action(
    action: Callable[[], Any],
    max_retries: int = 5,
    initial_backoff: float = 1.0,
    max_backoff: float = 20.0,
    retryable_exceptions: Optional[Tuple[Type[BaseException], ...]] = None,
    recovery_callback: Optional[Callable[[], Any]] = None,
) -> Any:
    """Executes a single async or sync action with automated recovery on network fluctuations."""
    exceptions = retryable_exceptions or DEFAULT_RETRYABLE_EXCEPTIONS
    last_exc: Optional[BaseException] = None

    for attempt in range(max_retries + 1):
        try:
            res = action()
            if inspect.isawaitable(res):
                return await res
            return res
        except exceptions as exc:
            last_exc = exc
            if attempt >= max_retries:
                logger.error(f"Action exhausted all {max_retries} retries: {exc}")
                raise
            delay = calculate_backoff(attempt, initial_backoff, max_backoff)
            logger.warning(f"Action interrupted by {type(exc).__name__}: {exc}. Recovering in {delay:.2f}s...")
            if recovery_callback:
                try:
                    rec = recovery_callback()
                    if inspect.isawaitable(rec):
                        await rec
                except Exception as rec_err:
                    logger.warning(f"Recovery callback failed: {rec_err}")
            await asyncio.sleep(delay)
    raise last_exc or RuntimeError("Action failed.")


class TaskCheckpointManager:
    """Saves atomic progress checkpoints to disk to ensure interrupted tasks resume seamlessly."""

    def __init__(self, checkpoint_file: Union[str, Path]):
        self.checkpoint_file = Path(checkpoint_file)
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.checkpoint_file.exists():
            try:
                return json.loads(self.checkpoint_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Corrupt checkpoint file {self.checkpoint_file}: {e}. Initializing fresh.")
        return {}

    def is_completed(self, step_name: str) -> bool:
        """Checks if a particular step has already been completed."""
        return self.state.get("steps", {}).get(step_name, {}).get("completed", False)

    def record_step(self, step_name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Atomically saves progress for a completed step."""
        if "steps" not in self.state:
            self.state["steps"] = {}
        self.state["steps"][step_name] = {
            "completed": True,
            "timestamp": time.time(),
            "data": data or {},
        }
        self.save()

    def save(self) -> None:
        """Flushes state to disk."""
        tmp = self.checkpoint_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        tmp.replace(self.checkpoint_file)

    def get_step_data(self, step_name: str) -> Optional[Dict[str, Any]]:
        return self.state.get("steps", {}).get(step_name, {}).get("data")
