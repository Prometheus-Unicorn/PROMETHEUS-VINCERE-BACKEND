import sys
sys.path.insert(0, '.')
import json
import numpy as np
from PIL import Image

# Load receipt
receipt = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
layers = receipt.get('fontManifest', {}).get('chunks', [])
chunks = receipt.get('chunks', [])

frames = [
    {'timestampSec': t, 'framePath': f'scratch/r18_inspections/frame_{t:.2f}s.png'}
    for t in [1.8, 4.6, 8.6, 15.0, 22.5, 28.0]
]

# Load receipt
receipt = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
chunks = receipt.get('chunks', [])

frames = [
    {'timestampSec': t, 'framePath': f'scratch/r18_inspections/frame_{t:.2f}s.png'}
    for t in [1.8, 4.6, 8.6, 15.0, 22.5, 28.0]
]

# Test measure_frame_text_pixel_bounds on 22.5s with filtering
img = Image.open('scratch/r18_inspections/frame_22.50s.png').convert('RGB')
arr = np.array(img)
h, w = arr.shape[:2]
sub = arr[1316:1756, :]
r = sub[:, :, 0].astype(float)
g = sub[:, :, 1].astype(float)
b = sub[:, :, 2].astype(float)
lum = 0.299 * r + 0.587 * g + 0.114 * b
bright_text = lum > 115.0
cyan_text = (b > 125) & (g > 125) & (r < 110)
warm_text = (r > 160) & (g > 120) & (b < 80)
mask = bright_text | cyan_text | warm_text

col_counts = np.sum(mask, axis=0)
active_cols = np.where(col_counts >= 6)[0]
splits = np.where(np.diff(active_cols) > 35)[0]
segments = np.split(active_cols, splits + 1)
valid_segs = [s for s in segments if (s.max() - s.min() >= 50 and np.sum(col_counts[s]) >= 350)]
print("Valid segments count at 22.5s:", len(valid_segs))

# Test on 8.6s (real text)
img8 = Image.open('scratch/r18_inspections/frame_8.60s.png').convert('RGB')
arr8 = np.array(img8)
sub8 = arr8[1316:1756, :]
r8 = sub8[:, :, 0].astype(float)
g8 = sub8[:, :, 1].astype(float)
b8 = sub8[:, :, 2].astype(float)
lum8 = 0.299 * r8 + 0.587 * g8 + 0.114 * b8
mask8 = (lum8 > 115.0) | ((b8 > 125) & (g8 > 125) & (r8 < 110)) | ((r8 > 160) & (g8 > 120) & (b8 < 80))
cols8 = np.sum(mask8, axis=0)
act8 = np.where(cols8 >= 6)[0]
sp8 = np.where(np.diff(act8) > 35)[0]
segs8 = np.split(act8, sp8 + 1)
vsegs8 = [s for s in segs8 if (s.max() - s.min() >= 50 and np.sum(cols8[s]) >= 350)]
print("Valid segments count at 8.6s (real text):", len(vsegs8), "best width:", (vsegs8[0].max() - vsegs8[0].min()) if vsegs8 else 0)

