import sys
sys.path.insert(0, '.')
import cv2
import numpy as np

for t, expected_x in [(2.54, 540), (22.01, 540)]:
    frame_path = f'scratch/r20b_frame_{t:.2f}s.png'
    img = cv2.imread(frame_path)
    h, w = img.shape[:2]
    
    # Text region mask
    b, g, r = cv2.split(img)
    lum = 0.299 * r.astype(float) + 0.587 * g.astype(float) + 0.114 * b.astype(float)
    bright_text = lum > 160.0
    cyan_text = (b > 130) & (g > 130) & (r < 110)
    warm_text = (r > 175) & (g > 130) & (b < 80)
    mask = bright_text | cyan_text | warm_text

    # Let's inspect connected components or column clustering
    col_counts = np.sum(mask[int(h*0.4):int(h*0.8), :] > 0, axis=0)
    active_cols = np.where(col_counts >= 8)[0]
    
    # Word gap in caption typography can be up to 48px
    splits = np.where(np.diff(active_cols) > 48)[0]
    segments = np.split(active_cols, splits + 1)
    
    print(f"=== Frame at {t}s (expected_x={expected_x}) ===")
    for i, s in enumerate(segments):
        s_min, s_max = s.min(), s.max()
        s_w = s_max - s_min
        s_mid = (s_min + s_max) / 2.0
        dist_to_expected = abs(s_mid - expected_x)
        density = np.sum(col_counts[s])
        print(f"  Cluster {i}: x=[{s_min}, {s_max}], width={s_w}, mid={s_mid:.1f}, dist={dist_to_expected:.1f}, density={density}")
