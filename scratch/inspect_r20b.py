import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from mini_run_pipeline.policy_check import measure_frame_text_pixel_bounds

for t in [2.54, 22.01]:
    frame_path = f'scratch/r20b_frame_{t:.2f}s.png'
    res = measure_frame_text_pixel_bounds(frame_path)
    print(f"--- Frame at {t}s ---")
    print(res)

    # Let's inspect the bounding box area
    img = cv2.imread(frame_path)
    bbox = res.get('bbox')
    if bbox:
        crop = img[bbox['yMin']:bbox['yMax'], bbox['xMin']:bbox['xMax']]
        cv2.imwrite(f'scratch/r20b_crop_{t:.2f}s.png', crop)
        print(f"Crop saved to scratch/r20b_crop_{t:.2f}s.png (shape={crop.shape})")
