import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from mini_run_pipeline.subject_placement import plan_subject_safe_placements

with open('output/gha_hakt_30s_pbd_1789257491_receipt.json', 'r') as f:
    receipt = json.load(f)

chunks = receipt['chunks']
obs = receipt.get('subjectObservation')

placements = plan_subject_safe_placements(chunks, obs)

print("=== CHECKING NON-PIVOT LAYER Y-DELTAS ===")
prev_non_pivot_y = None
max_delta = 0.0

for idx, (c, p) in enumerate(zip(chunks, placements)):
    layers = c.get('layers', [])
    for l in layers:
        is_pivot = bool(l.get('behindSubject'))
        if not is_pivot:
            # Non-pivot layer position
            layer_p = l.get('placement') or p
            if bool(c.get('subjectLayering', {}).get('behindSubject')) and not is_pivot:
                # Companion layer in a pivot chunk
                layer_p = p.get('companionPlacement') or layer_p
            
            y_str = layer_p.get('yPercent', '80%')
            y_val = float(str(y_str).replace('%', ''))
            
            if prev_non_pivot_y is not None:
                dy = abs(y_val - prev_non_pivot_y)
                if dy > max_delta:
                    max_delta = dy
                print(f"Chunk {c.get('chunkIndex')} non-pivot '{l.get('text')}': y={y_val}% (dy={dy:.1f}%)")
            else:
                print(f"Chunk {c.get('chunkIndex')} non-pivot '{l.get('text')}': y={y_val}% (initial)")
            prev_non_pivot_y = y_val

print(f"\nMAX NON-PIVOT Y-DELTA: {max_delta:.2f}% (Acceptance: <= 15.0%)")
