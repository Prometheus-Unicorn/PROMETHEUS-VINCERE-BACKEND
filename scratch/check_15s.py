import sys
sys.path.insert(0, '.')
import json
import cv2
import numpy as np

r = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
for c in r.get('chunks', []):
    s = float(c.get('startMs', 0)) / 1000.0
    e = float(c.get('endMs', 0)) / 1000.0
    if s <= 15.0 <= e + 0.15:
        print(f"Chunk {c.get('chunkIndex')}: \"{c.get('text')}\", startMs={c.get('startMs')}, endMs={c.get('endMs')}")
        print("placement:", c.get('placement'))
        for l in c.get('layers', []):
            print("   layer:", l.get('layerName'), "text:", l.get('rawText'), "preset:", l.get('fxPreset'))

from mini_run_pipeline.policy_check import measure_pixel_row_projection_lines
f_path = 'scratch/r18_inspections/frame_15.00s.png'
meas = measure_pixel_row_projection_lines(f_path)
print("measure_pixel_row_projection_lines (default):", meas)

# Check with chunk's placement
c13 = [c for c in r.get('chunks', []) if c.get('chunkIndex') == 13][0]
p = c13.get('placement')
meas_p = measure_pixel_row_projection_lines(f_path, placement=p, layers=c13.get('layers'))
print("measure_pixel_row_projection_lines (with placement):", meas_p)
