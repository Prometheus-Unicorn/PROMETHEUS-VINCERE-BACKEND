import sys
sys.path.insert(0, '.')
import json
from mini_run_pipeline import subject_placement, policy_check

r = json.load(open('docs/mini_run_studio/run_34832825076/render-receipt-gha_hakt_30s_pbd_1789381325/receipt_gha_hakt_30s_pbd_1789381325.json'))
obs = json.load(open('scratch/saved_obs.json'))

chunks = r['fontManifest']['chunks']

# Re-run plan_subject_safe_placements
placements = subject_placement.plan_subject_safe_placements(chunks, obs)

for i, (c, p) in enumerate(zip(chunks, placements)):
    print(f"Chunk {i} (index={c.get('chunkIndex')}): text='{c.get('text')}' -> zone={p.get('dominantZone')}, x={p.get('xPercent')}, y={p.get('yPercent')}")
