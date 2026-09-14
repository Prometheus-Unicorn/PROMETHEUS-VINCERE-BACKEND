import json
import shutil
from pathlib import Path

receipt_path = Path("C:/Users/HomePC/Downloads/PROMETHEUS-VINCERE-BACKEND/output/gha_hakt_30s_pbd_1789360183_receipt.json")
master_mp4 = Path("C:/Users/HomePC/Downloads/PROMETHEUS-VINCERE-BACKEND/output/gha_hakt_30s_pbd_1789360183_master.mp4")
artifact_dir = Path("C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444")

with open(receipt_path, "r", encoding="utf-8") as f:
    receipt = json.load(f)

print("=== RECEIPT VERIFICATION ===")
print("Git SHA:", receipt.get("gitSha") or receipt.get("deploymentFingerprint", {}).get("gitSha"))
print("Status:", receipt.get("status"))
print("Duration (ms):", receipt.get("durationMs"))
print("Chunk Count:", receipt.get("chunkCount"))
print("Look Plan:", receipt.get("lookPlan", {}).get("lookId"))
print("Grade Filter:", repr(receipt.get("lookPlan", {}).get("gradeFilter")))

policy_report = receipt.get("policyReport", {})
print("\n=== POLICY REPORT ===")
print("Overall Policy Status:", policy_report.get("status"))
print("Passed Checks:", policy_report.get("passedChecks"), "/", policy_report.get("totalChecks"))
print("Violations:", policy_report.get("violations"))
for check_name, check_data in policy_report.get("checks", {}).items():
    print(f"  - {check_name}: {check_data.get('status')}")

print("\n=== CHUNK PLACEMENTS & LAYERING ===")
chunks = receipt.get("chunks", [])
for i, c in enumerate(chunks):
    text = c.get("text", "")
    p = c.get("placement", {})
    layers = c.get("layers", [])
    behind_layers = [l for l in layers if l.get("behindSubject")]
    y_pct = p.get("yPercent")
    dom_zone = p.get("dominantZone")
    behind_tag = f"BEHIND: {[l.get('rawText') for l in behind_layers]}" if behind_layers else "FOREGROUND ONLY"
    print(f"Chunk {i+1:02d} [{c.get('startMs')}ms - {c.get('endMs')}ms]: '{text}' | {behind_tag} | Zone: {dom_zone} | Y: {y_pct}")

# Copy receipt and mp4 to artifact dir
shutil.copy(receipt_path, artifact_dir / "r19_final_receipt.json")
shutil.copy(master_mp4, artifact_dir / "r19_final_master.mp4")
print("\nCopied master MP4 and receipt to artifact directory.")
