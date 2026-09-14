import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from mini_run_pipeline.pipeline import resolve_chunk_zone

with open('output/gha_hakt_30s_pbd_1789257491_receipt.json', 'r') as f:
    receipt = json.load(f)

chunks = receipt['chunks']
for i in range(len(chunks) - 1):
    c1 = chunks[i]
    c2 = chunks[i+1]
    z1 = resolve_chunk_zone(c1)
    z2 = resolve_chunk_zone(c2)
    s1 = c1.get('startMs')
    e1 = c1.get('displayEndMs')
    s2 = c2.get('startMs')
    coll = max(0, e1 - s2)
    same = bool(z1 and z2 and z1 == z2)
    if same and coll > 0:
        trunc_end = max(s1, s2 - 30)
        new_coll = max(0, trunc_end - s2)
        print(f"Chunk {c1['chunkIndex']} -> {c2['chunkIndex']}: zone={z1}, old_coll={coll}ms, old_end={e1} -> trunc_end={trunc_end}, new_coll={new_coll}ms")
