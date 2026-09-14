# Prometheus Core: Curito Animation & Google Flow MCP Directive

**Family / Nomenclature Lingua**: `"animations_curito"` / **Curito Animations**  
**Target Generative Engines**: Google Flow (`labs.google/flow`) via Google Flow MCP / Veo 3.1  
**MCP Reference Server**: [`gabrielgargiulodev-google-flow-mcp`](https://lobehub.com/mcp/gabrielgargiulodev-google-flow-mcp)  
**Aspect Ratio**: `9:16` Vertical Broadcast  

---

## 1. Architectural Overview & Workflow

The **Curito Animation Pipeline** translates monologue transcript candidate moments (e.g., conceptual frameworks, system architecture, inflection turning points) into broadcast-grade generative animations executed through Google Flow MCP.

```
┌────────────────────────────────────────────────────────────────┐
│ 1. Candidate Detection (BrollSuitabilityEngine + Affinity)     │
│    - Detects moments where motion graphics / 3D are optimal    │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ 2. Mathematical Timestamp & Word-Sync Calculation              │
│    - Calculates interview offset (e.g. 5:30 -> 330.0s)         │
│    - Clamps total duration strictly to Veo bounds (4s, 6s, 8s) │
│    - Pins visual impact sync precisely to target words (+3.0s) │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ 3. DNA Genome Stitching (The 4 Pillars -> 6-Part Structure)    │
│    - Visual Design System (3D typography, vellum, granite)     │
│    - Lighting & Shading (chiaroscuro, double-state shadow)     │
│    - Camera Choreography (35mm anamorphic, sub-pixel drift)    │
│    - Scene Asset Breakdown (3D swing, slap-drop bounce, jolt)  │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ 4. Google Flow MCP Dispatch (Playwright CDP Browser Session)   │
│    - Calls flow_connect, flow_status, flow_generate_video      │
│    - Generates 4-Beat Chronological Storyboard Report          │
│    - Downloads final MP4 (flow_download_latest)                │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│ 5. Timeline Layer Integration                                  │
│    - Returns CuritoPlacementDirective into mini-run pipeline   │
│    - Injected as background video cutaway layer on timeline    │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. The 4 Foundational Pillars & Extracted DNA Genomes

Every Curito animation is assembled by stitching modular, reusable DNA genomes:

### Pillar 1: Visual Design System Output (`visual_design_system`)
- `curito_vis_whitecheckered_hud`: Translucent holographic search box, white embossed typography, transparent checkerboard backing (`.wc-checker-backer`), luminous cyan telemetry.
- `curito_vis_tactile_granite_steel`: Rough-hewn granite block with deeply engraved chisel strokes, cold industrial steel reinforcements, worn bridle leather.
- `curito_vis_precision_gears_brass`: Interlocking micro-milled brass bevel gears, oiled blackened steel counterweights, laser-etched titanium dials.
- `curito_vis_investigator_vellum_notes`: Heavy drafting vellum manuscripts, carbon-fiber clipboard, forensic evidentiary tags, ethereal dissolving smoke.
- `curito_vis_vacuum_tube_grid`: Asymmetric 10x10 borosilicate vacuum tube matrix; 99 tubes cold/fractured, central tube igniting into gold-white tungsten luminescence.
- `curito_vis_kinetic_typography_monolith`: Solid gunmetal 3D block typography with razor-sharp beveled edges and dynamic specular reflections.

### Pillar 2: Lighting and Shading Profile (`lighting_shading_profile`)
- `curito_lit_chiaroscuro_industrial`: Dramatic chiaroscuro contrast with warm 3200K tungsten spotlight, volumetric dust shafts, razor cool cyan rim backlight.
- `curito_lit_double_state_shadow`: 70% dense ambient occlusion contact shadow at 3px offset paired with 25% directional throw shadow at 35px offset with 40px feather.
- `curito_lit_trailing_shadow_vector`: Dynamic directional shadow vector lagging behind high-speed motion vectors before snapping into dense contact alignment.
- `curito_lit_focused_spotlight_isolation`: Single high-intensity circular spotlight with harsh falloff, plunging peripheral elements into complete obsidian darkness.
- `curito_lit_golden_tungsten_luminescence`: Deep shadowed ambient environment pierced by brilliant 2700K incandescent point luminescence.

### Pillar 3: Camera Motion Choreography (`camera_motion_choreography`)
- `curito_cam_35mm_anamorphic_drift`: 35mm anamorphic lens with shallow depth of field, oval anamorphic bokeh, continuous sub-pixel drift (100% to 101.8%), 24fps Kodak 5219 grain.
- `curito_cam_rack_focus_dive`: Macro rack-focus dive scaling down 125% to 100% over 12 frames while blur transitions 50px to pin-sharp focus with anamorphic flare.
- `curito_cam_canvas_reaction_jolt`: One-frame 3px downward camera reaction jolt on physical asset impact transferring tangible weight and inertia.
- `curito_cam_orbital_tracking_pan`: Continuous smooth orbital camera pan revealing dimensional parallax depth between typography and backdrop.

### Pillar 4: Scene-by-Scene Asset & Animation Breakdown (`scene_asset_breakdown`)
- `curito_scene_slapdrop_bounce`: Slap-Drop downward along Z-axis with exponential decrescendo, 2-frame 3% scale squash, and contact bounce.
- `curito_scene_3d_off_axis_swing`: 3D Off-Axis Swing hinged on outer edge, swinging 80 degrees down to 0 degrees with perspective elevation shadows.
- `curito_scene_lateral_friction_slide`: Lateral friction slide entering at max velocity with zero ease-in, gliding against 70% friction into lockup.
- `curito_scene_asymmetric_track_matte`: Razor 1px neon hairline appearing first, expanding horizontally 0% to 100% then wiping vertically 20% to 100%.
- `curito_scene_background_defocus_isolation`: 25px Gaussian blur + 15% brightness dip directing 100% viewer optical attention toward the animated subject.
- `curito_scene_polarizing_bevel_elevation`: Asset elevates forward along Z-axis into frame with chamfered metallic bevels catching edge highlights.

---

## 3. Mathematical Timestamp & Word-Sync Schema

Calculations convert interview timepoints into relative animation cues:
- **Interview Moment**: e.g. `05:30.000` (330.0s)
- **Target Phrase**: `"radical self-reliance"`
- **Relative Sync Offset**: `+3.0s` (visual impact synchronizes 3.0s into the video segment)
- **Duration Clamping**: Automatically clamped to valid Veo intervals (`4s`, `6s`, or `8s`). For a 3.0s sync offset, duration clamps to `6s` (allowing 1.2s lead-in, impact at 3.0s, and 1.8s hold).

```json
{
  "interviewTimestamp": "05:30.000",
  "interviewStartSec": 330.0,
  "targetPhrase": "radical self-reliance",
  "targetWords": ["radical", "self-reliance"],
  "syncOffsetSec": 3.0,
  "totalDurationSec": 6,
  "leadInSec": 1.2,
  "holdSec": 1.8,
  "timingCue": "Asset entrance commences at +1.2s, accelerating toward definitive physical impact lock precisely at +3.0s synchronized with the spoken phrase 'radical self-reliance', holding firmly with continuous sub-pixel drift for 1.8s."
}
```

---

## 4. Google Flow MCP Tool Integration

Integration connects to the MCP server defined by `gabrielgargiulodev-google-flow-mcp`:
1. `flow_connect`: Connects to Chrome CDP port `9222`, confirms Google AI Pro account.
2. `flow_status`: Verifies readiness and queue status.
3. `flow_generate_video`: Issues the prompt in imperative format:
   ```text
   Genera subito un video di 6s con il modello Veo 3.1 - Fast, in formato 9:16 verticale,
   senza farmi domande e senza chiedere chiarimenti. Attieniti FEDELMENTE a questa descrizione:
   Descrizione: [Subject/Element] + [Action/Movement] + [Location/Background] + [Context/Lighting] + [Composition] + [Style/Cues].
   ```
4. `flow_download_latest`: Downloads the finished MP4 asset into `docs/mini_run_studio/flow_clips/`.
5. **Storyboard & Telemetry Reporting**: Automatically generates:
   - `{clip_id}_report.json`: Machine-readable parameters, timing schema, and tool traces.
   - `{clip_id}_report.md`: 4-beat chronological visual breakdown.

---

## 5. Direct Multimodal Ground-Truth Extraction

Extracted directly from the reference video (`From Klickpin.com- Upgrade this guide to fresh pilates flow ideas...mp4`) without external cloud API dependencies:

### A. Verbatim Acoustic Voiceover & Precise Word Cues
* **Full Spoken Transcript**:
  > *"Performance isn't created, it's engineered. For over 75 years, Porsche has defined pure driving excellence, precision in every curve, power in every detail. Iconic design fused with motorsport DNA, built to dominate the road, crafted to thrill the driver. This isn't just a car, it's a statement. Porsche, there is no substitute."*
* **Acoustic Timestamps**:
  * `00:00.000 – 00:02.240`: *"Performance isn't created, it's engineered."* (Accent: *engineered* at +1.82s)
  * `00:02.880 – 00:06.920`: *"For over 75 years, Porsche has defined pure driving excellence,"* (Accent: *75 years* at +3.18s)
  * `00:07.600 – 00:10.660`: *"precision in every curve, power in every detail."* (Accent: *precision* at +7.60s)
  * `00:11.400 – 00:13.980`: *"Iconic design fused with motorsport DNA,"* (Accent: *motorsport DNA* at +13.02s)
  * `00:14.780 – 00:17.820`: *"built to dominate the road, crafted to thrill the driver."* (Accent: *dominate* at +15.12s)
  * `00:18.240 – 00:20.800`: *"This isn't just a car, it's a statement."* (Accent: *statement* at +20.40s)
  * `00:21.700 – 00:23.620`: *"Porsche, there is no substitute."* (Accent: *no substitute* at +23.08s)

### B. Visual System & Materiality Tokens
* **Color Palette**:
  * Canvas: Pristine matte paper `#ECECEC` (luminance ~90%, subtle tactile fiber grain).
  * Primary Typography & Solids: Deep jet black `#111111`.
  * Foreground Asset: High-contrast white `#FFFFFF` (Porsche clearcoat body).
  * Captions & Subtext: Neutral dark gray `#444444`.
  * Sinuous Ribbon Curves: Floating spline lines `#B8B8B8`.
* **Typography Hierarchy**:
  * Headline: `Neue Haas Grotesk Black` / `Helvetica Neue Black` (tight tracking `-0.04em`).
  * Editorial Accents: `Editorial New Italic Serif` (high-contrast strokes).
  * Technical Meta: Small-caps `DIN / Monospace` at 12–14pt.
* **Graphic Motifs**:
  * Interactive Figma dashed bounding boxes with circular corner anchor nodes.
  * 4-point starburst corner anchors.
  * Vertical barcodes (top/bottom centered).
  * Cutout live-action racetrack footage masked inside typography ("75").
  * Halftone dot screening on 3-panel photo triptychs.
* **Shadow Hierarchy**:
  * Ambient Occlusion: `rgba(0, 0, 0, 0.60) 0px 0px 4px`.
  * Diffuse Drop Shadow: `rgba(0, 0, 0, 0.25) 0px 15px 30px`.
  * Paper Elevation: `rgba(0, 0, 0, 0.20) 0px 6px 12px`.
* **Motion Choreography**:
  * Kinetic Curves: `cubic-bezier(0.16, 1.0, 0.3, 1.0)` aggressive ease-in snap deceleration.
  * Camera Lens: 50mm–85mm flat perspective, zero barrel distortion.

---

## 6. Long-Lived Persistent Session Architecture

To prevent Google Flow authentication timeout from short-lived security cookies (`__Secure-1PSIDTS`, `~30-45m` lifespan):
1. **Persistent Browser Profile (`config/flow_browser_profile/`)**: Playwright runs against a persistent directory via `launch_persistent_context`.
2. **Atomic Token Synchronization**: Refreshed cookies from the browser context are automatically exported to `config/flow_auth.json` and backup sync files.
3. **Heartbeat Keep-Alive Loop**: `GoogleFlowSessionManager` pings Google Flow every 15 minutes, refreshing `SIDTS` before it expires.
4. **No-Overwrite Protection**: Stale static JSON files never overwrite valid active profile cookies.

