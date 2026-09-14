import sys, json, os
from pathlib import Path
import cv2
import numpy as np

RECEIPT_PATH = Path('output/gha_hakt_30s_pbd_1789386330_receipt.json')
MASTER_MP4 = Path('output/gha_hakt_30s_pbd_1789386330_master.mp4')
RAW_SOURCE = Path('remotion-app/public/source/test-video.mp4')
SCRATCH_DIR = Path('scratch/r20_final_critique')
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

receipt = json.loads(RECEIPT_PATH.read_text(encoding='utf-8'))

print("=" * 70)
print("RUN 34839835841: HOSTILE-TO-HALLUCINATION 4-PILLAR CRITIQUE")
print("=" * 70)

# Receipt verification
git_sha = receipt.get('deploymentFingerprint', {}).get('gitSha')
print(f"[Receipt] deploymentFingerprint.gitSha: {git_sha}")
print(f"[Receipt] status: {receipt.get('status')}")
print(f"[Receipt] durationMs: {receipt.get('durationMs')}")
print(f"[Receipt] slicesRendered: {receipt.get('slicesRendered')}")
pr = receipt.get('policyReport', {})
print(f"[Receipt] policyReport status: {pr.get('status')} | passed: {pr.get('passedChecks')}/{pr.get('totalChecks')} | violations: {len(pr.get('violations', []))}")
for v in pr.get('violations', []):
    print(f"   Violation: {v}")

# Extract frames for comparison
timestamps = [2.0, 7.4, 15.0, 18.5, 20.6, 21.6, 22.0, 27.5]
cap_raw = cv2.VideoCapture(str(RAW_SOURCE))
cap_master = cv2.VideoCapture(str(MASTER_MP4))
fps_raw = cap_raw.get(cv2.CAP_PROP_FPS)
fps_master = cap_master.get(cv2.CAP_PROP_FPS)

metrics = []

for t in timestamps:
    # Read raw
    cap_raw.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps_raw)))
    ret_r, f_raw = cap_raw.read()
    
    # Read master
    cap_master.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps_master)))
    ret_m, f_master = cap_master.read()
    
    if not (ret_r and ret_m):
        continue

    # Resize raw to 1080x1920 (crop/scale matching master canvas)
    # The raw is 1280x720 horizontal or 1080x1920? Let's check raw shape
    rh, rw = f_raw.shape[:2]
    mh, mw = f_master.shape[:2]
    
    gray_r = cv2.cvtColor(f_raw, cv2.COLOR_BGR2GRAY)
    gray_m = cv2.cvtColor(f_master, cv2.COLOR_BGR2GRAY)

    r_mean = float(np.mean(gray_r))
    m_mean = float(np.mean(gray_m))
    r_shadow = float(np.mean(gray_r < 10) * 100)
    m_shadow = float(np.mean(gray_m < 10) * 100)
    r_high = float(np.mean(gray_r > 245) * 100)
    m_high = float(np.mean(gray_m > 245) * 100)

    # Save proof frame
    frame_name = f"frame_{t:.1f}s.png"
    cv2.imwrite(str(SCRATCH_DIR / frame_name), f_master)
    
    metrics.append({
        "timestamp": t,
        "raw_mean": round(r_mean, 2),
        "master_mean": round(m_mean, 2),
        "raw_shadow_crush_pct": round(r_shadow, 3),
        "master_shadow_crush_pct": round(m_shadow, 3),
        "raw_high_clip_pct": round(r_high, 3),
        "master_high_clip_pct": round(m_high, 3),
        "delta_mean": round(abs(m_mean - r_mean), 2)
    })

cap_raw.release()
cap_master.release()

print("\n--- PILLAR 1 & 2: QUANTITATIVE LUMINANCE & COLOR METRICS ---")
print(f"{'Time':>6} | {'Raw Mean':>9} | {'Master Mean':>11} | {'Raw Shd %':>10} | {'Mstr Shd %':>10} | {'High %':>7} | {'Delta':>6}")
for m in metrics:
    print(f"{m['timestamp']:>5.1f}s | {m['raw_mean']:>9.2f} | {m['master_mean']:>11.2f} | {m['raw_shadow_crush_pct']:>9.3f}% | {m['master_shadow_crush_pct']:>9.3f}% | {m['master_high_clip_pct']:>6.3f}% | {m['delta_mean']:>6.2f}")

# Save metrics JSON
(SCRATCH_DIR / "critique_metrics.json").write_text(json.dumps(metrics, indent=2))
print(f"\n[Saved] Metrics -> {SCRATCH_DIR / 'critique_metrics.json'}")
