import sys
sys.path.insert(0, '.')
import json
import numpy as np
from PIL import Image

r = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
c14 = [c for c in r.get('chunks', []) if c.get('chunkIndex') == 14][0]

arr = np.array(Image.open('scratch/r18_inspections/frame_15.00s.png').convert('RGB'))
h, w = arr.shape[:2]
p = c14.get('placement', {})
raw_x = str(p.get("xPercent", "50%")).replace("%", "")
x_pct = float(raw_x) / 100.0 if float(raw_x) > 1.0 else float(raw_x)
raw_y = str(p.get("yPercent", "80%")).replace("%", "")
y_pct = float(raw_y) / 100.0 if float(raw_y) > 1.0 else float(raw_y)
raw_mw = str(p.get("maxWidthPercent", "85%")).replace("%", "")
mw_pct = float(raw_mw) / 100.0 if float(raw_mw) > 1.0 else float(raw_mw)

center_x = x_pct * w
center_y = y_pct * h
box_w = min(float(w), max(350.0, mw_pct * float(w) + 60.0))
layers = c14.get('layers', [])
font_sizes = [float(l.get("fontSizePx") or l.get("font_size_px") or 60.0) for l in layers]
est_h = sum(font_sizes) * 1.5 + 40.0 if font_sizes else 260.0
box_h = max(180.0, min(500.0, est_h))

x0 = max(0, int(center_x - box_w / 2.0))
x1 = min(w, int(center_x + box_w / 2.0))
y0 = max(0, int(center_y - box_h / 2.0))
y1 = min(h, int(center_y + box_h / 2.0))

crop = arr[y0:y1, x0:x1]
r_c = crop[:, :, 0].astype(float)
g_c = crop[:, :, 1].astype(float)
b_c = crop[:, :, 2].astype(float)
lum = 0.299 * r_c + 0.587 * g_c + 0.114 * b_c

bright_text = lum > 115.0
colored_text = ((np.maximum(np.maximum(r_c, g_c), b_c) - np.minimum(np.minimum(r_c, g_c), b_c)) > 35) & (lum > 70.0)
mask = bright_text | colored_text

row_counts = np.sum(mask, axis=1)
min_row_px = max(20, int((x1 - x0) * 0.04))
active_rows = np.where(row_counts >= min_row_px)[0]
splits = np.where(np.diff(active_rows) > 12)[0]
raw_bands = np.split(active_rows, splits + 1)
for i, b in enumerate(raw_bands):
    print(f"Band {i}: len={len(b)}, maxRowPx={np.max(row_counts[b])}")
