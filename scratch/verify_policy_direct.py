import sys
sys.path.insert(0, '.')
import json
from mini_run_pipeline import policy_check

receipt = json.load(open('scratch/r18_artifacts/render-receipt-gha_hakt_30s_pbd_1789344864/receipt_gha_hakt_30s_pbd_1789344864.json', encoding='utf-8'))
layers = policy_check.extract_manifest_layers(receipt)
chunks = receipt.get('chunks', [])

frames = [
    {'timestampSec': t, 'framePath': f'scratch/r18_inspections/frame_{t:.2f}s.png'}
    for t in [1.8, 4.6, 8.6, 15.0, 22.5, 28.0]
]

safe = policy_check.validate_safe_region_bounds_with_frames(layers, frames=frames, chunks=chunks)
has_matte = bool(receipt.get('matteSrc'))
lines = policy_check.validate_line_count_and_wrap(layers, chunks=chunks, frames=frames, has_matte=has_matte)
look = policy_check.validate_look_conformance(receipt.get('look'))
shadow = policy_check.validate_shadow_glow_budget(layers)
head = policy_check.validate_head_occlusion(layers, chunks=chunks, frames=frames)
cranial = policy_check.validate_cranial_halo_guard(layers, chunks=chunks)
caption = policy_check.validate_caption_collisions(chunks)

print(f"Safe bounds: {safe.get('status')} (violations: {len(safe.get('violations', []))})")
for v in safe.get('violations', []):
    print("  -", v)

print(f"Line count: {lines.get('status')} (violations: {len(lines.get('violations', []))})")
for v in lines.get('violations', []):
    print("  -", v)

print(f"Look conformance: {look.get('status')} (violations: {len(look.get('violations', []))})")
for v in look.get('violations', []):
    print("  -", v)

print(f"Shadow budget: {shadow.get('status')}")
print(f"Head occlusion: {head.get('status')}")
print(f"Cranial halo guard: {cranial.get('status')}")
print(f"Caption collision: {caption.get('status')}")

all_violations = (
    safe["violations"]
    + lines["violations"]
    + shadow["violations"]
    + look["violations"]
    + head["violations"]
    + caption["violations"]
    + cranial["violations"]
)
print("TOTAL VIOLATIONS:", len(all_violations))
