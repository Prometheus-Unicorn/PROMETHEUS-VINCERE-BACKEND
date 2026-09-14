import json

with open("mini_run_pipeline/typography_profiles_v2_catalog.json", "r", encoding="utf-8") as f:
    v2 = json.load(f)

profs = v2["profiles"]
print("Type of profiles:", type(profs))
if isinstance(profs, dict):
    print("Keys containing Personal:", [k for k in profs.keys() if "Personal" in k])
    p = profs.get("Getting_More_Personal_Video_Subtitle_Hook") or profs.get("Getting_More_Personal_Video_Subtitle_Hook.json")
    print(json.dumps(p, indent=2))
elif isinstance(profs, list):
    for p in profs:
        if "Personal" in str(p):
            print(json.dumps(p, indent=2))
