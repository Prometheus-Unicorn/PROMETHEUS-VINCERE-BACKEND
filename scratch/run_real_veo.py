"""
Real Veo Video Generation via google-genai SDK.
Account: GEMINI_API_KEY from environment (Google AI Studio)
Model: veo-2.0-generate-001
No fallbacks. No mocks. Exposes any failure directly.
"""

import os
import sys
import time
import warnings
import urllib.request
from pathlib import Path

warnings.filterwarnings("ignore")

import google.genai as genai
from google.genai import types

# --- Config ---
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_STUDIO_API_KEY")
if not API_KEY:
    print("FATAL: No GEMINI_API_KEY found in environment.")
    sys.exit(1)

OUTPUT_DIR = Path("docs/mini_run_studio/flow_clips")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_MP4 = OUTPUT_DIR / "curito_porsche_zenith_veo31_8s.mp4"

# --- Curito Prompt: Porsche Zenith Dial Lockup ---
PROMPT = (
    "Top-down orthographic zenith perspective of a sculpted white Porsche 911 GT3 RS "
    "with carbon fiber dual hood vents and massive rear wing, anchored by deep ambient "
    "occlusion floor contact shadows, flanked by radial clock hands and precision compass "
    "needles sweeping dynamically and snapping to magnetic lock. "
    "Dramatic chiaroscuro contrast with intense warm 3200K tungsten spotlight, "
    "volumetric shafts of light cutting through dusty studio air, "
    "razor cool cyan rim backlighting throwing sharp directional highlights across bodywork. "
    "Vertical 9:16 composition captured on 35mm anamorphic lens with shallow depth of field, "
    "smooth oval anamorphic bokeh, continuous anti-stagnation sub-pixel drift, "
    "24fps cadence, subtle Kodak 5219 film grain, "
    "high-agency luxury automotive editorial motion design, crisp vector edges."
)

print(f"API Key: {API_KEY[:6]}...{API_KEY[-4:]}")
print(f"Prompt ({len(PROMPT)} chars): {PROMPT[:80]}...")
print()

# --- Initialize client ---
client = genai.Client(api_key=API_KEY)

# --- Check available Veo models ---
print("Listing available models with video generation support...")
try:
    all_models = list(client.models.list())
    veo_models = [m for m in all_models if "veo" in m.name.lower() or "video" in m.name.lower()]
    if veo_models:
        print(f"Found {len(veo_models)} Veo model(s):")
        for m in veo_models:
            print(f"  - {m.name}")
    else:
        print(f"No explicit Veo models found. Total models: {len(all_models)}")
        print("Model names:", [m.name for m in all_models[:15]])
except Exception as e:
    print(f"Warning: Could not list models: {e}")

print()
MODELS_TO_TRY = [
    "veo-3.1-generate-preview",
    "veo-3.1-fast-generate-preview",
    "veo-3.1-lite-generate-preview",
]

operation = None
used_model = None

for model_name in MODELS_TO_TRY:
    print(f"Trying model: {model_name} ...")
    try:
        operation = client.models.generate_videos(
            model=model_name,
            prompt=PROMPT,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                duration_seconds=8,
                number_of_videos=1,
            ),
        )
        used_model = model_name
        print(f"Dispatched successfully on {model_name}.")
        break
    except Exception as e:
        print(f"  FAILED ({model_name}): {type(e).__name__}: {str(e)[:200]}")
        if "RESOURCE_EXHAUSTED" not in str(e) and "QUOTA" not in str(e).upper():
            raise  # Non-quota error — propagate immediately

if operation is None:
    print()
    print("=" * 60)
    print("FAILURE: All Veo models exhausted their quota on the current API key.")
    print("The GEMINI_API_KEY in environment has no remaining Veo video generation quota.")
    print("Resolution required: Use a paid Vertex AI key or refresh the Google AI Studio quota.")
    print("=" * 60)
    sys.exit(1)

print(f"\nOperation dispatched on {used_model}. Operation name: {operation.name}")
print("Polling for completion (timeout: 10 minutes)...")

start = time.time()
poll_interval = 10
timeout = 600

while not operation.done:
    elapsed = time.time() - start
    if elapsed > timeout:
        print(f"TIMEOUT: Generation did not complete within {timeout}s.")
        sys.exit(1)
    print(f"  [{int(elapsed)}s] Still generating... (polling every {poll_interval}s)")
    time.sleep(poll_interval)
    operation = client.operations.get(operation)

print()
print("Generation complete!")

if not operation.response or not operation.response.generated_videos:
    print("FAILURE: Operation completed but no videos were returned.")
    print("Full response:", operation)
    sys.exit(1)

video = operation.response.generated_videos[0]
print(f"Video object: {video}")

# --- Download ---
print(f"Downloading video to {OUTPUT_MP4}...")
client.files.download(file=video.video, download_path=str(OUTPUT_MP4))

size = OUTPUT_MP4.stat().st_size
if size < 10000:
    print(f"FAILURE: Downloaded file is only {size} bytes — likely corrupt or empty.")
    sys.exit(1)

print()
print("=" * 60)
print(f"SUCCESS: Real Veo-generated MP4 saved.")
print(f"Model used: {used_model}")
print(f"File: {OUTPUT_MP4.absolute()}")
print(f"Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
print("=" * 60)
