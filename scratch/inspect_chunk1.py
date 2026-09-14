import json

r = json.load(open('docs/mini_run_studio/run_34837285119/render-receipt-gha_hakt_30s_pbd_1789384516/receipt_gha_hakt_30s_pbd_1789384516.json'))
c1 = r['fontManifest']['chunks'][1]
print("Chunk 1 text:", c1.get('text'))
print("Chunk 1 placement:", c1.get('placement'))
for l in c1.get('layers', []):
    print("  Layer:", l.get('rawText'), "fontFamily:", l.get('fontFamily'), "fontSizePx:", l.get('fontSizePx'), "est_width:", l.get('estimatedWidthPx') or l.get('est_width'))
