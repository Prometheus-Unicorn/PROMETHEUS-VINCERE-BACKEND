import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from mini_run_pipeline.policy_check import measure_frame_text_pixel_bounds

frame_path = 'scratch/test_conformance_frames/frame_22.0s.png'
img = cv2.imread(frame_path)
print("Image shape:", img.shape)
res = measure_frame_text_pixel_bounds(frame_path)
print("measure_frame_text_pixel_bounds result:", res)
