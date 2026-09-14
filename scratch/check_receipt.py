import json

with open("output/gha_hakt_30s_r6_1789124114_receipt.json", "r", encoding="utf-8") as f:
    receipt = json.load(f)

chunks = receipt.get("chunks", [])
for idx in (1, 3):
    c = chunks[idx]
    print(f"=== Chunk {idx}: '{c.get('text')}' ===")
    print("fxPreset:", c.get("fxPreset"))
    print("listicle:", c.get("listicle"))
    print("profileName:", c.get("profileName"))
    for l_i, layer in enumerate(c.get("layers", [])):
        print(f"  Layer {l_i}:")
        print(f"    text: {layer.get('text')}")
        print(f"    fontFamily: {layer.get('fontFamily')}")
        print(f"    role: {layer.get('role')}")
        print(f"    isHero: {layer.get('isHero')}")
        print(f"    fxPreset: {layer.get('fxPreset')}")
