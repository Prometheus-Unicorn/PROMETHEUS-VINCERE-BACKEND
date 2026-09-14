import json
from pathlib import Path

receipt_path = Path("output/gha_hakt_30s_pbd_1789279473_receipt.json")
with open(receipt_path, "r", encoding="utf-8") as f:
    r = json.load(f)

print("=== DEPLOYMENT FINGERPRINT ===")
print(json.dumps(r.get("deploymentFingerprint"), indent=2))

print("\n=== LOOK PLAN ===")
lp = r.get("lookPlan") or {}
print(f"lookId: {lp.get('lookId')}")
print(f"gradeFilter: {lp.get('gradeFilter')}")
print(f"authentic3dLut: {lp.get('authentic3dLut')}")

print("\n=== POLICY REPORT CHECKS ===")
pr = r.get("policyReport") or {}
print(f"overall status: {pr.get('status')}")
checks = pr.get("checks") or {}
for k, v in checks.items():
    print(f"\n--- CHECK: {k} (status={v.get('status')}) ---")
    for field, val in v.items():
        if field not in ("status", "measurements"):
            print(f"  {field}: {val}")
        elif field == "measurements":
            print(f"  measurements count: {len(val)}")
            for m in val:
                print(f"    {m}")
        if field == "pixelTruth":
            print(f"    pixelTruth: wrapInducedRowsDetected={val.get('wrapInducedRowsDetected')}")
            for pm in val.get("measurements", []):
                print(f"      ts={pm.get('timestampSec')}s, chk={pm.get('chunkIndex')}, manifest={pm.get('manifestLines')}, pixel={pm.get('pixelTruthRows')}, wrapInduced={pm.get('wrapInduced')}")

print("\n=== SPLIT-LAYER CHUNKS & PLACEMENT (C2/C5) ===")
chunks = r.get("chunks") or []
for c in chunks:
    layers = c.get("layers") or []
    has_behind = any(l.get("behindSubject") for l in layers)
    if has_behind:
        c_idx = c.get("chunkIndex")
        print(f"Chunk {c_idx} (split-layer):")
        for l in layers:
            p = l.get("placement") or {}
            print(f"  layer {l.get('layerIndex')}: role={l.get('role')}, text='{l.get('rawText')}', font='{l.get('fontFamily')}', behindSubject={l.get('behindSubject')}, zone={p.get('dominantZone')}, yPercent={p.get('yPercent')}")
