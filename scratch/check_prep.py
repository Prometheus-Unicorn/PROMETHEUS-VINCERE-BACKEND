import json

with open("output/gha_hakt_30s_r11_1789168294_receipt.json", "r", encoding="utf-8") as f:
    r = json.load(f)

for idx in [4, 12]:
    c = r["fontManifest"]["chunks"][idx]
    print(f"Chunk {c['chunkIndex']} ({c['text']}) layers:")
    for l in c["layers"]:
        print("  role:", l.get("role"), "| isHero:", l.get("isHero"), "| isOverlapping:", l.get("isOverlapping"), "| shadow:", l.get("shadow"), "| ambient:", l.get("ambientShadow"), "| gradient:", bool(l.get("gradient") or l.get("verticalGradient")))
