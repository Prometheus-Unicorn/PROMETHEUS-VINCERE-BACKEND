import sys
sys.path.insert(0, '.')
import json
from mini_run_pipeline import subject_placement, policy_check

r = json.load(open('docs/mini_run_studio/run_34832825076/render-receipt-gha_hakt_30s_pbd_1789381325/receipt_gha_hakt_30s_pbd_1789381325.json'))
obs = json.load(open('scratch/saved_obs.json'))
chunks = r['fontManifest']['chunks']

placements = subject_placement.plan_subject_safe_placements(chunks, obs)
for i in range(len(chunks)):
    chunks[i]['placement'] = placements[i]
    if 'companionPlacement' in placements[i]:
        for l in chunks[i].get('layers', []):
            if l.get('behindSubject'):
                l['placement'] = placements[i]
            else:
                l['placement'] = placements[i]['companionPlacement']
    else:
        for l in chunks[i].get('layers', []):
            l['placement'] = placements[i]

rep_coll = policy_check.validate_caption_collisions(chunks)
print("validate_caption_collisions violations count:", len(rep_coll['violations']))
for v in rep_coll['violations']:
    print("  ", v)

# Also test head occlusion
all_layers = []
for c in chunks:
    all_layers.extend(c.get('layers', []))
rep_occ = policy_check.validate_head_occlusion(all_layers, chunks=chunks)
print("validate_head_occlusion status:", rep_occ['status'], "maxOcclusionFound:", rep_occ.get('maxOcclusionFound'))
for v in rep_occ['violations']:
    print("  ", v)
