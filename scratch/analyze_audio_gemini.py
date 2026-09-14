import os
import sys
import json
import base64
import urllib.request
from pathlib import Path

sys.path.insert(0, ".")
from mini_run_pipeline import _load_env
_load_env()

key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_STUDIO_API_KEY")
if not key:
    print("No Gemini API key found.")
    sys.exit(1)

audio_path = Path("scratch/pilates_audio.mp3")
if not audio_path.exists():
    print("Audio file missing.")
    sys.exit(1)

audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("utf-8")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
payload = {
    "contents": [
        {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "audio/mp3",
                        "data": audio_b64
                    }
                },
                {
                    "text": (
                        "Analyze this 23.8-second video audio track. "
                        "1. Transcribe any spoken voice / dialogue with timestamps (start - end seconds). "
                        "2. If there is no speech, identify the genre, tempo (BPM), and rhythmic drops of the soundtrack. "
                        "Format output clearly."
                    )
                }
            ]
        }
    ]
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        text = res["candidates"][0]["content"]["parts"][0]["text"]
        print("GEMINI AUDIO ANALYSIS:")
        print(text)
        Path("scratch/audio_analysis.txt").write_text(text, encoding="utf-8")
except Exception as e:
    print(f"Error calling Gemini: {e}")
