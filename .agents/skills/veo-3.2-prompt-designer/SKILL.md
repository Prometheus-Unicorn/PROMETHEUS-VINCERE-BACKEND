---
name: veo-3.2-prompt-designer
description: Transforms multimodal assets (images, videos, audio) and creative intent into structured, executable prompts for the Google Veo 3.2 video generation model (Artemis world-model engine). Implements the 5-Part Framework (Shot → Subject → Environment → Camera → Style), reference image attachments, and generation parameter configs.
---

# Veo 3.2 Prompt Designer Skill

This skill transforms scattered multimodal assets (images, videos, audio) and creative intent into structured, executable prompts and parameter payloads for the Google Veo 3.2 video generation model (Artemis engine).

## When to Use
- When providing assets (images, videos, audio) for video generation with Veo 3.2.
- When generating complex video diffusion prompts requiring world-model physics, rigid geometry, and lighting discipline.
- When configuring reference images (STYLE, SUBJECT, SUBJECT_FACE) or parameter schemas for any Google Veo 3.x model.

## Core Capabilities & Artemis Engine Differentiators
- **Engine**: Artemis — world-model physical simulation (not 2D pixel prediction).
- **Duration**: Up to ~30s native continuous generation (standard clips: 6s - 8s).
- **Audio**: Native dialogue + synchronized SFX and ambient acoustic pads.
- **Reference Images**: Up to 3 reference images mapped to specific roles:
  - `STYLE`: Color palette, grain, lighting, and texture aesthetic.
  - `SUBJECT`: Physical object shape, geometry, material finish, and details.
  - `SUBJECT_FACE`: Facial likeness, identity consistency.
- **Video Extension & Keyframing**: Chain clips via previous video input; first/last frame keyframing.
- **Resolutions & Ratios**: 720p, 1080p, 4K (with upscaling); 16:9, 9:16 aspect ratios.

## 3-Phase Internal Workflow

### Phase 1: Recognition
Analyze incoming transcript chunks, audio stems, and uploaded assets:
1. Deconstruct spoken speech into Entity-Action-Manner NLP dimensions:
   - **Action Verb**: Core kinetic verb (lock, rotate, clamp, switch, accelerate).
   - **Manner Adverb / Torque**: Physical dynamic (high-torque, decisive, decelerating).
   - **Thematic Target**: Abstract concept (tolerance, foundation, scale, friction).
2. Classify any provided visual/audio assets into atomic element roles (Subject, Style, Camera, Audio).

### Phase 2: Mapping
Map each atomic element to its optimal reference method:
- **Reference Image**: Specific hero products, brand artifacts, or strict graphic styles.
- **Text Prompt**: Lighting physics, kinetic trajectories, temporal arcs, camera moves.
- **Hybrid**: Visual subject reference image combined with kinetic motion prompt.

### Phase 3: Construction (The 5-Part Framework)
Assemble the final diffusion prompt using the standard 5-element sequence:
1. **Shot**: Framing & perspective (e.g., `Hero shot, spatially locked 45-degree isometric studio view`).
2. **Subject**: Tangible, volumetric hero artifact with physical materiality and surface micro-details (e.g., `cast-steel dual-throw knife switch, solid copper busbar jaws, micro-chamfered brass pivot pins`).
3. **Environment**: Spatial-temporal graphic backdrop with tactile textures and negative space (e.g., `pristine off-white graphic canvas with micro-stippled dot grid texture, upper 45% reserved as clean negative space. Zero tables or office furniture`).
4. **Camera & Physics**: Spatially locked fixed-tripod camera, 1-DoF constrained axial kinematics, rigid-body topological permanence, zero 180-degree yaw flips, unitary manifold physics with zero ghosting or duplication.
5. **Style & Optics**: Raked directional key light, floating ambient occlusion volume, directional slow-shutter motion blur on kinetic components with tack-sharp stationary bodies.

## Final Output Schema

```json
{
  "final_prompt": "Hero shot, heavy industrial cast-steel dual-throw knife switch with solid copper busbar jaws, spatially locked 45-degree isometric studio view. Blackened carbon steel lever arm, hand-finished copper jaws, micro-chamfered brass pivot pins. Pristine matte off-white graphic canvas with fine micro-stippled grid texture, reserving upper 45% as negative space. High-contrast raked key lighting with floating ambient occlusion. Fixed tripod camera, 1-DoF constrained downward lever rotation, rigid-body topological permanence, native 24fps. Lever snaps down with high-torque authority, directional motion blur on moving blade while base remains tack-sharp.",
  "reference_images": [
    {
      "file": "knife_switch_hero.png",
      "reference_type": "SUBJECT"
    }
  ],
  "recommended_parameters": {
    "model": "veo-3.2-generate",
    "duration_seconds": 8,
    "aspect_ratio": "9:16",
    "resolution": "720p",
    "generate_audio": false
  }
}
```
