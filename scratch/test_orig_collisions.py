import sys
sys.path.insert(0, '.')
import json
from mini_run_pipeline import subject_placement, policy_check

obs = subject_placement.observe_subject('remotion-app/public/source/test-video.mp4', 30000)
with open('scratch/saved_obs.json', 'w') as f:
    json.dump(obs, f, indent=2)

r = json.load(open('docs/mini_run_studio/run_34832825076/render-receipt-gha_hakt_30s_pbd_1789381325/receipt_gha_hakt_30s_pbd_1789381325.json'))
chunks = r['fontManifest']['chunks']

print(f"Original policy check on receipt fontManifest chunks:")
rep_orig = policy_check.validate_caption_collisions(chunks)
print(f"Original collisions violations: {len(rep_orig['violations'])}")
for v in rep_orig['violations']:
    print("  ", v)
