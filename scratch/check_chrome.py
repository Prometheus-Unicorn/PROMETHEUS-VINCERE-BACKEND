import subprocess
import json

out = subprocess.check_output(
    ["powershell", "-Command", "Get-Process -Name chrome -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle | ConvertTo-Json"],
    text=True
)
try:
    data = json.loads(out)
    if isinstance(data, dict):
        data = [data]
    print(f"Total Chrome processes found: {len(data)}")
    for p in data:
        print(f"PID: {p.get('Id')} - Title: '{p.get('MainWindowTitle')}'")
except Exception as e:
    print(f"Error: {e}\nRaw: {out}")
