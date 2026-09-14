import json
from pathlib import Path
import cv2

receipt_path = Path('docs/mini_run_studio/flow_clips/curito_porsche_paper_editorial_flow_veo31_receipt.json')
with open(receipt_path, 'r') as f:
    data = json.load(f)

print('RECEIPT GROUND TRUTH VERIFICATION:')
for k, v in data.items():
    if k != 'promptGenome':
        print(f'  {k}: {v}')

video_path = Path(data['assetPath'])
assert video_path.exists(), 'Video file does not exist'
assert video_path.stat().st_size == data['fileSizeBytes'], 'File size mismatch'

cap = cv2.VideoCapture(str(video_path))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.release()

expected_res = data['resolution']
assert f"{w}x{h}" == expected_res, f"Resolution mismatch: {w}x{h} vs {expected_res}"
assert cnt == data['frameCount'], f"Frame count mismatch: {cnt} vs {data['frameCount']}"
print("\nDeterministic verification: ALL RECEIPT ASSERTIONS PASSED!")
