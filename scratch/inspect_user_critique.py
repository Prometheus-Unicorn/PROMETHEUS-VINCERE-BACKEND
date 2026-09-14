import json

rc = json.loads(open('output/gha_hakt_30s_pbd_1789349837_receipt.json').read())
chunks = rc.get('chunks', [])
for i, c in enumerate(chunks):
    txt = c.get('text', '')
    if any(k in txt.lower() for k in ['profit', 'best', 'point', 'growing', 'transparent']):
        print(f'=== CHUNK {i} (chunkIndex={c.get("chunkIndex")}) ===')
        print(f'Text: "{txt}"')
        print(f'StartMs: {c.get("startMs")} | EndMs: {c.get("endMs")}')
        print(f'Placement: {c.get("placement")}')
        for l in c.get('layers', []):
            print(f'  Layer {l.get("layerIndex")}: text="{l.get("text")}" | role={l.get("role")} | font={l.get("fontFamily")} | size={l.get("fontSizePx")} | behind={l.get("behindSubject")} | fx={l.get("fxPreset")} | exit={l.get("exitTreatment")}')
            print(f'    Words: {[(w.get("text"), w.get("start_ms"), w.get("end_ms")) for w in l.get("words", [])]}')
