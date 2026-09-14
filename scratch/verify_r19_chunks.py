import json
from pathlib import Path
from mini_run_pipeline import typography, subject_placement

receipt_path = Path("C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444/r18_final_receipt.json")
with open(receipt_path, "r", encoding="utf-8") as f:
    receipt = json.load(f)

chunks = receipt.get("chunks", [])
print(f"Loaded {len(chunks)} chunks from r18_final_receipt.json")

# Run font manifest generation
manifest = typography.generate_font_manifest(chunks, design_override={"motif": "champagne_gold", "subjectLayering": "auto"})
m_chunks = manifest.get("chunks", [])

# Extract subject observations from receipt
observations = receipt.get("subject_observations", receipt.get("observations", []))
if not observations:
    # Try video metadata
    observations = receipt.get("design", {}).get("observations", [])

# Run subject placement planning
placements = subject_placement.plan_subject_safe_placements(m_chunks, observations)

print("\n--- ROUND 19 PLACEMENT & LAYERING AUDIT ---")
for i, (mc, pl) in enumerate(zip(m_chunks, placements)):
    text = mc.get("text", "")
    layers = mc.get("typographyLayers", [])
    behind = mc.get("subjectLayering", {}).get("behindSubject", False)
    behind_layers = [l for l in layers if l.get("behindSubject")]
    fg_layers = [l for l in layers if not l.get("behindSubject")]
    
    y_pct = pl.get("yPercent", "N/A")
    dom_zone = pl.get("dominantZone", "N/A")
    
    behind_desc = f"BEHIND ({', '.join(l.get('rawText', '') for l in behind_layers)})" if behind_layers else "NO BEHIND"
    fg_desc = f"FG: '{' / '.join(l.get('rawText', '') for l in fg_layers)}'"
    
    print(f"Chunk {i+1:02d}: '{text}' | {behind_desc} | {fg_desc} | Zone: {dom_zone} | Y: {y_pct}")
