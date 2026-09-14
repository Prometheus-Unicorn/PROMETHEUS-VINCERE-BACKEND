import json

r = json.load(open('docs/mini_run_studio/run_34832825076/render-receipt-gha_hakt_30s_pbd_1789381325/receipt_gha_hakt_30s_pbd_1789381325.json'))
chunks = r['fontManifest']['chunks']
for i, c in enumerate(chunks):
    txt = c.get('text', '')
    z = c.get('placement', {}).get('dominantZone')
    layers = c.get('layers', [])
    ws = [l.get('estimatedWidthPx', 0) for l in layers]
    print(f"Chunk {i} (index={c.get('chunkIndex')}): text='{txt}' est_w={ws} zone={z}")
