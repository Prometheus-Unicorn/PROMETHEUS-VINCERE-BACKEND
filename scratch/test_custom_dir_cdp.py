import os
import subprocess
import time
import urllib.request
import json

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
AUTO_DIR = r"C:\Users\HomePC\AppData\Local\Google\Chrome\AutomationData"
os.makedirs(AUTO_DIR, exist_ok=True)

subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
time.sleep(2)

cmd = [
    CHROME_PATH,
    "--remote-debugging-port=9222",
    f"--user-data-dir={AUTO_DIR}",
    "--headless=new",
]
p = subprocess.Popen(cmd)
time.sleep(3)

try:
    with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=3) as resp:
        print("Success! CDP Response:", resp.read().decode())
finally:
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
