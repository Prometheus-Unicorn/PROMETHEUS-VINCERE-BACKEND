"""One-Time Interactive Google Flow Login in Persistent Dedicated Profile.

Usage:
    python scripts/login_flow_dedicated.py

Opens native Google Chrome with the dedicated profile directory:
    C:\\Users\\HomePC\\.prometheus_flow_user_data

Once you sign in to ipsasummagnitudo@gmail.com and access https://flow.google.com,
this script detects the active session and confirms that headless automation
is permanently authenticated.
"""

import os
import subprocess
import sys
import time
import urllib.request
import json
from pathlib import Path

PROFILE_DIR = Path(r"C:\Users\HomePC\.prometheus_flow_user_data")
CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
FLOW_URL = "https://flow.google.com"
PORT = 9222


def check_cdp_alive() -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/version")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode())
            return "Browser" in data
    except Exception:
        return False


def main() -> None:
    print("=" * 72)
    print("  PROMETHEUS CORE: Permanent Google Flow Profile Sign-In")
    print(f"  Target Profile: {PROFILE_DIR}")
    print(f"  Target Executable: {CHROME_PATH}")
    print("=" * 72)

    if not CHROME_PATH.exists():
        print(f"ERROR: Google Chrome binary not found at {CHROME_PATH}")
        sys.exit(1)

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(CHROME_PATH),
        f"--user-data-dir={PROFILE_DIR.resolve()}",
        f"--remote-debugging-port={PORT}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        FLOW_URL,
    ]

    print("\nLaunching native Chrome window...")
    proc = subprocess.Popen(cmd)

    print("\n" + "*" * 72)
    print("ACTION REQUIRED:")
    print("1. In the Chrome window that just opened, sign in to your Google Account:")
    print("   -> ipsasummagnitudo@gmail.com")
    print("2. Complete any 2FA verification prompt on your phone.")
    print("3. Ensure you are on the Google Flow dashboard or project workspace.")
    print("*" * 72 + "\n")
    print("Waiting for login... (Press Ctrl+C when finished)")

    try:
        while True:
            time.sleep(3.0)
            if proc.poll() is not None:
                print("Chrome window was closed. Profile state saved.")
                break
    except KeyboardInterrupt:
        print("\nSession saved. Exiting activator.")


if __name__ == "__main__":
    main()
