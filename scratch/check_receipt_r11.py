import json

with open("output/gha_hakt_30s_r11_1789168294_receipt.json", "r", encoding="utf-8") as f:
    r = json.load(f)

manifest = r.get("fontManifest", {})
chunks = manifest.get("chunks", [])

print(f"Total chunks in manifest: {len(chunks)}")
print(f"{'Chunk':<6} | {'Text':<30} | {'Start':<6} | {'LastWordEnd':<11} | {'DisplayEnd':<10} | {'Hold_ms':<10}")
print("-" * 85)

negative_holds = 0
holds = []
for c in chunks:
    idx = c.get("chunkIndex")
    text = c.get("text", "")[:28]
    start = c.get("startMs", c.get("outputStartMs", 0))
    disp_end = c.get("displayEndMs", c.get("endMs", 0))
    words = c.get("words", [])
    word_ends = [w.get("end_ms", 0) for w in words if w.get("end_ms")]
    last_word_end = max(word_ends) if word_ends else c.get("endMs", disp_end)
    hold = disp_end - last_word_end
    holds.append(hold)
    if hold < 0:
        negative_holds += 1
    print(f"{idx:<6} | {text:<30} | {start:<6} | {last_word_end:<11} | {disp_end:<10} | {hold:<10}")

print("=" * 85)
print(f"Negative holds count: {negative_holds}")
print(f"Min hold: {min(holds)}ms | Median hold: {sorted(holds)[len(holds)//2]}ms | Max hold: {max(holds)}ms")
