import json
r = json.load(open('output/r10_receipt.json'))
for i in [1, 3, 18, 21, 24]:
    c = r['chunks'][i]
    print(f"Chunk {i}: text='{c.get('text')}', startMs={c.get('outputStartMs')}, endMs={c.get('outputEndMs')}, behindSubj={c.get('behindSubject')}")
