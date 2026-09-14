import json
from pathlib import Path
import cv2
import numpy as np

artifact_dir = Path("C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444")

frames = [
    "r19_frame_1.8s_chunk1.png",
    "r19_frame_10.2s_chunk8.png",
    "r19_frame_11.0s_chunk9_best_part.png",
    "r19_frame_16.2s_chunk14.png",
    "r19_frame_24.5s_chunk21_growing.png",
    "r19_frame_27.8s_chunk24_rainbows.png",
]

metrics = []

for fn in frames:
    fp = artifact_dir / fn
    if not fp.exists():
        continue
    img = cv2.imread(str(fp))
    h, w, c = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Shadow crush: fraction of pixels < 10
    shadow_crush_pct = float(np.mean(gray < 10)) * 100.0
    # Highlight clip: fraction of pixels > 245
    highlight_clip_pct = float(np.mean(gray > 245)) * 100.0
    
    # Mean luminance
    mean_lum = float(np.mean(gray))
    
    # Skin tone analysis: ROI around face (x: 35%-65%, y: 15%-45%)
    face_roi = img[int(h * 0.15):int(h * 0.45), int(w * 0.35):int(w * 0.65)]
    hsv_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
    # Standard skin tone range: Hue [5, 25], Sat [30, 200]
    skin_mask = (hsv_roi[:, :, 0] >= 5) & (hsv_roi[:, :, 0] <= 25) & (hsv_roi[:, :, 1] >= 30) & (hsv_roi[:, :, 1] <= 200)
    skin_pixels = hsv_roi[skin_mask]
    mean_skin_hue = float(np.mean(skin_pixels[:, 0])) if len(skin_pixels) > 0 else 0.0
    mean_skin_sat = float(np.mean(skin_pixels[:, 1])) if len(skin_pixels) > 0 else 0.0

    metrics.append({
        "frame": fn,
        "meanLuminance": round(mean_lum, 2),
        "shadowCrushPct": round(shadow_crush_pct, 2),
        "highlightClipPct": round(highlight_clip_pct, 2),
        "meanSkinHue": round(mean_skin_hue, 2),
        "meanSkinSat": round(mean_skin_sat, 2),
    })

print("=== FORENSIC COLOR & LUMINANCE METRICS ===")
for m in metrics:
    print(f"{m['frame']}: MeanLum={m['meanLuminance']}, ShadowCrush={m['shadowCrushPct']}%, HighlightClip={m['highlightClipPct']}%, SkinHue={m['meanSkinHue']} (ideal 12-18), SkinSat={m['meanSkinSat']}")

with open(artifact_dir / "r19_color_metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)
