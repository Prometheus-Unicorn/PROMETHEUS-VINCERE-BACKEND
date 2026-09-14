import subprocess
import shutil
from pathlib import Path

master_mp4 = Path("C:/Users/HomePC/Downloads/PROMETHEUS-VINCERE-BACKEND/output/gha_hakt_30s_pbd_1789360183_master.mp4")
artifact_dir = Path("C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444")

timestamps = [
    (1.8, "r19_frame_1.8s_chunk1"),
    (7.2, "r19_frame_7.2s_chunk5_resold"),
    (9.8, "r19_frame_9.8s_chunk8_in_pure_profit"),
    (10.6, "r19_frame_10.6s_chunk8_exit_rack_focus"),
    (11.0, "r19_frame_11.0s_chunk9_best_part"),
    (15.0, "r19_frame_15.0s_chunk14_sunday_best"),
    (20.5, "r19_frame_20.5s_chunk18_right"),
    (24.5, "r19_frame_24.5s_chunk21_growing"),
    (27.8, "r19_frame_27.8s_chunk24_rainbows"),
]

for ts, name in timestamps:
    out_png = artifact_dir / f"{name}.png"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{ts:.3f}", "-i", str(master_mp4),
        "-vframes", "1", "-q:v", "2", str(out_png)
    ], check=True)
    print(f"Extracted {ts:.1f}s -> {out_png.name} ({out_png.stat().st_size / 1024:.1f} KB)")

print("\nAll forensic frames successfully extracted to artifact directory.")
