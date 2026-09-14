import re, sys
sys.path.insert(0, '.')
from mini_run_pipeline import typography as t

# Show all origin_ / popcorn_ presets in ANIMA_RUNTIME_TREATMENTS
origin_ids = [item['id'] for item in t.ANIMA_RUNTIME_TREATMENTS if item['id'].startswith('origin_') or item['id'].startswith('popcorn')]
print("=== Registered in ANIMA_RUNTIME_TREATMENTS ===")
for i in origin_ids: print(' ', i)
print()

# Show all origin_/popcorn_ in INTRINSIC_ANIMATION_DURATIONS_MS
dur_ids = [k for k in t.INTRINSIC_ANIMATION_DURATIONS_MS if k.startswith('origin_') or k.startswith('popcorn')]
print("=== In INTRINSIC_ANIMATION_DURATIONS_MS ===")
for i in dur_ids: print(' ', i)
print()

# Show count
print(f"Total ANIMA_RUNTIME_TREATMENTS: {len(t.ANIMA_RUNTIME_TREATMENTS)}")

# Check KineticText folder for origin_ files
import os
kt = r'remotion-app/src/compositions/KineticText'
files = [f for f in os.listdir(kt) if f.startswith('Origin') or f.startswith('Popcorn')]
print("=== KineticText origin/popcorn files ===")
for f in sorted(files): print(' ', f)
