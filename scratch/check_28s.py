import sys
sys.path.insert(0, '.')
import json
from mini_run_pipeline.policy_check import measure_pixel_row_projection_lines

receipt = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
c24 = [c for c in receipt.get('chunks', []) if c.get('chunkIndex') == 24][0]
print(f"Chunk 24: \"{c24.get('text')}\", startMs={c24.get('startMs')}, endMs={c24.get('endMs')}")
print("Placement:", c24.get('placement'))
for l in c24.get('layers', []):
    print("   layer:", l.get('layerName'), "text:", l.get('rawText'), "preset:", l.get('fxPreset'), "isHero:", l.get('isHero'), "behind:", l.get('behindSubject'))

meas = measure_pixel_row_projection_lines('scratch/r18_inspections/frame_28.00s.png', placement=c24.get('placement'), layers=c24.get('layers'))
print("Measurement on frame 28.0s:", meas)
