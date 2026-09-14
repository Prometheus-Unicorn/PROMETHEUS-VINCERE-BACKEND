import shutil
import subprocess
from pathlib import Path

artifact_dir = Path(r"C:\Users\HomePC\.gemini\antigravity-cli\brain\8ec47dcb-d657-40d5-8c1c-7270878d6444")
output_dir = Path(r"C:\Users\HomePC\Downloads\PROMETHEUS-VINCERE-BACKEND\output")

job_id = "gha_hakt_30s_pbd_1789279473"
master_src = output_dir / f"{job_id}_master.mp4"
receipt_src = output_dir / f"{job_id}_receipt.json"

# 1. Copy receipt & master
master_dst = artifact_dir / "r16_final_master.mp4"
receipt_dst = artifact_dir / "r16_final_receipt.json"

print(f"Copying master to {master_dst}...")
shutil.copy2(master_src, master_dst)
print(f"Copying receipt to {receipt_dst}...")
shutil.copy2(receipt_src, receipt_dst)

# 2. Extract keyframes
timestamps = [
    (1.8, "r16_frame_1.8s_chunk1.png"),
    (4.6, "r16_frame_4.6s_chunk3_products.png"),
    (7.1, "r16_frame_7.1s_chunk5_resold_pivot.png"),
    (8.6, "r16_frame_8.6s_chunk7_six_figures.png"),
    (13.34, "r16_frame_13.34s_chunk12_home.png"),
    (15.0, "r16_frame_15.0s_chunk14_sunday_best.png"),
    (20.6, "r16_frame_20.6s_chunk18_right_pivot.png"),
    (22.5, "r16_frame_22.5s_chunk19_well.png"),
    (24.6, "r16_frame_24.6s_chunk21_growing_pivot.png"),
    (28.0, "r16_frame_28.0s_chunk24_rainbows_pivot_wrap.png"),
]

for ts, fname in timestamps:
    out_path = artifact_dir / fname
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(ts),
        "-i", str(master_src),
        "-vframes", "1",
        "-q:v", "2",
        str(out_path),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Extracted {ts}s -> {fname} ({out_path.stat().st_size} bytes)")

print("All extractions complete!")
