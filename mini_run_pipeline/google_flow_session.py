"""Google Flow Long-Lived Session Persistence & Token Synchronization Manager.

Architecture:
1. Persistent User Profile: Maintains a dedicated Playwright persistent context
   directory (`config/flow_browser_profile/` or system `AutomationData`).
2. Live Token Synchronization: Intercepts and records session rotation tokens
   (`__Secure-1PSIDTS`, `__Secure-3PSIDTS`, `SIDCC`, `OSID`) whenever Google
   authenticates or rotates credentials.
3. Automated Keep-Alive Heartbeat: Periodically pings Google Flow endpoints
   (every 15 minutes) to trigger background token refresh and prevent session expiration.
4. Fail-Fast Health Probing: Probes session validity directly without synthetic fallbacks.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page, async_playwright

logger = logging.getLogger("google_flow_session")

DEFAULT_PROFILE_DIR = Path("config/flow_browser_profile")
DEFAULT_AUTH_JSON = Path("config/flow_auth.json")
BACKUP_AUTH_JSON = Path("config/flow_auth_synced.json")
FLOW_ROOT_URL = "https://flow.google.com"
FLOW_ABOUT_URL = "https://flow.google.com/about"

# Security cookies requiring persistent freshness
CRITICAL_SESSION_COOKIES = (
    "__Secure-1PSIDTS",
    "__Secure-3PSIDTS",
    "SID",
    "__Secure-1PSID",
    "__Secure-3PSID",
    "OSID",
    "__Secure-OSID",
)


class GoogleFlowSessionManager:
    """Manages persistent browser contexts, token lifecycle, and session keep-alives."""

    def __init__(
        self,
        profile_dir: Path = DEFAULT_PROFILE_DIR,
        auth_json_path: Path = DEFAULT_AUTH_JSON,
        heartbeat_interval_sec: int = 900,  # 15 minutes
    ):
        self.profile_dir = Path(profile_dir)
        self.auth_json_path = Path(auth_json_path)
        self.heartbeat_interval_sec = heartbeat_interval_sec
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load_stored_cookies(cls, json_path: Path = DEFAULT_AUTH_JSON) -> List[Dict[str, Any]]:
        """Load stored cookies from JSON file if it exists."""
        if not json_path.exists():
            return []
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "cookies" in data:
                return data["cookies"]
        except Exception as e:
            logger.warning(f"Failed to read cookies from {json_path}: {e}")
        return []

    @classmethod
    def save_stored_cookies(cls, cookies: List[Dict[str, Any]], json_path: Path = DEFAULT_AUTH_JSON) -> None:
        """Atomically persist active cookies to disk."""
        json_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = json_path.with_suffix(".tmp")
        payload = {"cookies": cookies, "origins": [], "last_synced_utc": time.time()}
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        temp_path.replace(json_path)

    async def sync_context_cookies(self, context: BrowserContext) -> List[Dict[str, Any]]:
        """Extract live cookies from BrowserContext and update local storage files."""
        live_cookies = await context.cookies()
        if not live_cookies:
            return []

        # Filter for Google & Flow cookies
        google_cookies = [
            c for c in live_cookies
            if "google.com" in c.get("domain", "") or "flow.google" in c.get("domain", "")
        ]

        if google_cookies:
            self.save_stored_cookies(google_cookies, self.auth_json_path)
            self.save_stored_cookies(google_cookies, BACKUP_AUTH_JSON)
            ts_cookie = next((c for c in google_cookies if c.get("name") == "__Secure-1PSIDTS"), None)
            if ts_cookie:
                logger.info(f"Synchronized refreshed __Secure-1PSIDTS: {ts_cookie.get('value', '')[:20]}...")

        return google_cookies

    async def verify_session_health(self, page: Page) -> Dict[str, Any]:
        """Check whether the active page is authenticated to Google Flow."""
        url = page.url
        title = await page.title()
        is_signin_redirect = "accounts.google.com" in url or "ServiceLogin" in url
        is_landing_page = "flow.google.com/about" in url

        # Check for user avatar or create button on workspace
        has_workspace_nav = await page.query_selector("button:has-text('New project'), [aria-label*='account' i]") is not None
        has_create_btn = await page.query_selector("button:has-text('Create with Google Flow')") is not None

        is_authenticated = (not is_signin_redirect) and (has_workspace_nav or (not has_create_btn and "flow.google.com" in url))

        return {
            "url": url,
            "title": title,
            "authenticated": is_authenticated,
            "is_signin_redirect": is_signin_redirect,
            "is_landing_page": is_landing_page,
            "has_workspace_nav": has_workspace_nav,
        }

    async def run_heartbeat_ping(self, context: BrowserContext) -> bool:
        """Executes a non-intrusive background keep-alive ping to keep SIDTS token fresh."""
        page = await context.new_page()
        try:
            logger.info("Executing Google Flow heartbeat ping...")
            await page.goto(FLOW_ROOT_URL, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            health = await self.verify_session_health(page)
            await self.sync_context_cookies(context)
            logger.info(f"Heartbeat complete: authenticated={health['authenticated']}, url={health['url']}")
            return health["authenticated"]
        except Exception as e:
            logger.warning(f"Heartbeat ping encountered an exception: {e}")
            return False
        finally:
            await page.close()


async def launch_persistent_flow_context(
    profile_dir: Path = DEFAULT_PROFILE_DIR,
    headless: bool = True,
    seed_auth_json: Optional[Path] = DEFAULT_AUTH_JSON,
) -> BrowserContext:
    """Launch Playwright persistent context with full WebGL and security settings."""
    p = await async_playwright().start()
    launch_args = [
        "--enable-webgl",
        "--ignore-gpu-blocklist",
        "--enable-gpu-rasterization",
        "--use-gl=angle",
        "--use-angle=d3d11",
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
    ]

    context = await p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=headless,
        args=launch_args,
        viewport={"width": 1440, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        ),
    )

    # If persistent profile has no cookies yet, seed from auth JSON
    existing_cookies = await context.cookies()
    if not existing_cookies and seed_auth_json and seed_auth_json.exists():
        stored = GoogleFlowSessionManager.load_stored_cookies(seed_auth_json)
        if stored:
            await context.add_cookies(stored)

    return context
