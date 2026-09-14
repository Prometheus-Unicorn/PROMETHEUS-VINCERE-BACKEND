import os
import subprocess
import time
import urllib.request
import json

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\Users\HomePC\AppData\Local\Google\Chrome\User Data"

subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
time.sleep(2)

cmd = [
    CHROME_PATH,
    "--remote-debugging-port=9222",
    f"--user-data-dir={USER_DATA_DIR}",
    "--profile-directory=Profile 12",
]
p = subprocess.Popen(cmd)
time.sleep(3)

try:
    with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=2) as resp:
        print("Success with --user-data-dir! Response:", resp.read().decode())
except Exception as e:
    print("Failed with --user-data-dir:", e)
