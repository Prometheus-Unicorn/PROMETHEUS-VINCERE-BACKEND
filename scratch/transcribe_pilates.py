import os
import json
import urllib.request
from pathlib import Path

import sys
sys.path.insert(0, ".")
from mini_run_pipeline import _load_env
_load_env()

key = os.getenv("GROQ_API_KEY") or os.getenv("ASSEMBLYAI_API_KEY")

if not key:
    print("GROQ_API_KEY not found!")
    exit(1)

fbytes = open("scratch/pilates_audio.mp3", "rb").read()
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

parts = []
# file part
parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"audio.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode("utf-8"))
parts.append(fbytes)
parts.append(b"\r\n")

# model part
parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-large-v3\r\n".encode("utf-8"))

# response_format part
parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\nverbose_json\r\n".encode("utf-8"))

parts.append(f"--{boundary}--\r\n".encode("utf-8"))

body = b"".join(parts)

req = urllib.request.Request(
    "https://api.groq.com/openai/v1/audio/transcriptions",
    data=body,
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    },
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("TRANSCRIPT:")
        print(data.get("text", ""))
        Path("scratch/pilates_transcript.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
except Exception as e:
    print(f"Error transcribing: {e}")
