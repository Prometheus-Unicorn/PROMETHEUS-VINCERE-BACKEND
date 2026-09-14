import cv2

video_path = 'docs/mini_run_studio/run_34837285119/render-master-gha_hakt_30s_pbd_1789384516/master_gha_hakt_30s_pbd_1789384516.mp4'
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

for t in [2.54, 22.01]:
    target_frame = int(round(t * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()
    if ret:
        out_path = f'scratch/r20b_frame_{t:.2f}s.png'
        cv2.imwrite(out_path, frame)
        print(f"Extracted {out_path} at {t}s (frame {target_frame})")

cap.release()
