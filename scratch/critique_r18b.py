import cv2
import numpy as np
from pathlib import Path

source_path = Path('remotion-app/public/source/test-video.mp4')
master_path = list(Path('scratch/r18b_artifacts/render-master-gha_hakt_30s_pbd_1789347145').glob('*.mp4'))[0]

cap_src = cv2.VideoCapture(str(source_path))
cap_master = cv2.VideoCapture(str(master_path))

timestamps = [1.8, 4.6, 7.1, 8.6, 15.0, 22.5, 28.0]

print("=" * 80)
print(f"OUTPUT CRITIQUE AUDIT: MASTER RENDER ({master_path.name})")
print(f"File Size: {master_path.stat().st_size / (1024*1024):.2f} MB")
print("=" * 80)

for ts in timestamps:
    ms = int(ts * 1000)
    cap_src.set(cv2.CAP_PROP_POS_MSEC, ms)
    ret_src, f_src = cap_src.read()
    
    cap_master.set(cv2.CAP_PROP_POS_MSEC, ms)
    ret_mst, f_mst = cap_master.read()
    
    if not ret_src or not ret_mst:
        print(f"Could not read frames at {ts}s")
        continue
    
    # 9:16 Center Cover Crop of Raw Source for 1:1 geometry parity
    sh, sw = f_src.shape[:2]
    crop_w = int(sh * 9.0 / 16.0)
    x0 = (sw - crop_w) // 2
    f_src_crop = f_src[:, x0:x0+crop_w]
    f_src_916 = cv2.resize(f_src_crop, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
    
    lum_src = 0.299 * f_src_916[:,:,2] + 0.587 * f_src_916[:,:,1] + 0.114 * f_src_916[:,:,0]
    lum_mst = 0.299 * f_mst[:,:,2] + 0.587 * f_mst[:,:,1] + 0.114 * f_mst[:,:,0]
    
    src_clip10 = float(np.mean(lum_src < 10.0) * 100.0)
    mst_clip10 = float(np.mean(lum_mst < 10.0) * 100.0)
    
    src_clip5 = float(np.mean(lum_src < 5.0) * 100.0)
    mst_clip5 = float(np.mean(lum_mst < 5.0) * 100.0)
    
    mean_src = float(np.mean(lum_src))
    mean_mst = float(np.mean(lum_mst))
    lum_delta = abs(mean_mst - mean_src)
    
    # Skin tone probe in center third
    h, w = f_mst.shape[:2]
    face_src = f_src_916[int(h*0.25):int(h*0.48), int(w*0.35):int(w*0.65)]
    face_mst = f_mst[int(h*0.25):int(h*0.48), int(w*0.35):int(w*0.65)]
    hsv_src = cv2.cvtColor(face_src, cv2.COLOR_BGR2HSV)
    hsv_mst = cv2.cvtColor(face_mst, cv2.COLOR_BGR2HSV)
    
    skin_src_hue = float(np.mean(hsv_src[:,:,0]) * 2.0)
    skin_mst_hue = float(np.mean(hsv_mst[:,:,0]) * 2.0)
    skin_delta = abs(skin_mst_hue - skin_src_hue)
    
    print(f"Timestamp {ts:4.1f}s | Lum: Src={mean_src:5.1f}, Mst={mean_mst:5.1f} (Delta={lum_delta:4.1f}) | PitchBlack(<5): {mst_clip5:4.2f}% | SkinHue: Src={skin_src_hue:4.1f}°, Mst={skin_mst_hue:4.1f}° (Delta={skin_delta:4.1f}°)")

cap_src.release()
cap_master.release()
