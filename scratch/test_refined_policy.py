import sys
sys.path.insert(0, '.')
import json
import numpy as np
from PIL import Image

r = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
chunks = r.get('chunks', [])

def match_chunk(ts, chunks):
    candidates = []
    for c in chunks:
        start_sec = float(c.get("startMs", 0)) / 1000.0
        end_sec = float(c.get("endMs", 0)) / 1000.0
        if start_sec <= ts <= end_sec:
            candidates.append((0, abs(ts - (start_sec + end_sec) / 2.0), c))
        elif (start_sec - 0.15) <= ts <= (end_sec + 0.15):
            candidates.append((1, abs(ts - (start_sec + end_sec) / 2.0), c))
    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]
    return None

print("Matched at 15.0s:", match_chunk(15.0, chunks).get('chunkIndex'), match_chunk(15.0, chunks).get('text'))
print("Matched at 22.5s:", match_chunk(22.5, chunks).get('chunkIndex'), match_chunk(22.5, chunks).get('text'))
