import subprocess
import shutil
from pathlib import Path

brain_dir = Path(r"C:\Users\HomePC\.gemini\antigravity-cli\brain\8ec47dcb-d657-40d5-8c1c-7270878d6444")
for ts in [2.0, 20.5, 24.5, 27.8]:
    out = f"output/r10_frame_{ts}s.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ts), "-i", "output/master_r10_render.mp4", "-vframes", "1", "-q:v", "2", out], check=True)
    shutil.copy(out, brain_dir / f"r10_frame_{ts}s.png")
    print(f"Extracted {out}")
