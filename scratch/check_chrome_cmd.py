import subprocess

out = subprocess.check_output(
    ["wmic", "process", "where", "name='chrome.exe'", "get", "ProcessId,ParentProcessId,CommandLine", "/format:csv"],
    text=True
)
for line in out.strip().splitlines():
    if line.strip() and not line.startswith("Node"):
        print(line[:120])
