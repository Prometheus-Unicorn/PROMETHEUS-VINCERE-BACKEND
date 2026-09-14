import json

with open("output/gha_hakt_30s_r11_1789168294_receipt.json", "r", encoding="utf-8") as f:
    r = json.load(f)

for idx in [0, 1]:
    c = r["fontManifest"]["chunks"][idx]
    c_idx = c["chunkIndex"]
    print(f"=== CHUNK {c_idx} ===")
    print("text:", c["text"])
    print("profileId:", c.get("profileId"), "| profileName:", c.get("profileName"))
    print("fxPreset:", c.get("fxPreset"), "| treatmentSystem:", c.get("treatmentSystem"))
    print("lockupOption:", c.get("lockupOption"))
    print("placement:", c.get("placement"))
    print("timing:", f"startMs={c.get('startMs')}, endMs={c.get('endMs')}, displayEndMs={c.get('displayEndMs')}")
    print("words:", c.get("words"))
    print("layers:")
    for l in c.get("layers", []):
        print(" -", l.get("layerName"), "| role:", l.get("role"), "| text:", l.get("text"), "| rawText:", l.get("rawText"), "| font:", l.get("fontFamily"), "| size:", l.get("fontSizePx"), "| behindSubject:", l.get("behindSubject"), "| words:", l.get("words"))
