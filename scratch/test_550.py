import sys
sys.path.insert(0, '.')
import json

# Temporarily test with 550.0
from mini_run_pipeline import subject_placement, policy_check

r = json.load(open('docs/mini_run_studio/run_34832825076/render-receipt-gha_hakt_30s_pbd_1789381325/receipt_gha_hakt_30s_pbd_1789381325.json'))
obs = json.load(open('scratch/saved_obs.json'))
chunks = r['fontManifest']['chunks']

# What happens if flank_eligible <= 550.0?
# Let's inspect where Chunk 18 lands when top_headroom >= 0.10 and flank_eligible <= 550.0
# In subject_placement.py:
# Chunk 17 will be cranial_crown.
# Then prev_zone for Chunk 18 is cranial_crown -> target_zone = "foreground_lower_deck"!
# So Chunk 18 is foreground_lower_deck REGARDLESS of flank_eligible!

# Let's test with 550.0:
import importlib
# modify subject_placement line 728-729 in memory or check
# Let's check with 550.0:
