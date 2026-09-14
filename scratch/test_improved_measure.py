import sys
sys.path.insert(0, '.')
import cv2
import numpy as np

def test_measurement(frame_path, expected_x=540.0, expected_y=None, safe_margin_x=130.0):
    img = cv2.imread(frame_path)
    h, w = img.shape[:2]

    if expected_y is not None:
        y_start = max(50, int(expected_y - 220))
        y_end = min(h - 50, int(expected_y + 220))
    else:
        y_start = min(h - 50, 500)
        y_end = min(h, 1850)
    sub = img[y_start:y_end, :]

    b = sub[:, :, 0].astype(float)
    g = sub[:, :, 1].astype(float)
    r = sub[:, :, 2].astype(float)
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    bright_text = lum > 160.0
    cyan_text = (b > 130) & (g > 130) & (r < 110)
    warm_text = (r > 175) & (g > 130) & (b < 80)
    mask = bright_text | cyan_text | warm_text

    col_counts = np.sum(mask, axis=0)
    active_cols = np.where(col_counts >= 8)[0]
    if len(active_cols) == 0:
        return {"status": "passed", "detected": False, "edgeBleed": False}

    # Use 48px gap to keep adjacent words within the same line together
    splits = np.where(np.diff(active_cols) > 48)[0]
    segments = np.split(active_cols, splits + 1)
    valid_segs = [s for s in segments if (s.max() - s.min() >= 40 and np.sum(col_counts[s]) >= 250)]
    if not valid_segs:
        return {"status": "passed", "detected": False, "edgeBleed": False}

    # If expected_x is provided, pick the valid segment cluster closest to expected_x
    if expected_x is not None:
        best_seg = min(valid_segs, key=lambda s: abs((s.min() + s.max()) / 2.0 - expected_x))
    else:
        best_seg = max(valid_segs, key=lambda s: np.sum(col_counts[s]))

    x_min = int(best_seg.min())
    x_max = int(best_seg.max())

    left_c = float(x_min)
    right_c = float(w - x_max)
    has_left_bleed = left_c < (safe_margin_x - 1.0)
    has_right_bleed = right_c < (safe_margin_x - 1.0)
    edge_bleed = has_left_bleed or has_right_bleed

    return {
        "status": "passed" if not edge_bleed else "failed",
        "detected": True,
        "bbox": {"xMin": x_min, "xMax": x_max},
        "leftClearancePx": left_c,
        "rightClearancePx": right_c,
        "edgeBleed": edge_bleed,
        "bleedSide": "both" if (has_left_bleed and has_right_bleed) else ("left" if has_left_bleed else ("right" if has_right_bleed else "none"))
    }

print("Frame 22.01s:", test_measurement('scratch/r20b_frame_22.01s.png', expected_x=540.0, expected_y=1138.0))
print("Frame 2.54s:", test_measurement('scratch/r20b_frame_2.54s.png', expected_x=540.0, expected_y=1038.0))
