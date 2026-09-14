import json
from pathlib import Path

with open('output/gha_hakt_30s_pbd_1789257491_receipt.json', 'r') as f:
    receipt = json.load(f)

for c in receipt.get('chunks', []):
    c_idx = c.get('chunkIndex')
    text = c.get('text')
    layers = c.get('layers', [])
    placement = c.get('placement', {})
    print(f"Chunk {c_idx}: '{text}' (start={c.get('startMs')}, end={c.get('displayEndMs')}, collision={c.get('collisionMs')}, exit={c.get('exitTreatment')})")
    print(f"   placement: domZone={placement.get('dominantZone')}, y={placement.get('yPercent')}, x={placement.get('xPercent')}")
    for l_idx, l in enumerate(layers):
        print(f"   layer {l_idx}: text='{l.get('text')}', font={l.get('fontFamily')}, size={l.get('fontSizePx')}, behind={l.get('behindSubject')}, isHero={l.get('isHero')}")
