import os
import subprocess
import sys
import time
import urllib.request
import json

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_URL = "http://127.0.0.1:9222"

def is_cdp_ready():
    try:
        req = urllib.request.Request(f"{CDP_URL}/json/version", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("CDP Ready! Browser:", data.get("Browser"))
            return True
    except Exception:
        return False

def restart_chrome_with_cdp():
    print("Checking if CDP is already active...")
    if is_cdp_ready():
        return True

    print("Stopping existing Chrome processes to allow CDP port 9222 binding...")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(3)

    print("Launching Chrome with --remote-debugging-port=9222 and Profile 12...")
    cmd = [
        CHROME_PATH,
        "--remote-debugging-port=9222",
        '--profile-directory=Profile 12',
        "--restore-last-session",
    ]
    subprocess.Popen(cmd)

    print("Waiting for CDP server to initialize...")
    for i in range(15):
        time.sleep(1)
        if is_cdp_ready():
            return True
        print(f"Waiting ({i+1}/15)...")

    print("CDP failed to initialize within 15 seconds.")
    return False

if __name__ == "__main__":
    success = restart_chrome_with_cdp()
    print("Result:", "SUCCESS" if success else "FAILED")
    sys.exit(0 if success else 1)
