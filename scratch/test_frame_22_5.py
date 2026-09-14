import sys
sys.path.insert(0, '.')
import cv2
from mini_run_pipeline.policy_check import measure_frame_text_pixel_bounds

# Extract or test frame at 22.5s from old master
cap = cv2.VideoCapture('docs/mini_run_studio/run_34832825076/render-master-gha_hakt_30s_pbd_1789381325/master_gha_hakt_30s_pbd_1789381325.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
target_frame = int(round(22.5 * fps))
cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
ret, frame = cap.read()
cap.release()

if ret:
    cv2.imwrite('scratch/test_frame_22.5s.png', frame)
    res = measure_frame_text_pixel_bounds('scratch/test_frame_22.5s.png')
    print("measure_frame_text_pixel_bounds at 22.5s:", res)
else:
    print("Could not read frame at 22.5s")
