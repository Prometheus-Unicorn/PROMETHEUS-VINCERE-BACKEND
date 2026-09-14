---
name: output-critique
description: Hostile-to-hallucination visual and acoustic output critique loop. Automatically measures luminance clipping, shadow crush, skin tone preservation, text occlusion geometry, and stem separation against raw source material before declaring quality. Use when validating renders, diagnosing color grading regressions, checking visual legibility, or auditing pipeline outputs.
---

# Output Critique: Hostile-to-Hallucination Quality Gate

## Philosophy: Assume Failure Until Proven by Pixels
AI agents suffer from a known confirmation bias: declaring a rendered video "high quality", "cinematic", or "flawless" based purely on the intention of the code, without objectively inspecting the visual and acoustic output.

This skill establishes a **mandatory internal loop of adversarial critique**. You do not praise an output. You run deterministic probes, compute pixel deltas against the unprocessed source footage, and aggressively hunt for regressions.

---

## The 4-Pillar Internal Critique Loop

### Pillar 1: Source Material Sanity Check (The Domain Mismatch Trap)
Before grading or evaluating any shot:
1. **Identify the Color Space of the Ingest Footage**:
   - Is the source raw camera Log (flat, desaturated, high-dynamic-range curve like Panasonic V-Log, Sony S-Log3, ARRI LogC)?
   - Or is the source an **already-graded standard Rec.709** production master (normal contrast, deep blacks, natural saturation)?
2. **Rule of Log LUT Application**:
   - **NEVER** apply a Log-to-Rec709 conversion LUT to footage that is already in Rec.709. Doing so creates an aggressive double S-curve that crushes shadows into pitch-black voids and destroys dynamic range.
   - For already-graded Rec.709 footage, the grade must be **passthrough (unaltered)** or strictly restrained to subtle creative tinting without shadow crushing.

### Pillar 2: Quantitative Luminance & Dynamic Range Verification
Every rendered shot must pass automated histogram and clipping analysis:
```python
# Compute clipping and dynamic range
import cv2, numpy as np
frame = cv2.imread("frame.png")
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
shadow_clipped_pct = np.mean(gray < 10) * 100
highlight_clipped_pct = np.mean(gray > 245) * 100
mean_brightness = np.mean(gray)
```
- **Shadow Crush Defect**: If `shadow_clipped_pct > 15%` (and the raw source was `< 5%`), flag as **CRITICAL REGRESSION: Shadow Crush / Black Void**.
- **Dynamic Range Defect**: If the output loses more than 50% of the ambient environment visible in the source, flag as **CRITICAL REGRESSION: Crushed Exposure**.

### Pillar 3: Visual Element Occlusion & Lighting Separation
Inspect the composite keyframes at key semantic beats:
1. **Subject-Background Contrast**: Is the subject tonally separated from the background, or do the subject's clothes/hair merge into the background?
2. **Behind-Subject Text Integrity**:
   - Does behind-subject text emit a glow/halo box over the subject? (Must be `none`).
   - Does text clip through the subject's face? (Head occlusion must remain $\le 40\%$).
   - Is companion text anchored cleanly in the lower deck without colliding with the subject's head?

### Pillar 4: Audio Stem Vocal Priority Verification
1. **Dialogue Clearance**: Dialogue stems must remain prominently intelligible at all times.
2. **Music Bed Separation**: Background music must duck $\ge 4.0:1$ with $\le 20\text{ms}$ attack under speech syllables, resting at $\le -12\text{dB}$ relative to dialogue.
3. **SFX Intelligibility**: Camera moves and visual transitions must produce distinct, audible acoustic feedback without masking the voice.

---

## Critique Protocol Output Format
Every audit cycle conducted under this skill must output:
1. **Source vs Output Metric Table**: Raw vs Graded mean brightness, shadow clipping %, and pixel delta.
2. **Visual Proof**: Side-by-side comparative frame (`scratch/color_grade_diagnostic_comparison.png`).
3. **Flaw Ledger**: Unvarnished list of defects, failures, or regressions.
4. **Root Cause Analysis**: Why the system produced the defect (code/data/transform mismatch).
5. **Concrete Correction**: The single minimal code/configuration fix required.
