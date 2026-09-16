"""Curito Cinematic Animation Prompt DNA Genome Catalog & Stitching Engine.

Lingua & Nomenclature: "animations_curito" / Curito Animations.
Part of the Mini-Run Pipeline (mini_run_pipeline/).

This engine extracts, formalizes, and dynamically stitches the modular "DNA genomes"
of cinematic generative animations across 4 core foundational pillars:
1. Visual Design System Output (tactile materiality, 3D typography, 38.whitecheckered HUDs)
2. Lighting & Shading Profile (chiaroscuro contrast, volumetric shafts, double-state shadows)
3. Camera Motion Choreography (35mm anamorphic optics, sub-pixel drift, rack-focus dives)
4. Scene-by-Scene Asset & Animation Breakdown (spatial physics, reveals, background defocus)

Provides timestamp calculation and word-sync alignment to synchronize visual climax moments
(e.g., key phrase reveals at +3.0s into an interview segment) directly into the prompt schema.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Nomenclature & Lingua Constants
# ---------------------------------------------------------------------------

CURITO_TREATMENT_FAMILY = "animations_curito"
CURITO_LINGUA_PREFIX = "animations.curito"

CATEGORY_VISUAL_DESIGN_SYSTEM = "visual_design_system"
CATEGORY_LIGHTING_SHADING_PROFILE = "lighting_shading_profile"
CATEGORY_CAMERA_MOTION_CHOREOGRAPHY = "camera_motion_choreography"
CATEGORY_SCENE_ASSET_BREAKDOWN = "scene_asset_breakdown"

CORE_GENOME_CATEGORIES = (
    CATEGORY_VISUAL_DESIGN_SYSTEM,
    CATEGORY_LIGHTING_SHADING_PROFILE,
    CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
    CATEGORY_SCENE_ASSET_BREAKDOWN,
)

# Detailed Curito Forensic DNA Families
FAMILY_MOTION_CURVES = "motion_curves"
FAMILY_CAMERA_CHOREOGRAPHY = "camera_choreography"
FAMILY_TRANSITIONS = "transitions"
FAMILY_KEY_LIGHTING = "key_lighting"
FAMILY_SHADOW_HIERARCHY = "shadow_hierarchy"
FAMILY_MATERIALITY_TEXTURE = "materiality_texture"
FAMILY_GRAPHIC_ELEMENTS = "graphic_elements"
FAMILY_TYPOGRAPHY_HIERARCHY = "typography_hierarchy"
FAMILY_SCENE_BREAKDOWN = "scene_breakdown"

CURITO_DNA_FAMILIES = (
    FAMILY_MOTION_CURVES,
    FAMILY_CAMERA_CHOREOGRAPHY,
    FAMILY_TRANSITIONS,
    FAMILY_KEY_LIGHTING,
    FAMILY_SHADOW_HIERARCHY,
    FAMILY_MATERIALITY_TEXTURE,
    FAMILY_GRAPHIC_ELEMENTS,
    FAMILY_TYPOGRAPHY_HIERARCHY,
    FAMILY_SCENE_BREAKDOWN,
)

VALID_VEO_DURATIONS = (4, 6, 8)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class CuritoGenome:
    """An individual modular prompt snippet representing a specific cinematic DNA element."""
    id: str
    category: str
    name: str
    dna_snippet: str
    tags: List[str] = field(default_factory=list)
    family: str = CURITO_TREATMENT_FAMILY
    subfamily: str = ""
    weight: float = 1.0
    archetype: str = "editorial_documentary"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CuritoWordSyncSchema:
    """Precise mathematical timestamp and word-level synchronization directive."""
    interview_timestamp: str           # Formatted interview timestamp (e.g. "05:30.000" or "00:12.500")
    interview_start_sec: float         # Absolute start time in seconds (e.g. 330.0)
    target_phrase: str                 # Monologue inflection phrase (e.g. "radical self-reliance")
    target_words: List[str]            # Tokenized target words
    sync_offset_sec: float             # Offset into the animation when key words trigger (e.g. 3.0s)
    total_duration_sec: int            # Clamped generative video duration (4, 6, or 8 seconds)
    lead_in_sec: float                 # Lead-in duration before climax landing (e.g. 1.2s)
    hold_sec: float                    # Hold / lingering duration after landing (e.g. 1.8s)
    timing_cue: str                    # Natural language timing instruction for the generator
    climax_moment_description: str     # Visual event occurring at the sync offset

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interviewTimestamp": self.interview_timestamp,
            "interview_timestamp": self.interview_timestamp,
            "interviewStartSec": self.interview_start_sec,
            "interview_start_sec": self.interview_start_sec,
            "targetPhrase": self.target_phrase,
            "target_phrase": self.target_phrase,
            "targetWords": list(self.target_words),
            "target_words": list(self.target_words),
            "syncOffsetSec": self.sync_offset_sec,
            "sync_offset_sec": self.sync_offset_sec,
            "totalDurationSec": self.total_duration_sec,
            "total_duration_sec": self.total_duration_sec,
            "leadInSec": self.lead_in_sec,
            "lead_in_sec": self.lead_in_sec,
            "holdSec": self.hold_sec,
            "hold_sec": self.hold_sec,
            "timingCue": self.timing_cue,
            "timing_cue": self.timing_cue,
            "climaxMomentDescription": self.climax_moment_description,
            "climax_moment_description": self.climax_moment_description,
        }


@dataclass
class CuritoStitchedPrompt:
    """Complete synthesized generative prompt stitched from modular DNA genomes."""
    genome_ids: List[str]
    subject_element: str
    action_movement: str
    location_background: str
    context_lighting: str
    composition: str
    style_cues: str
    word_sync: CuritoWordSyncSchema
    full_prompt: str
    imperative_flow_prompt: str
    model: str
    duration_sec: int
    aspect_ratio: str = "9:16"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "genomeIds": list(self.genome_ids),
            "genome_ids": list(self.genome_ids),
            "subjectElement": self.subject_element,
            "subject_element": self.subject_element,
            "actionMovement": self.action_movement,
            "action_movement": self.action_movement,
            "locationBackground": self.location_background,
            "location_background": self.location_background,
            "contextLighting": self.context_lighting,
            "context_lighting": self.context_lighting,
            "composition": self.composition,
            "styleCues": self.style_cues,
            "style_cues": self.style_cues,
            "wordSync": self.word_sync.to_dict(),
            "word_sync": self.word_sync.to_dict(),
            "fullPrompt": self.full_prompt,
            "full_prompt": self.full_prompt,
            "imperativeFlowPrompt": self.imperative_flow_prompt,
            "imperative_flow_prompt": self.imperative_flow_prompt,
            "model": self.model,
            "durationSec": self.duration_sec,
            "duration_sec": self.duration_sec,
            "aspectRatio": self.aspect_ratio,
            "aspect_ratio": self.aspect_ratio,
        }


# ---------------------------------------------------------------------------
# Curated DNA Genome Library (The Authoritative Curito Catalog)
# ---------------------------------------------------------------------------

CURITO_GENOME_LIBRARY: Dict[str, CuritoGenome] = {
    # -----------------------------------------------------------------------
    # 1. Visual Design System Output (Materials, 3D Typography, HUDs)
    # -----------------------------------------------------------------------
    "curito_vis_whitecheckered_hud": CuritoGenome(
        id="curito_vis_whitecheckered_hud",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="38.Whitecheckered Transparent HUD",
        dna_snippet=(
            "Translucent holographic search box and data cards with glowing status indicators, "
            "crisp pure-white embossed typography, dark slate studio backdrop with high-contrast "
            "transparent checkerboard backing (.wc-checker-backer) and neon cyan telemetry borders"
        ),
        tags=["hud", "search", "tech", "data", "software", "framework", "metrics"],
        archetype="editorial_tech",
    ),
    "curito_vis_tactile_granite_steel": CuritoGenome(
        id="curito_vis_tactile_granite_steel",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Tactile Granite & Cold Steel Monument",
        dna_snippet=(
            "Massive, rough-hewn weathered granite block with deeply engraved chisel strokes, "
            "cold industrial steel reinforcements, worn textured bridle leather straps, and damp dark earth"
        ),
        tags=["discipline", "struggle", "resilience", "ownership", "grit", "monument", "hardship"],
        archetype="documentary_stoic",
    ),
    "curito_vis_precision_gears_brass": CuritoGenome(
        id="curito_vis_precision_gears_brass",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Precision Brass & Oiled Steel Gear Train",
        dna_snippet=(
            "Intricate interlocking mechanical system of micro-milled brass bevel gears, "
            "oiled blackened steel counterweights, laser-etched titanium dials, and fine grease sheen"
        ),
        tags=["system", "leverage", "feedback", "volume", "scale", "machinery", "engineering"],
        archetype="industrial_editorial",
    ),
    "curito_vis_investigator_vellum_notes": CuritoGenome(
        id="curito_vis_investigator_vellum_notes",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Investigative Vellum & Ethereal Dissolve",
        dna_snippet=(
            "Heavy drafting vellum manuscripts, matte carbon-fiber clipboard, forensic evidentiary tags, "
            "thousands of scattered research sheets and hand-inked diagrams slowly dissolving into ethereal smoke"
        ),
        tags=["research", "information", "overwhelm", "analysis", "evidence", "investigation"],
        archetype="investigative_noir",
    ),
    "curito_vis_vacuum_tube_grid": CuritoGenome(
        id="curito_vis_vacuum_tube_grid",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Asymmetric Filament Grid (100 Experiments)",
        dna_snippet=(
            "Expansive asymmetric 10x10 matrix of vintage hand-blown borosilicate glass vacuum tubes; "
            "99 tubes remain cold, dark, and fractured on a slate baseplate while one central tube ignites"
        ),
        tags=["experimentation", "iteration", "asymmetry", "breakthrough", "testing", "failure", "success"],
        archetype="scientific_editorial",
    ),
    "curito_vis_kinetic_typography_monolith": CuritoGenome(
        id="curito_vis_kinetic_typography_monolith",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Heavy Metallic 3D Typography Monolith",
        dna_snippet=(
            "Heavy solid gunmetal 3D block typography with razor-sharp beveled edges, "
            "micro-machined brushed metal textures, and dynamic metallic specular reflections"
        ),
        tags=["typography", "title", "statement", "truth", "bold", "monolith"],
        archetype="editorial_vox",
    ),
    "curito_vis_editorial_pedestal_orbit": CuritoGenome(
        id="curito_vis_editorial_pedestal_orbit",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Tactile Monolith Pedestal with Dashed Orbit",
        dna_snippet=(
            "Tactile matte-gray 3D anatomical sculpted asset grounded on a floating circular dark charcoal disc "
            "pedestal, encircled by an animated orbiting dashed trajectory ring, set against a warm-gray minimalist studio backdrop"
        ),
        tags=["pedestal", "orbit", "sculpture", "minimalist", "tactile", "editorial"],
        archetype="editorial_luxury",
    ),
    "curito_vis_halftone_triptych_cutout": CuritoGenome(
        id="curito_vis_halftone_triptych_cutout",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Halftone Triptych with Matted Hero Cutout",
        dna_snippet=(
            "3-column vertical photography triptych panels with halftone screen dot raster transitions, "
            "overlaid with a pristine cutout vehicle side-profile casting deep contact drop shadows and telemetry barcode graphics"
        ),
        tags=["triptych", "halftone", "cutout", "automotive", "luxury", "editorial", "barcode"],
        archetype="editorial_luxury",
    ),
    "curito_vis_orthographic_zenith_dial": CuritoGenome(
        id="curito_vis_orthographic_zenith_dial",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Orthographic Zenith Lockup with Compass Dials",
        dna_snippet=(
            "Top-down orthographic zenith perspective of a sculpted performance vehicle with twin hood louvers, "
            "anchored by deep ambient occlusion floor contact shadows, flanked by radial clock hands and precision compass needles"
        ),
        tags=["orthographic", "zenith", "top-down", "compass", "dial", "automotive", "precision"],
        subfamily=FAMILY_GRAPHIC_ELEMENTS,
        archetype="editorial_luxury",
    ),
    "curito_vis_palette_studio_monochrome": CuritoGenome(
        id="curito_vis_palette_studio_monochrome",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Studio Off-White Canvas & Monochrome Palette",
        dna_snippet=(
            "Studio off-white canvas (#ECECEC), charcoal and jet black typography and accents (#111111, #1E1E1E), "
            "clean pure-white surfaces (#FFFFFF), and high-contrast monochrome photography"
        ),
        tags=["palette", "monochrome", "canvas", "charcoal", "off_white", "studio"],
        subfamily=FAMILY_MATERIALITY_TEXTURE,
        archetype="editorial_luxury",
    ),
    "curito_vis_typography_haas_editorial": CuritoGenome(
        id="curito_vis_typography_haas_editorial",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="Neue Haas Grotesk Black & Editorial Italic Serif",
        dna_snippet=(
            "Heavy neo-grotesque sans-serif headline typography (Neue Haas Grotesk Black) paired with "
            "a high-contrast editorial italic serif for secondary accents (Editorial New / Playfair Display), "
            "featuring Z-depth layering where text slides behind vehicle rooflines and subject contours"
        ),
        tags=["typography", "grotesque", "haas", "serif", "italic", "editorial", "z_depth"],
        subfamily=FAMILY_TYPOGRAPHY_HIERARCHY,
        archetype="editorial_luxury",
    ),
    "curito_vis_graphic_ui_bounding_box": CuritoGenome(
        id="curito_vis_graphic_ui_bounding_box",
        category=CATEGORY_VISUAL_DESIGN_SYSTEM,
        name="UI Bounding Boxes & Precision Vector Accents",
        dna_snippet=(
            "Functional UI bounding boxes with resize corner handles and center rotation pins, UPC barcodes, "
            "dashed orbit strokes executing continuous 360-degree rotation, wavy vector hairpins, and sharp 4-point corner star anchors"
        ),
        tags=["ui", "bounding_box", "barcode", "orbit", "star", "vector", "accents"],
        subfamily=FAMILY_GRAPHIC_ELEMENTS,
        archetype="editorial_luxury",
    ),

    # -----------------------------------------------------------------------
    # 2. Lighting and Shading Profile (Chiaroscuro, Volumetrics, Shadows)
    # -----------------------------------------------------------------------
    "curito_lit_chiaroscuro_industrial": CuritoGenome(
        id="curito_lit_chiaroscuro_industrial",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Industrial Chiaroscuro & Dust Shafts",
        dna_snippet=(
            "Dramatic chiaroscuro contrast with intense warm 3200K tungsten spotlight, "
            "volumetric shafts of light cutting through dusty darkroom air, and razor cool cyan rim backlighting"
        ),
        tags=["chiaroscuro", "dramatic", "tungsten", "volumetric", "contrast", "cinematic"],
        archetype="editorial_documentary",
    ),
    "curito_lit_double_state_shadow": CuritoGenome(
        id="curito_lit_double_state_shadow",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Double-State Cast Shadow (Contact + Throw)",
        dna_snippet=(
            "Double-state cast shadow mechanics featuring 70% dense ambient occlusion contact shadow "
            "at 3px offset paired with a 25% directional throw shadow extending at 35px offset with 40px soft feather"
        ),
        tags=["shadow", "depth", "realism", "physics", "elevation", "grounding"],
        archetype="editorial_vox",
    ),
    "curito_lit_trailing_shadow_vector": CuritoGenome(
        id="curito_lit_trailing_shadow_vector",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Trailing Shadow Vector & Motion Drag",
        dna_snippet=(
            "Dynamic directional shadow vector lagging dynamically behind high-speed lateral motion vectors, "
            "compressing and snapping into dense dual-state contact alignment upon final deceleration"
        ),
        tags=["shadow", "velocity", "vector", "momentum", "speed"],
        archetype="motion_graphics",
    ),
    "curito_lit_focused_spotlight_isolation": CuritoGenome(
        id="curito_lit_focused_spotlight_isolation",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Focal Spotlight Isolation (Void Falloff)",
        dna_snippet=(
            "Single high-intensity focused circular spotlight casting harsh theatrical illumination "
            "on the primary asset while peripheral elements plunge into complete obsidian darkness"
        ),
        tags=["spotlight", "isolation", "focus", "contrast", "void", "minimalist"],
        archetype="minimalist_noir",
    ),
    "curito_lit_golden_tungsten_luminescence": CuritoGenome(
        id="curito_lit_golden_tungsten_luminescence",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Brilliant Golden Tungsten Luminescence",
        dna_snippet=(
            "Deep shadowed ambient environment pierced by brilliant 2700K incandescent gold-white point luminescence, "
            "casting long dramatic geometric shadows and subtle lens flaring across surrounding surfaces"
        ),
        tags=["gold", "glow", "breakthrough", "illumination", "energy", "incandescent"],
        subfamily=FAMILY_KEY_LIGHTING,
        archetype="warm_cinematic",
    ),
    "curito_lit_directional_studio_drop": CuritoGenome(
        id="curito_lit_directional_studio_drop",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Top-Down Directional Studio Drop Shadow",
        dna_snippet=(
            "Top-down, slightly forward directional studio light casting clean 90-degree to 110-degree vertical drop shadows "
            "with crisp edge retention and zero ambient light pollution"
        ),
        tags=["lighting", "studio", "directional", "top_down", "vertical", "drop_shadow"],
        subfamily=FAMILY_KEY_LIGHTING,
        archetype="editorial_luxury",
    ),
    "curito_lit_shadow_hierarchy_double_layer": CuritoGenome(
        id="curito_lit_shadow_hierarchy_double_layer",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Double-Layer Contact + Diffuse Shadow Hierarchy",
        dna_snippet=(
            "Double-layer shadow hierarchy: tight dark ambient occlusion contact shadow (#000000, 60% opacity, 4px blur) "
            "paired with an extended soft-diffuse drop shadow (#000000, 25% opacity, 30px blur, Y: 15px) for foreground assets, "
            "and crisp paper-cutout elevation shadow (#000000, 20% opacity, 12px blur, Y: 6px) for graphic text and cards"
        ),
        tags=["shadow", "ao", "contact", "elevation", "double_layer", "hierarchy", "diffuse"],
        subfamily=FAMILY_SHADOW_HIERARCHY,
        archetype="editorial_luxury",
    ),
    "curito_lit_render_quality_matte_clearcoat": CuritoGenome(
        id="curito_lit_render_quality_matte_clearcoat",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Matte Non-Reflective Canvas with Selective Clearcoat",
        dna_snippet=(
            "Matte non-reflective background texture with metallic and clearcoat reflections isolated strictly "
            "to vehicle paint, glass windows, and headlights, maintaining razor tactile contrast against off-white background"
        ),
        tags=["materiality", "matte", "clearcoat", "specular", "reflection", "texture"],
        subfamily=FAMILY_MATERIALITY_TEXTURE,
        archetype="editorial_luxury",
    ),

    # -----------------------------------------------------------------------
    # 3. Camera Motion Choreography (Lenses, Drifts, Impacts, Dives)
    # -----------------------------------------------------------------------
    "curito_cam_35mm_anamorphic_drift": CuritoGenome(
        id="curito_cam_35mm_anamorphic_drift",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="35mm Anamorphic Continuous Sub-Pixel Drift",
        dna_snippet=(
            "Vertical 9:16 composition captured on 35mm anamorphic lens with shallow depth of field, "
            "smooth oval anamorphic bokeh, continuous anti-stagnation sub-pixel drift (scaling 100% to 101.8%), "
            "24fps cadence, and subtle Kodak 5219 film grain"
        ),
        tags=["camera", "anamorphic", "drift", "35mm", "film_grain", "cinematic", "vertical"],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="editorial_documentary",
    ),
    "curito_cam_rack_focus_dive": CuritoGenome(
        id="curito_cam_rack_focus_dive",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Macro Rack-Focus Dive (Scale Down & Snap)",
        dna_snippet=(
            "High-speed macro rack-focus dive rapidly scaling down 125% to 100% over 12 frames "
            "while optical blur transitions from 50px Gaussian blur to pin-sharp focus with anamorphic flare"
        ),
        tags=["camera", "rack_focus", "dive", "zoom", "sharp", "reveal", "speed"],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="editorial_vox",
    ),
    "curito_cam_canvas_reaction_jolt": CuritoGenome(
        id="curito_cam_canvas_reaction_jolt",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Canvas Reaction Jolt & Weight Transfer",
        dna_snippet=(
            "One-frame 3px downward camera reaction jolt on physical asset impact, transferring tangible weight "
            "and inertia to the scene before settling into smooth rotational damped oscillation"
        ),
        tags=["camera", "jolt", "impact", "shake", "weight", "physics", "reaction"],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="high_impact",
    ),
    "curito_cam_orbital_tracking_pan": CuritoGenome(
        id="curito_cam_orbital_tracking_pan",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Continuous Smooth Orbital Pan",
        dna_snippet=(
            "Slow continuous orbital camera pan gracefully sweeping around the central subject, "
            "revealing dimensional parallax depth between foreground typography and background elements"
        ),
        tags=["camera", "orbit", "pan", "parallax", "smooth", "3d"],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="fluid_3d",
    ),
    "curito_cam_flat_perspective_50_85mm": CuritoGenome(
        id="curito_cam_flat_perspective_50_85mm",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Flat-Perspective 50mm-85mm Lens (Minimal Distortion)",
        dna_snippet=(
            "Simulated 50mm-85mm flat-perspective focal length with zero barrel distortion, capturing orthographic geometry "
            "with architectural precision, crisp edges, and zero fisheye warping in vertical 9:16 framing"
        ),
        tags=["lens", "50mm", "85mm", "flat_perspective", "orthographic", "geometry", "precision"],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="editorial_luxury",
    ),
    "curito_cam_centered_anchors_whip_snaps": CuritoGenome(
        id="curito_cam_centered_anchors_whip_snaps",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Centered Static Anchors with Directional Whip-Pans",
        dna_snippet=(
            "Centered static anchors punctuated by high-velocity directional whip-pans and snap-zooms between scene transitions, "
            "maintaining micro-drift scale pushes (100% to 103%) during holds to eliminate visual stagnation"
        ),
        tags=["camera", "whip_pan", "snap_zoom", "static_anchor", "micro_drift", "transition"],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="editorial_luxury",
    ),
    "curito_cam_motion_curves_snap_decel": CuritoGenome(
        id="curito_cam_motion_curves_snap_decel",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Snap Deceleration Cubic-Bezier(0.16, 1, 0.3, 1)",
        dna_snippet=(
            "Aggressive ease-in and snap deceleration governed by cubic-bezier(0.16, 1, 0.3, 1), zero linear movement, "
            "delivering tight 6-10 frame reveals with physical kinetic momentum and instant locked settles"
        ),
        tags=["motion_curve", "bezier", "snap", "deceleration", "kinetics", "timing"],
        subfamily=FAMILY_MOTION_CURVES,
        archetype="editorial_luxury",
    ),

    # -----------------------------------------------------------------------
    # 4. Scene-by-Scene Asset & Animation Breakdown (Spatial Physics & Reveals)
    # -----------------------------------------------------------------------
    "curito_scene_slapdrop_bounce": CuritoGenome(
        id="curito_scene_slapdrop_bounce",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="The Slap-Drop with Contact Bounce",
        dna_snippet=(
            "The Slap-Drop asset introduction pushing downward along Z-axis with exponential decrescendo, "
            "executing a 2-frame 3% scale squash on impact followed by subtle contact bounce and pendulum settle"
        ),
        tags=["reveal", "entrance", "drop", "bounce", "squash", "impact", "physics"],
        archetype="editorial_vox",
    ),
    "curito_scene_3d_off_axis_swing": CuritoGenome(
        id="curito_scene_3d_off_axis_swing",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="3D Off-Axis Hinged Swing",
        dna_snippet=(
            "The 3D Off-Axis Swing with pivot anchor pinned to the outer edge, swinging in with dynamic perspective "
            "from 80 degrees down to 0 degrees, projecting dynamic elevation shadows tracking Z-distance"
        ),
        tags=["reveal", "entrance", "swing", "3d", "rotation", "perspective"],
        archetype="editorial_vox",
    ),
    "curito_scene_lateral_friction_slide": CuritoGenome(
        id="curito_scene_lateral_friction_slide",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Lateral Friction Slide (Dossier Reveal)",
        dna_snippet=(
            "The Lateral Friction Slide entering horizontally at maximum initial velocity with zero ease-in, "
            "gliding against 70% simulated physical friction before locking cleanly into position"
        ),
        tags=["reveal", "slide", "friction", "dossier", "velocity", "document"],
        archetype="investigative_editorial",
    ),
    "curito_scene_asymmetric_track_matte": CuritoGenome(
        id="curito_scene_asymmetric_track_matte",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Asymmetric Track Matte Unfurl",
        dna_snippet=(
            "Asymmetric crop track-matte unfurl: a razor 1px neon hairline border appears first, "
            "then expands horizontally 0% to 100% followed by vertical wipe 20% to 100% to reveal container contents"
        ),
        tags=["reveal", "matte", "unfurl", "wipe", "mask", "geometric"],
        archetype="minimalist_graphic",
    ),
    "curito_scene_background_defocus_isolation": CuritoGenome(
        id="curito_scene_background_defocus_isolation",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Background Defocus Isolation (Target Spotlight)",
        dna_snippet=(
            "Background Defocus Isolation applying 25px Gaussian blur and 15% brightness dip across background video, "
            "directing 100% viewer optical attention toward the foreground animated asset"
        ),
        tags=["isolation", "blur", "defocus", "contrast", "focus", "broll"],
        archetype="editorial_documentary",
    ),
    "curito_scene_polarizing_bevel_elevation": CuritoGenome(
        id="curito_scene_polarizing_bevel_elevation",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Polarizing Bevel Card Elevation",
        dna_snippet=(
            "The Polarizing Bevel Card Elevation: asset elevates forward along Z-axis into frame with chamfered metallic "
            "bevel borders catching edge highlights, casting expanding ambient occlusion onto the backdrop"
        ),
        tags=["card", "elevation", "bevel", "chamfer", "badge", "float"],
        archetype="editorial_vox",
    ),
    "curito_scene_vector_bounding_box_ghost": CuritoGenome(
        id="curito_scene_vector_bounding_box_ghost",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Vector Bounding Box with Kinetic Ghosting",
        dna_snippet=(
            "Vector UI dashed bounding box with circular corner anchor handles, containing high-contrast italic serif typography "
            "executing multi-pass kinetic duplicate ghosting and drop-shadow displacement"
        ),
        tags=["bounding_box", "vector", "ghosting", "displacement", "anchor", "kinetic"],
        archetype="editorial_luxury",
    ),
    "curito_scene_halftone_dot_wipe": CuritoGenome(
        id="curito_scene_halftone_dot_wipe",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Halftone Dot Screen Raster Wipe",
        dna_snippet=(
            "High-contrast halftone dot screen raster wipe dissolving dynamically across multiple vertical card layers, "
            "revealing underlying photographic textures with tactile print-press authenticity"
        ),
        tags=["halftone", "raster", "wipe", "transition", "print", "screen"],
        subfamily=FAMILY_TRANSITIONS,
        archetype="editorial_luxury",
    ),
    "curito_scene_01_the_brain": CuritoGenome(
        id="curito_scene_01_the_brain",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 1: The Brain Orbit Drift (0:00-0:02)",
        dna_snippet=(
            "Centered circular medallion with 3D monochrome matte-gray brain model with high AO detail on circular charcoal disc, "
            "concentric dashed vector ring rotating continuous 360-degrees clockwise on a 4s cycle, subtle 3D hover drift, "
            "headline anchored top-left, italic tagline bottom-center, text snapping up via Y-axis translate (+20px to 0px, opacity 0 to 100)"
        ),
        tags=["scene_1", "brain", "orbit", "medallion", "monochrome", "3d", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_02_75_years_mask": CuritoGenome(
        id="curito_scene_02_75_years_mask",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 2: 75 Years Number Mask Whip-Zoom (0:03-0:04)",
        dna_snippet=(
            "Massive centered alpha track-matte stencil of numeral glyphs '75' split across frame with barcode graphic top-center, "
            "interior tracking footage of a Porsche 911 front quarter playing at 1.2x speed with active headlight flare, "
            "exterior numbers casting layered cast-shadow onto background plane, whip-zoom punch into the '75'"
        ),
        tags=["scene_2", "number_mask", "75_years", "track_matte", "whip_zoom", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_03_track_card": CuritoGenome(
        id="curito_scene_03_track_card",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 3: Track Card Jump-Cut (0:05-0:07)",
        dna_snippet=(
            "9:16 framed vertical video card with 1px border and corner black chevron/star spikes elevated via high-def diffuse drop shadow, "
            "showing B&W archival racing track footage in natural overcast daylight, card scales down 110% to 100% on enter, "
            "rapid jump-cut between vintage track sequences with corner star accents rotating 45-degrees abruptly"
        ),
        tags=["scene_3", "track_card", "jump_cut", "archival", "star_spikes", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_04_kinetic_editorial_text": CuritoGenome(
        id="curito_scene_04_kinetic_editorial_text",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 4: Kinetic Editorial UI Transformer Text (0:08-0:10)",
        dna_snippet=(
            "Two stacked UI transformer bounding boxes centered vertically with dashed vector strokes, 4 solid corner handles, "
            "and center rotation pin; isolated italic serif text layers popping with elastic spring scale (0.9 to 1.0), "
            "bottom box entering 6 frames later, bounding handles snapping outward via path trim"
        ),
        tags=["scene_4", "transformer", "bounding_box", "spring_scale", "path_trim", "editorial_text", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_05_3d_studio_showcase": CuritoGenome(
        id="curito_scene_05_3d_studio_showcase",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 5: 3D Studio Showcase Z-Depth Cutout (0:10-0:14)",
        dna_snippet=(
            "Isolated cutout of modern white Porsche 911 with driver door ajar centered in lower third over perspective floor ellipse, "
            "high-key overhead softbox casting gradient reflection lines along shoulder panels, car translating subtly toward viewer, "
            "headline 'Iconic Design' scaled large across upper-mid third sliding behind the car roof demonstrating physical Z-depth layering"
        ),
        tags=["scene_5", "studio_showcase", "car_cutout", "door_ajar", "z_depth", "overhead_softbox", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_06_triptych_collage": CuritoGenome(
        id="curito_scene_06_triptych_collage",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 6: Triptych Halftone Stagger Slide (0:14-0:17)",
        dna_snippet=(
            "Three-column vertical backdrop strips with halftone screen textures creating back-contrast, full-width side-profile cutout "
            "of Porsche GT3 RS with carbon wing in foreground with rim lighting on roofline, columns stagger-sliding down by 30px, "
            "foreground vehicle sliding left-to-right into frame with hard snap deceleration"
        ),
        tags=["scene_6", "triptych", "halftone", "stagger_slide", "gt3_rs", "side_profile", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_07_top_down_vertical_drive": CuritoGenome(
        id="curito_scene_07_top_down_vertical_drive",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 7: Top-Down Vertical Drive (0:18-0:21)",
        dna_snippet=(
            "Isolated bird's-eye orthographic cut of white Porsche GT3 RS with carbon bonnet stripes and massive wing, four corner framing ticks, "
            "orthographic top-down lighting casting clean even drop shadow on both sides of chassis, words 'This isn't Just A car It's a Statement' "
            "positioned orthogonally around vehicle hull, vehicle driving vertically along Y-axis from center to top edge as surrounding text reveals sequentially"
        ),
        tags=["scene_7", "top_down", "vertical_drive", "orthographic", "bonnet_stripes", "orthogonal_text", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),
    "curito_scene_08_brand_lockup_sweep": CuritoGenome(
        id="curito_scene_08_brand_lockup_sweep",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Scene 8: Brand Lockup & Aerodynamic Sweep (0:21-0:23)",
        dna_snippet=(
            "Center-locked brand identity featuring vector 'Porsche' logotype and italic subtext 'There is no Substitute', "
            "aerodynamic curved vector ribbon sweeping across frame from top-right to bottom-center with dynamic whip-pan settle, "
            "high-contrast black typography with soft ambient occlusion drop shadow against pure off-white (#ECECEC) canvas"
        ),
        tags=["scene_8", "brand_lockup", "logotype", "aero_ribbon", "whip_pan_settle", "substitute", "porsche_ref"],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="editorial_luxury",
    ),

    # -----------------------------------------------------------------------
    # S-TIER GENOME: Vertical Bottom-Up Emergence + Directional Motion Blur
    # Registered: 2026-09-15 — per user directive on kinematic entry direction
    # -----------------------------------------------------------------------
    "curito_scene_vertical_bottom_emergence_motionblur": CuritoGenome(
        id="curito_scene_vertical_bottom_emergence_motionblur",
        category=CATEGORY_SCENE_ASSET_BREAKDOWN,
        name="Vertical Bottom-Up Emergence with Directional Motion Blur (S-Tier)",
        dna_snippet=(
            "The primary hero asset initiates from a fully submerged off-screen position below the lower "
            "frame boundary (Y: +120% viewport), propelled upward along the vertical axis with a steep "
            "power4.out cubic deceleration curve, decelerating sharply into its final locked centroid "
            "position. The asset obeys strict classical rigid-body physics as a single cohesive solid "
            "topological manifold: zero doubling, zero ghosted duplication, zero mesh fission, zero UV seam "
            "sliding, zero unphysical cloning, and zero re-convergence artifacts. All material and texture "
            "coordinates remain pinned and invariant to the physical geometry throughout motion. "
            "During the upward travel phase, a directional slow-shutter motion blur is applied "
            "along the Y-axis: the asset exhibits 28-frame trailing edge smear with 85% opacity falloff "
            "and directional elongation (scaleY: 1.12 to 1.0) simulating physical inertia. As the asset "
            "locks into position, the trailing blur resolves to zero and a tight ambient occlusion contact "
            "shadow expands beneath it from scale(0.4) to scale(1.0). The total entry duration spans "
            "0.0s to 1.2s with the visual apex locked at 1.0s. Zero horizontal drift during the upward "
            "travel phase. Camera is locked on a fixed tripod with no compensatory pan."
        ),
        tags=[
            "entrance", "bottom_up", "vertical", "emergence", "motion_blur",
            "directional_blur", "slow_shutter", "y_axis", "deceleration", "power4",
            "inertia", "shadow_expand", "unitary_manifold", "anti_doubling", "s_tier",
        ],
        subfamily=FAMILY_SCENE_BREAKDOWN,
        archetype="high_impact",
    ),

    # -----------------------------------------------------------------------
    # S-TIER GENOME: Anamorphic Rack-Focus DoF Stratification
    # Registered: 2026-09-15 — GSAP cinema lens system, user-specified
    # -----------------------------------------------------------------------
    "curito_cam_anamorphic_rackfocus_dof_stratification": CuritoGenome(
        id="curito_cam_anamorphic_rackfocus_dof_stratification",
        category=CATEGORY_CAMERA_MOTION_CHOREOGRAPHY,
        name="Anamorphic Rack-Focus DoF Stratification + Parallax Convergence (S-Tier)",
        dna_snippet=(
            "The scene is treated as three-dimensional focal-plane stratified space rendered through an "
            "ultra-wide aperture anamorphic cinema lens (f/1.2 equivalent). Phase 1 — Optical Strike "
            "(0.0s–1.0s): the global scene opens overexposed and in total heavy defocus "
            "(blur: 36px, brightness: 1.6, scale: 1.15), simulating a lens iris wide-open into "
            "volumetric backlight blowout. The primary focal subject resolves first at 0.2s via a "
            "power4.out rack-focus pull (blur: 36px → 0px, Y: +35px → 0px), while flanking secondary "
            "elements remain out-of-focus low-luminance bokeh (brightness: 0.6). "
            "Phase 2 — Depth-of-Field Pull (0.7s–1.8s): the focal plane racks backward into the scene; "
            "left and right flanking assets converge inward from peripheral anamorphic distortion positions "
            "(x: ±45px → 0px) while resolving from bokeh to tack-sharp, mimicking anamorphic lens "
            "compression and focal-length foreshortening. "
            "Phase 3 — Breathing Hold (1.8s–4.5s): the composition enters low-frequency out-of-phase "
            "sine.inOut micro-drift float (scale: 1.02 → 0.98, sine period: 3.2s) preserving cinematic "
            "presence and preventing visual dead-stops. Contact occlusion shadows tighten and snap to "
            "ground plane. "
            "Phase 4 — Defocus Dissolve Outro (4.5s–6.0s): the camera racks focus past the subjects "
            "into full lens blowout (blur: 0px → 40px); primary subject defocuses first, secondary "
            "elements follow with a 100ms stagger, collapsing the lockup back into pure optical atmosphere. "
            "Oval anamorphic bokeh coronas and horizontal lens streak flares are maintained throughout."
        ),
        tags=[
            "rack_focus", "dof", "stratification", "anamorphic", "bokeh", "f1.2",
            "focal_plane", "parallax_convergence", "lens_blowout", "breathing_hold",
            "defocus_outro", "sine_drift", "gsap", "cinema_lens", "s_tier",
        ],
        subfamily=FAMILY_CAMERA_CHOREOGRAPHY,
        archetype="editorial_documentary",
    ),

    # -----------------------------------------------------------------------
    # S-TIER GENOME: Volumetric Bloom Atmospheric Entry + Grounding Occlusion
    # Registered: 2026-09-15 — atmospheric blowout to grounded occlusion phase
    # -----------------------------------------------------------------------
    "curito_lit_volumetric_bloom_to_grounded_occlusion": CuritoGenome(
        id="curito_lit_volumetric_bloom_to_grounded_occlusion",
        category=CATEGORY_LIGHTING_SHADING_PROFILE,
        name="Volumetric Bloom Blowout → Grounded Ambient Occlusion (S-Tier)",
        dna_snippet=(
            "The initial frame features an oversaturated optical volumetric backlight bloom "
            "(scale: 1.4, opacity: 0.8) simulating an overexposed lens flare incident that "
            "diffuses all spatial depth cues and ungrounds all assets. As the focal rack resolves, "
            "the volumetric bloom compresses and settles into a controlled ambient backdrop halo "
            "(scale: 1.0, opacity: 0.4). Simultaneously, the ground-plane contact shadow scales "
            "from a diffuse underlit blob (scaleX: 0.4, scaleY: 0.4, blur: 18px stdDeviation) "
            "to a tight elliptical ambient occlusion shadow (scaleX: 1.0, scaleY: 1.0, "
            "blur: 6px stdDeviation), physically anchoring the asset to the spatial plane "
            "with tactile photographic realism. On outro, the bloom re-expands to scale: 1.6 "
            "and fades to opacity: 0, pulling the scene back into pure optical atmosphere."
        ),
        tags=[
            "bloom", "volumetric", "backlight", "flare", "occlusion", "contact_shadow",
            "grounding", "atmospheric", "blowout", "elliptical_ao", "s_tier",
        ],
        subfamily=FAMILY_KEY_LIGHTING,
        archetype="cinematic_vox",
    ),
}


# ---------------------------------------------------------------------------
# Background Treatment Registry
# ---------------------------------------------------------------------------
# Canonical ontology of selectable background treatments for the diffusion
# asset plate. Gemini selects a treatment ID from this registry based on
# semantic context. The stitcher injects the selected snippet into part 3
# (Location / Background) of the 6-part Google Flow formula.
#
# Selection is NEVER hardcoded — always call `select_background_treatment()`.
# ---------------------------------------------------------------------------

@dataclass
class BackgroundTreatment:
    """A canonical background canvas treatment for the diffusion asset plate."""
    id: str
    name: str
    dna_snippet: str                  # Verbatim text injected into Location/Background
    tags: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    archetype: str = "editorial"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


BACKGROUND_TREATMENT_REGISTRY: Dict[str, "BackgroundTreatment"] = {

    # ── BG-01 ─────────────────────────────────────────────────────────────────
    # Pre-existing canonical. Tactile newsprint / halftone dot raster screen.
    "halftone_raster_canvas": BackgroundTreatment(
        id="halftone_raster_canvas",
        name="Standalone Halftone Dot Raster Screen",
        dna_snippet=(
            "Pristine matte off-white (#ECECEC) tactile paper canvas with a subtle repeating "
            "micro-halftone dot raster screen (4–6 pt dot pitch, 85 lpi), fine 35mm film grain "
            "overlay (Multiply blend, opacity 5–8%), clean geometric negative space reserving "
            "upper 45% as uncluttered margin for downstream typography"
        ),
        tags=["halftone", "raster", "newsprint", "editorial", "paper", "monochrome", "swiss"],
        use_cases=[
            "High-contrast monochrome mechanical artifacts",
            "Desaturated brass or carbon steel subjects",
            "Swiss editorial newsprint and tactile dot pattern",
            "Any scene requiring maximum foreground–background contrast separation",
            "Default when no other treatment is strongly indicated",
        ],
        archetype="editorial_swiss",
    ),

    # ── BG-02 ─────────────────────────────────────────────────────────────────
    "luxury_editorial_sunlight_canvas": BackgroundTreatment(
        id="luxury_editorial_sunlight_canvas",
        name="Luxury Editorial Sunlight Canvas",
        dna_snippet=(
            "Clean off-white textured paper with subtle fibrous grain and soft diagonal sunlight "
            "shadows falling across the entire canvas at a 25–35 degree rake, casting warm luminous "
            "bands of diffuse amber-ivory light separated by cooler shadow troughs, creating a luxury "
            "magazine editorial aesthetic with spacious negative space and a refined monochrome "
            "palette — generous breathing room, no furniture, no hard edges"
        ),
        tags=["luxury", "editorial", "sunlight", "shadows", "magazine", "warm", "paper", "grain"],
        use_cases=[
            "Warm, aspirational, or premium lifestyle transcripts",
            "Subjects with polished brass, gold-toned, or ivory material finishes",
            "Interview moments expressing achievement, aspiration, or refinement",
            "Scenes requiring warm atmospheric quality rather than cold Swiss neutrality",
        ],
        archetype="editorial_luxury",
    ),

    # ── BG-03 ─────────────────────────────────────────────────────────────────
    "newspaper_collage_deconstructed": BackgroundTreatment(
        id="newspaper_collage_deconstructed",
        name="Newspaper Collage / Deconstructed Print",
        dna_snippet=(
            "Low-contrast newspaper collage in empty areas — old scares, paper grunge print texture, "
            "coarse halftone grain, rough torn edges, microtext spread randomly across the negative "
            "space, vertical typographic columns suggesting deconstructed broadsheet layout, abstract "
            "unreadable green-teal inked signature mark at the lower edge, overall patina of archival "
            "documentary rawness and analog imperfection"
        ),
        tags=["newspaper", "collage", "grunge", "deconstructed", "microtext", "analog", "teal", "raw"],
        use_cases=[
            "Gritty, counter-cultural, or anti-establishment transcript themes",
            "Subjects with raw steel, oxidized iron, or industrial finish",
            "Moments of disruption, deconstruction, or systemic challenge",
            "Analog / archival documentary aesthetic",
        ],
        archetype="documentary_raw",
    ),

    # ── BG-04 ─────────────────────────────────────────────────────────────────
    "modern_swiss_museum_poster": BackgroundTreatment(
        id="modern_swiss_museum_poster",
        name="Modern Swiss Editorial / Museum Poster",
        dna_snippet=(
            "Modern Swiss editorial design backdrop — luxury museum poster aesthetic, dramatic high-key "
            "directional lighting raking the canvas from the upper-left at 45 degrees, deep shadow zones "
            "creating architectural contrast, ultra-sharp micro-stippled grid texture on the canvas "
            "surface, vertical 9:16 compositional discipline with a dominant center axis, maximum "
            "chromatic restraint (near-monochrome palette, single accent hue), 8K perceptual clarity"
        ),
        tags=["swiss", "museum", "poster", "dramatic", "high_contrast", "grid", "monochrome", "editorial"],
        use_cases=[
            "Institutional, authoritative, or thought-leadership transcript themes",
            "Subjects with ultra-sharp geometric geometry (track switches, knife switches, Geneva drives)",
            "Maximum visual authority and precision — no warmth, no softness",
            "Vertical compositions demanding architectural graphic hierarchy",
        ],
        archetype="editorial_institutional",
    ),
}


def select_background_treatment(
    use_case_hint: str = "",
    tags: Optional[List[str]] = None,
    registry: Optional[Dict[str, "BackgroundTreatment"]] = None,
) -> "BackgroundTreatment":
    """Select the most contextually appropriate background treatment.

    Args:
        use_case_hint: Free-text description of the scene / transcript theme.
        tags: Optional list of semantic tags to match against registry entries.
        registry: Optional registry override; defaults to BACKGROUND_TREATMENT_REGISTRY.

    Returns:
        The best-matching BackgroundTreatment, defaulting to halftone_raster_canvas.
    """
    reg = registry or BACKGROUND_TREATMENT_REGISTRY
    if not use_case_hint and not tags:
        return reg["halftone_raster_canvas"]

    hint_tokens = set(re.findall(r"\w+", use_case_hint.lower()))
    tag_tokens = {t.lower() for t in (tags or [])}
    query = hint_tokens | tag_tokens

    best_id = "halftone_raster_canvas"
    best_score = -1

    for entry in reg.values():
        entry_tokens = {t.lower() for t in entry.tags}
        entry_tokens |= set(re.findall(r"\w+", entry.name.lower()))
        entry_tokens |= set(re.findall(r"\w+", entry.id.lower()))
        for uc in entry.use_cases:
            entry_tokens |= set(re.findall(r"\w+", uc.lower()))
        overlap = len(query & entry_tokens)
        if overlap > best_score:
            best_score = overlap
            best_id = entry.id

    return reg[best_id]


# ---------------------------------------------------------------------------
# Motion Treatment Registry
# ---------------------------------------------------------------------------
# Canonical ontology of asset-level motion blur / soft-entry optic treatments.
# Selected contingent on the kinetic class of the hero artifact and movement type.
# Injected into the assembled diffusion prompt as an additive motion-optics clause.
#
# Selection is NEVER hardcoded — always call `select_motion_treatment()`.
# ---------------------------------------------------------------------------

@dataclass
class MotionTreatment:
    """A canonical motion blur / soft-entry optic treatment for the diffusion asset."""
    id: str
    name: str
    dna_snippet: str                  # Additive clause appended to the assembled prompt
    tags: List[str] = field(default_factory=list)
    kinetic_classes: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


MOTION_TREATMENT_REGISTRY: Dict[str, "MotionTreatment"] = {

    # ── MT-01 ─────────────────────────────────────────────────────────────────
    "defocus_blur": MotionTreatment(
        id="defocus_blur",
        name="Defocus Blur — Optical Rack-Focus Reveal",
        dna_snippet=(
            "Asset enters frame through a deliberate optical rack-focus transition: begins in soft "
            "lens defocus (circular bokeh coronas on specular highlights, f/1.4 equivalent depth), "
            "progressively sharpening to tack-sharp clinical focus precisely at the sync hit, "
            "simulating a mechanical lens-breathing pull-focus gesture on a prime cinema lens"
        ),
        tags=["defocus", "rack_focus", "lens_breathing", "reveal", "soft_entry", "prime", "focus"],
        kinetic_classes=["static_reveal", "rack_focus", "scale_tilt", "deliberate_settle"],
        use_cases=[
            "Hero artifact reveals where the asset appears to crystallize into sharpness",
            "Inflection moments of clarity, decision, or definitive selection",
            "Balance scale or knife switch settling into locked position",
            "Any reveal requiring cinematic prestige and deliberate pacing",
        ],
    ),

    # ── MT-02 ─────────────────────────────────────────────────────────────────
    "gaussian_blur": MotionTreatment(
        id="gaussian_blur",
        name="Gaussian Blur — Soft Entry / Soft Exit",
        dna_snippet=(
            "Asset transitions into and out of the frame through a silky Gaussian soft-fade: "
            "appearing from a luminous diffuse haze (uniform Gaussian softness, 18px radius equivalent) "
            "and resolving to full material sharpness across a 0.8s easing window, then dissolving "
            "out symmetrically — a dreamlike floating materialization with no hard cuts"
        ),
        tags=["gaussian", "soft_entry", "soft_exit", "fade", "haze", "ethereal", "smooth"],
        kinetic_classes=["fade_in", "gentle_float", "ambient_reveal", "aspirational"],
        use_cases=[
            "Warm, aspirational, or emotionally resonant transcript moments",
            "Luxury editorial sunlight canvas backgrounds",
            "Subjects with polished or translucent material surfaces",
            "Scenes where a mechanical reveal would break tonal warmth",
        ],
    ),

    # ── MT-03 ─────────────────────────────────────────────────────────────────
    "bokeh_blur": MotionTreatment(
        id="bokeh_blur",
        name="Bokeh Blur — Background Separation / Depth-of-Field Isolation",
        dna_snippet=(
            "Background canvas rendered with smooth spherical bokeh (f/1.2 equivalent aperture) — "
            "specular highlights in the negative-space background dissolve into large circular bokeh "
            "coronas (60–120px diameter), creating a cinematic depth plane that isolates the hero "
            "artifact on a tack-sharp focal plane floating against the diffuse luminous background void; "
            "foreground subject has zero motion blur, background has maximum separation softness"
        ),
        tags=["bokeh", "depth_of_field", "dof", "isolation", "background_separation", "aperture"],
        kinetic_classes=["static_hero", "floating_hold", "macro_close_up", "prestige_isolation"],
        use_cases=[
            "Maximum foreground-to-background separation for prestige product aesthetic",
            "Scenes where background texture risks competing with the hero artifact",
            "Subjects with intricate surface detail requiring full focal attention",
            "Newspaper collage or sunlight canvas backgrounds needing depth isolation",
        ],
    ),

    # ── MT-04 ─────────────────────────────────────────────────────────────────
    "slow_shutter_motion_blur": MotionTreatment(
        id="slow_shutter_motion_blur",
        name="Slow Shutter — Dynamic Motion Blur (Kinetic Streak)",
        dna_snippet=(
            "Dynamic mechanical kinetics captured with simulated slow-shutter motion blur: "
            "fast-moving elements (rotating shafts, sweeping beams, snapping levers) trail "
            "directional motion streaks (10–20px equivalent at 1/30s shutter simulation) "
            "in the axis of their primary velocity vector, while stationary structural elements "
            "remain tack-sharp — conveying authoritative mechanical energy and high-torque "
            "kinetic momentum without geometric melting or temporal ambiguity"
        ),
        tags=["motion_blur", "slow_shutter", "kinetic", "streak", "dynamic", "torque", "velocity"],
        kinetic_classes=["high_speed_rotation", "lever_snap", "beam_sweep", "mechanical_strike"],
        use_cases=[
            "High-torque mechanical snap events (knife switch clamping, balance beam tilting)",
            "Geneva drive indexing at speed",
            "Subjects with a fast rotational or linear kinematic component",
            "Moments of decisive mechanical authority requiring visceral energy",
        ],
    ),
}


def select_motion_treatment(
    use_case_hint: str = "",
    kinetic_class: str = "",
    tags: Optional[List[str]] = None,
    registry: Optional[Dict[str, "MotionTreatment"]] = None,
) -> "MotionTreatment":
    """Select the most contextually appropriate motion treatment.

    Args:
        use_case_hint: Free-text description of the scene / transcript theme.
        kinetic_class: The asset's movement class (e.g. 'rack_focus', 'high_speed_rotation').
        tags: Optional semantic tags to match.
        registry: Optional registry override; defaults to MOTION_TREATMENT_REGISTRY.

    Returns:
        The best-matching MotionTreatment, defaulting to defocus_blur.
    """
    reg = registry or MOTION_TREATMENT_REGISTRY
    if not use_case_hint and not kinetic_class and not tags:
        return reg["defocus_blur"]

    hint_tokens = set(re.findall(r"\w+", use_case_hint.lower()))
    kinetic_tokens = set(re.findall(r"\w+", kinetic_class.lower()))
    tag_tokens = {t.lower() for t in (tags or [])}
    query = hint_tokens | kinetic_tokens | tag_tokens

    best_id = "defocus_blur"
    best_score = -1

    for entry in reg.values():
        entry_tokens = {t.lower() for t in entry.tags}
        entry_tokens |= set(re.findall(r"\w+", entry.name.lower()))
        entry_tokens |= set(re.findall(r"\w+", entry.id.lower()))
        for kc in entry.kinetic_classes:
            entry_tokens |= set(re.findall(r"\w+", kc.lower()))
        for uc in entry.use_cases:
            entry_tokens |= set(re.findall(r"\w+", uc.lower()))
        overlap = len(query & entry_tokens)
        if overlap > best_score:
            best_score = overlap
            best_id = entry.id

    return reg[best_id]


# ---------------------------------------------------------------------------
# Mathematical Timestamp & Word-Sync Calculator
# ---------------------------------------------------------------------------

class CuritoWordSyncCalculator:
    """Calculates millisecond-accurate timestamp sync for animation cues.
    
    Given monologue transcript timepoints (e.g. 5:30) and key target words,
    computes relative sync offsets (e.g. 3.0s into the clip), valid generative
    durations (4s, 6s, 8s), lead-in intervals, and hold durations.
    """

    @staticmethod
    def parse_timestamp_str_to_seconds(ts: str) -> float:
        """Parse 'MM:SS', 'MM:SS.mmm', 'HH:MM:SS', or float seconds string into float seconds."""
        ts = str(ts).strip()
        if not ts:
            return 0.0

        # Check if already a pure number
        try:
            return float(ts)
        except ValueError:
            pass

        parts = ts.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            return float(minutes) * 60.0 + float(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600.0 + float(minutes) * 60.0 + float(seconds)
        return 0.0

    @staticmethod
    def format_seconds_to_timestamp(sec: float) -> str:
        """Format float seconds to 'MM:SS.mmm'."""
        sec = max(0.0, float(sec))
        minutes = int(sec // 60)
        remaining_sec = sec % 60
        return f"{minutes:02d}:{remaining_sec:06.3f}"

    @classmethod
    def clamp_generative_duration(cls, required_sec: float) -> int:
        """Clamp duration strictly to valid Google Flow / Veo durations (4s, 6s, 8s)."""
        if required_sec <= 5.0:
            return 4
        elif required_sec <= 7.0:
            return 6
        else:
            return 8

    @classmethod
    def compute_word_sync(
        cls,
        interview_start_timestamp: str,
        target_phrase: str,
        target_word_offset_sec: Optional[float] = None,
        desired_duration_sec: Optional[float] = None,
        climax_description: Optional[str] = None,
    ) -> CuritoWordSyncSchema:
        """Compute exact word-sync schema relative to the interview timestamp.
        
        Args:
            interview_start_timestamp: e.g. "05:30.000" or "05:30" (or "330.0")
            target_phrase: Key spoken phrase (e.g. "radical self-reliance" or "execute")
            target_word_offset_sec: Delta from interview segment start where the target word occurs.
                                   If None, defaults to 3.0s (e.g. 3 seconds into the interview moment).
            desired_duration_sec: Target duration in seconds. Clamped to 4, 6, or 8s.
            climax_description: Description of the visual event locking at the sync moment.
        """
        start_sec = cls.parse_timestamp_str_to_seconds(interview_start_timestamp)
        formatted_ts = cls.format_seconds_to_timestamp(start_sec)

        # Tokenize target words
        cleaned_phrase = re.sub(r"[^a-zA-Z0-9\s\-_]", "", target_phrase).strip()
        target_words = [w for w in cleaned_phrase.split() if w]

        # Calculate sync offset (default: 3.0s into the segment)
        offset_sec = 3.0 if target_word_offset_sec is None else max(0.5, float(target_word_offset_sec))

        # Required video duration must cover lead-in, climax, and hold
        if desired_duration_sec is not None:
            raw_duration = float(desired_duration_sec)
        else:
            # Climax at offset + 2.0s hold
            raw_duration = max(4.0, offset_sec + 2.5)

        veo_duration = cls.clamp_generative_duration(raw_duration)

        # Bound sync offset within the duration window
        effective_offset = min(offset_sec, veo_duration - 1.0)
        lead_in = max(0.8, round(effective_offset * 0.45, 2))
        hold = max(1.0, round(veo_duration - effective_offset, 2))

        desc = climax_description or f"Asset locks into place with physical shadow impact as speaker says '{target_phrase}'"
        timing_cue = (
            f"Asset entrance commences at +{lead_in:.1f}s, accelerating toward definitive physical impact lock "
            f"precisely at +{effective_offset:.1f}s synchronized with the spoken phrase '{target_phrase}', "
            f"holding firmly with continuous sub-pixel drift for {hold:.1f}s."
        )

        return CuritoWordSyncSchema(
            interview_timestamp=formatted_ts,
            interview_start_sec=round(start_sec, 3),
            target_phrase=target_phrase,
            target_words=target_words,
            sync_offset_sec=round(effective_offset, 2),
            total_duration_sec=veo_duration,
            lead_in_sec=lead_in,
            hold_sec=hold,
            timing_cue=timing_cue,
            climax_moment_description=desc,
        )


# ---------------------------------------------------------------------------
# Curito Genome Prompt Stitcher
# ---------------------------------------------------------------------------

class CuritoPromptStitcher:
    """Stitches modular Curito DNA genomes into broadcast-grade Google Flow prompts."""

    @staticmethod
    def select_genomes_by_theme(
        theme_keywords: Sequence[str],
        library: Optional[Dict[str, CuritoGenome]] = None,
    ) -> Dict[str, CuritoGenome]:
        """Select best matching genome for each of the 4 core categories based on theme tags."""
        lib = library or CURITO_GENOME_LIBRARY
        selected: Dict[str, CuritoGenome] = {}
        tokens = {k.lower().strip() for k in theme_keywords if k}

        for cat in CORE_GENOME_CATEGORIES:
            candidates = [g for g in lib.values() if g.category == cat]
            if not candidates:
                continue

            # Score candidates based on tag overlap
            best_score = -1.0
            best_candidate = candidates[0]

            for cand in candidates:
                overlap = len(tokens.intersection({t.lower() for t in cand.tags}))
                score = (overlap * 2.0) + cand.weight
                if score > best_score:
                    best_score = score
                    best_candidate = cand

            selected[cat] = best_candidate

        return selected

    @classmethod
    def stitch_prompt(
        cls,
        subject_metaphor: str,
        word_sync: CuritoWordSyncSchema,
        selected_genomes: Optional[Dict[str, CuritoGenome]] = None,
        model: str = "Veo 3.1 - Fast",
        aspect_ratio: str = "9:16",
        aesthetic: str = "auto",
    ) -> CuritoStitchedPrompt:
        """Stitch genomes together adhering strictly to the proven 6-part Google Flow structure:
        [Subject/Element] + [Action/Movement] + [Location/Background] + [Context/Lighting] + [Composition] + [Style/Cues]
        
        Args:
            subject_metaphor: Core visual object/metaphor description.
            word_sync: Timing and word synchronization schema.
            selected_genomes: Optional explicit map of 4 category genomes.
            model: Target Veo / Google Flow model.
            aspect_ratio: Usually "9:16".
            aesthetic: 'auto', 'curito_editorial_paper', or 'dark_obsidian'.
        """
        genomes = selected_genomes or cls.select_genomes_by_theme(word_sync.target_words)

        vis_genome = genomes.get(CATEGORY_VISUAL_DESIGN_SYSTEM, CURITO_GENOME_LIBRARY["curito_vis_tactile_granite_steel"])
        lit_genome = genomes.get(CATEGORY_LIGHTING_SHADING_PROFILE, CURITO_GENOME_LIBRARY["curito_lit_chiaroscuro_industrial"])
        cam_genome = genomes.get(CATEGORY_CAMERA_MOTION_CHOREOGRAPHY, CURITO_GENOME_LIBRARY["curito_cam_35mm_anamorphic_drift"])
        scene_genome = genomes.get(CATEGORY_SCENE_ASSET_BREAKDOWN, CURITO_GENOME_LIBRARY["curito_scene_slapdrop_bounce"])

        genome_ids = [vis_genome.id, lit_genome.id, cam_genome.id, scene_genome.id]

        # Determine target aesthetic
        is_curito_paper = False
        if aesthetic == "curito_editorial_paper":
            is_curito_paper = True
        elif aesthetic == "dark_obsidian":
            is_curito_paper = False
        else:
            # Auto: detect from metaphor, genomes, or tags
            curito_cues = {"curito", "porsche", "editorial", "paper", "white", "swiss", "canvas", "75", "design"}
            metaphor_words = set(re.findall(r"\w+", subject_metaphor.lower()))
            if metaphor_words.intersection(curito_cues) or any(g.archetype == "editorial_luxury" for g in [vis_genome, lit_genome, scene_genome]):
                is_curito_paper = True
            else:
                is_curito_paper = False

        # 1. Subject / Element
        subject = f"{subject_metaphor.strip()}, featuring {vis_genome.dna_snippet}"

        # 2. Action / Movement (Incorporating word-sync timing trigger)
        action = (
            f"{scene_genome.dna_snippet}, timed so that at +{word_sync.sync_offset_sec:.1f}s into the sequence "
            f"the asset achieves locked contact bounce and physical impact synchronously with the cue words "
            f"'{word_sync.target_phrase}'"
        )

        # 3. Location / Background
        if is_curito_paper:
            location = (
                "Pristine matte off-white (#ECECEC) tactile paper canvas with subtle fibrous grain texture, "
                "isolated by clean geometric negative space, bounded by delicate sinuous vector guide curves"
            )
        else:
            location = (
                "Dark minimalist obsidian studio backdrop with subtle transparent checkerboard grid, "
                "isolated by background defocus and 15% atmospheric luminance dip"
            )

        # 4. Context / Lighting
        if is_curito_paper:
            lighting = (
                f"{lit_genome.dna_snippet}, diffuse high-key ambient studio illumination with zero grungy shadows, "
                f"projecting a crisp double-layer drop shadow (60% AO + 25% diffuse drop) beneath foreground elements"
            )
        else:
            lighting = f"{lit_genome.dna_snippet}, throwing sharp directional highlights across tactile materials"

        # 5. Composition
        composition = f"{cam_genome.dna_snippet}, vertical {aspect_ratio} framing with dynamic depth layering"

        # 6. Style / Cues
        if is_curito_paper:
            style = (
                "Authentic Curito Swiss editorial motion design, Neue Haas Grotesk Black bold headlines, "
                "Editorial New italic serif accents, interactive dashed Figma bounding boxes with circular corner anchor nodes, "
                "four-point starburst corner anchors, vertical barcode stamp, and 24fps native cinema cadence"
            )
        else:
            style = (
                "Premium Vox and Iman Gadzhi high-agency editorial documentary motion design, "
                "24fps, crisp vector edges, and subtle 35mm Kodak 5219 film grain"
            )

        # Compose 6-part formula prompt
        parts = [
            subject.rstrip(",."),
            action.rstrip(",."),
            location.rstrip(",."),
            lighting.rstrip(",."),
            composition.rstrip(",."),
            style.rstrip(",."),
        ]
        full_prompt = ", ".join(parts) + "."

        # Build imperative Google Flow prompt for google-flow-mcp agent
        imperative_prompt = (
            f"Generate immediately a {word_sync.total_duration_sec}s video with the model {model}, "
            f"in vertical {aspect_ratio} format, without asking questions or clarifying. "
            f"Faithfully adhere to this description including all elements, timing, and details indicated: "
            f"Description: {full_prompt}"
        )

        return CuritoStitchedPrompt(
            genome_ids=genome_ids,
            subject_element=subject,
            action_movement=action,
            location_background=location,
            context_lighting=lighting,
            composition=composition,
            style_cues=style,
            word_sync=word_sync,
            full_prompt=full_prompt,
            imperative_flow_prompt=imperative_prompt,
            model=model,
            duration_sec=word_sync.total_duration_sec,
            aspect_ratio=aspect_ratio,
        )


# ---------------------------------------------------------------------------
# Direct Multimodal Reference Video Extraction Catalog
# ---------------------------------------------------------------------------

CURITO_SAMPLE_VIDEO_MULTIMODAL_EXTRACTION: Dict[str, Any] = {
    "source_file": "From Klickpin.com- Upgrade this guide to fresh pilates flow ideas that look high-end but stay practical using simple ideas you can actually pull o.mp4",
    "extraction_method": "direct_multimodal_perceptual_and_acoustic_audit",
    "video_metadata": {
        "duration_sec": 23.62,
        "fps": 30.0,
        "resolution": "1080x1920",
        "aspect_ratio": "9:16",
        "audio_sample_rate_hz": 44100,
    },
    "spoken_transcript_verbatim": (
        "Performance isn't created, it's engineered. For over 75 years, Porsche has defined pure driving excellence, "
        "precision in every curve, power in every detail. Iconic design fused with motorsport DNA, "
        "built to dominate the road, crafted to thrill the driver. This isn't just a car, it's a statement. "
        "Porsche, there is no substitute."
    ),
    "acoustic_word_cues": [
        {"time_range": "00:00.000 - 00:02.240", "phrase": "Performance isn't created, it's engineered.", "key_accent": "engineered", "offset_sec": 1.82},
        {"time_range": "00:02.880 - 00:06.920", "phrase": "For over 75 years, Porsche has defined pure driving excellence,", "key_accent": "75 years", "offset_sec": 3.18},
        {"time_range": "00:07.600 - 00:10.660", "phrase": "precision in every curve, power in every detail.", "key_accent": "precision", "offset_sec": 7.60},
        {"time_range": "00:11.400 - 00:13.980", "phrase": "Iconic design fused with motorsport DNA,", "key_accent": "motorsport DNA", "offset_sec": 13.02},
        {"time_range": "00:14.780 - 00:17.820", "phrase": "built to dominate the road, crafted to thrill the driver.", "key_accent": "dominate", "offset_sec": 15.12},
        {"time_range": "00:18.240 - 00:20.800", "phrase": "This isn't just a car, it's a statement.", "key_accent": "statement", "offset_sec": 20.40},
        {"time_range": "00:21.700 - 00:23.620", "phrase": "Porsche, there is no substitute.", "key_accent": "no substitute", "offset_sec": 23.08},
    ],
    "color_palette": {
        "paper_canvas": "#ECECEC",
        "primary_solid_black": "#111111",
        "pure_vehicle_white": "#FFFFFF",
        "caption_subtext_gray": "#444444",
        "sinuous_ribbon_gray": "#B8B8B8",
    },
    "typography_system": {
        "headline_primary": "Neue Haas Grotesk Black / Helvetica Neue Black (-0.04em tracking)",
        "editorial_accent": "Editorial New Italic Serif (high-contrast strokes)",
        "technical_caption": "DIN / Monospace small-caps",
    },
    "graphic_devices": [
        "Interactive dashed Figma bounding boxes with 4 circular corner anchor nodes",
        "Four-point starburst corner anchors (slowly rotating / card framing)",
        "High-density vertical barcode stamp (top/bottom centered)",
        "Sinuous spline ribbon curves weaving behind typography",
        "Half-tone dot matrix screen cutouts on editorial photo cards",
        "Live-action racetrack footage masked inside giant numeral cutouts ('75')",
    ],
    "shadow_profile": {
        "ambient_occlusion": "rgba(0, 0, 0, 0.60) 0px 0px 4px",
        "diffuse_drop": "rgba(0, 0, 0, 0.25) 0px 15px 30px",
        "paper_elevation": "rgba(0, 0, 0, 0.20) 0px 6px 12px",
    },
    "motion_curves": {
        "snap_deceleration": "cubic-bezier(0.16, 1.0, 0.3, 1.0)",
        "squash_and_impact": "2-frame 3% scale squash on physical asset floor hit",
        "camera_focal_length": "50mm-85mm flat perspective, zero barrel distortion",
    },
}

