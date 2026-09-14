import subprocess
import time
import urllib.request
import json

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA = r"C:\Users\HomePC\AppData\Local\Google\Chrome\User Data"

# Kill all chrome
subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
time.sleep(2)

print("Starting Chrome with real User Data and Profile 12...")
cmd = [
    CHROME_PATH,
    "--remote-debugging-port=9222",
    f"--user-data-dir={USER_DATA}",
    '--profile-directory=Profile 12',
    "--remote-allow-origins=*",
]
p = subprocess.Popen(cmd)

for i in range(15):
    time.sleep(1)
    try:
        with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=1) as resp:
            print(f"CDP connected at sec {i+1}! Response: {resp.read().decode()[:100]}")
            break
    except Exception as e:
        print(f"Sec {i+1}: {e}")

subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
