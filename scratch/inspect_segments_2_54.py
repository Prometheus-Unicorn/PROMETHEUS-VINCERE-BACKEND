import sys
sys.path.insert(0, '.')
import cv2
import numpy as np

img = cv2.imread('scratch/r20b_frame_2.54s.png')
b, g, r = cv2.split(img)
lum = 0.299 * r.astype(float) + 0.587 * g.astype(float) + 0.114 * b.astype(float)

bright_text = lum > 160.0
cyan_text = (b > 130) & (g > 130) & (r < 110)
warm_text = (r > 175) & (g > 130) & (b < 80)
mask = (bright_text | cyan_text | warm_text).astype(np.uint8) * 255

col_counts = np.sum(mask > 0, axis=0)
active_cols = np.where(col_counts >= 8)[0]
splits = np.where(np.diff(active_cols) > 16)[0]
segments = np.split(active_cols, splits + 1)

print("Active cols min:", active_cols.min() if len(active_cols) else None, "max:", active_cols.max() if len(active_cols) else None)
print(f"Total segments found: {len(segments)}")
for i, s in enumerate(segments):
    w = s.max() - s.min()
    density = np.sum(col_counts[s])
    print(f"Segment {i}: xMin={s.min()}, xMax={s.max()}, width={w}, density={density}")

cv2.imwrite('scratch/mask_2.54s.png', mask)
