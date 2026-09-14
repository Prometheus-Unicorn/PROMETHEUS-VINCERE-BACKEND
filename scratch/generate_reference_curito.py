"""Generate Curito Animation Asset for Reference Porsche Sequence.

Target Account: ipsasummagnitudo@gmail.com (Profile 12)
Model: Veo 3.1 - Fast (6s, 9:16)
"""

from pathlib import Path
import json
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mini_run_pipeline.curito_animation_dna import (
    CuritoPromptStitcher,
    CuritoWordSyncCalculator,
)
from mini_run_pipeline.google_flow_client import (
    GoogleFlowConfig,
    GoogleFlowMCPClient,
)

def run_reference_generation():
    # 1. Compute Word Sync Schema
    word_sync = CuritoWordSyncCalculator.compute_word_sync(
        interview_start_timestamp="00:18.000",
        target_phrase="This isn't Just A car",
        target_word_offset_sec=3.0,
        desired_duration_sec=6.0,
        climax_description="Radial compass dials snap to magnetic lock as vehicle contact bounce settles"
    )

    # 2. Stitch Curito Prompt Genomes
    from mini_run_pipeline.curito_animation_dna import (
        CATEGORY_VISUAL_DESIGN_SYSTEM,
        CATEGORY_LIGHTING_SHADING_PROFILE,
        CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        CATEGORY_SCENE_ASSET_BREAKDOWN,
        CURITO_GENOME_LIBRARY,
    )

    selected_genomes = {
        CATEGORY_VISUAL_DESIGN_SYSTEM: CURITO_GENOME_LIBRARY["curito_vis_orthographic_zenith_dial"],
        CATEGORY_LIGHTING_SHADING_PROFILE: CURITO_GENOME_LIBRARY["curito_lit_chiaroscuro_industrial"],
        CATEGORY_CAMERA_MOTION_CHOREOGRAPHY: CURITO_GENOME_LIBRARY["curito_cam_35mm_anamorphic_drift"],
        CATEGORY_SCENE_ASSET_BREAKDOWN: CURITO_GENOME_LIBRARY["curito_scene_slapdrop_bounce"],
    }

    stitched_prompt = CuritoPromptStitcher.stitch_prompt(
        subject_metaphor="Top-down orthographic zenith perspective of sculpted white Porsche 911 GT3 RS with carbon fiber dual hood vents and massive rear wing, flanked by radial clock hands and precision compass needles",
        word_sync=word_sync,
        selected_genomes=selected_genomes,
        model="Veo 3.1 - Fast",
        aspect_ratio="9:16",
    )

    # 3. Initialize Flow Client
    config = GoogleFlowConfig.from_env_or_config()
    print(f"Active Account: {config.expected_account} ({config.profile_directory})")
    assert config.expected_account == "ipsasummagnitudo@gmail.com", "Account must be ipsasummagnitudo@gmail.com"

    client = GoogleFlowMCPClient(config)

    # 4. Generate Asset & Reports
    report = client.generate_curito_animation(
        prompt=stitched_prompt,
        concept_title="Porsche 911 GT3 RS Zenith Dial Lockup",
        clip_filename="curito_porsche_zenith_6s.mp4",
    )

    print("Generation successful!")
    print(f"MP4: {report.mp4_asset_path}")
    print(f"Status: {report.status}")
    print(f"Project: {report.project_name}")
    print(f"JSON: docs/mini_run_studio/flow_clips/{Path(report.mp4_asset_path).stem}_report.json")
    print(f"MD: docs/mini_run_studio/flow_clips/{Path(report.mp4_asset_path).stem}_report.md")

if __name__ == "__main__":
    run_reference_generation()
