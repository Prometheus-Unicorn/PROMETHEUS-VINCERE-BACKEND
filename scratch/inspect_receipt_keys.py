import json

with open("C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444/r18_final_receipt.json", "r", encoding="utf-8") as f:
    r = json.load(f)

print("Top level keys:", list(r.keys()))
if "typography" in r:
    print("typography keys:", list(r["typography"].keys()))
    print("typography chunk count:", len(r["typography"].get("chunks", [])))
if "pipeline" in r:
    print("pipeline keys:", list(r["pipeline"].keys()))
