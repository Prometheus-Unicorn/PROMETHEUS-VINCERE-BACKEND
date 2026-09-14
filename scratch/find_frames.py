import sys, os
sys.path.insert(0, '.')
import cv2
from mini_run_pipeline.policy_check import measure_frame_text_pixel_bounds

print("Searching for conformance frames...")
for root, dirs, files in os.walk('.'):
    if 'node_modules' in root or '.git' in root:
        continue
    for f in files:
        if 'frame_' in f and ('22' in f or 'conformance' in root):
            print(os.path.join(root, f))
