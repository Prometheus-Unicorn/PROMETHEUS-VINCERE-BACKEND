import json
from pathlib import Path
from mini_run_pipeline import typography, subject_placement

receipt_path = Path("C:/Users/HomePC/.gemini/antigravity-cli/brain/8ec47dcb-d657-40d5-8c1c-7270878d6444/r18_final_receipt.json")
with open(receipt_path, "r", encoding="utf-8") as f:
    receipt = json.load(f)

# Extract raw fresh chunks without pre-existing subjectLayering / placement
raw_chunks = []
for c in receipt.get("chunks", []):
    raw_chunks.append({
        "chunkIndex": c.get("chunkIndex"),
        "text": c.get("text"),
        "words": c.get("words"),
        "startMs": c.get("startMs"),
        "endMs": c.get("endMs"),
    })

print(f"Loaded {len(raw_chunks)} fresh transcription chunks")

# Run font manifest generation
manifest = typography.generate_font_manifest(raw_chunks, design_override={"motif": "champagne_gold", "subjectLayering": "auto"})
m_chunks = manifest.get("chunks", [])

print("\n--- FRESH GENERATION: BEHIND SUBJECT ASSIGNMENT ---")
for i, mc in enumerate(m_chunks):
    text = mc.get("text", "")
    layers = mc.get("typographyLayers", [])
    sl = mc.get("subjectLayering", {})
    behind = sl.get("behindSubject", False)
    behind_layers = [l for l in layers if l.get("behindSubject")]
    fg_layers = [l for l in layers if not l.get("behindSubject")]
    
    if behind or behind_layers:
        print(f"Chunk {i+1:02d}: '{text}' -> BEHIND: {[l.get('rawText') for l in behind_layers]}")
    else:
        print(f"Chunk {i+1:02d}: '{text}' -> FOREGROUND ONLY")
