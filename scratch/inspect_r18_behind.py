import json

with open('C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444/r18_final_receipt.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

for i, c in enumerate(r.get('chunks', [])):
    p = c.get('placement', {})
    layers = c.get('layers', [])
    behind_layers = [l for l in layers if l.get('behindSubject')]
    if behind_layers:
        pivots = [l.get('rawText') for l in behind_layers]
        print(f"Chunk {i+1:02d}: text='{c.get('text')}' | pivots={pivots} | yPercent={p.get('yPercent')} | anchor={p.get('anchor')} | dominantZone={p.get('dominantZone')}")
