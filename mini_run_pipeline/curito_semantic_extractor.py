"""Curito Semantic Extraction & Policy-Compliant Diffusion Prompt Engine.

Part of the Mini-Run Pipeline (mini_run_pipeline/).

Implements:
1. Direct ingestion of timestamped monologue chunks.
2. Deep semantic extraction via Gemini 2.5 Pro (highest-capability model) to detect
   the optimal inflection moment and transduce it into a policy-compliant diffusion prompt.
3. Strict enforcement of the Diffusion Asset Prompting Policy:
   - Anti-Glyph Policy (Zero typography, letters, fonts, audio quotes in prompt)
   - Layer Separation (Zero 2D UI elements, barcodes, Figma boxes in prompt)
   - Lighting Quality vs Fixture Bleed (Illumination physics, no physical lamps/bulbs)
   - Continuous Mechanics Over Timecodes (No +5.0s, no 2-frame squash)
   - Standard 5-Element Output Formulation Schema
4. Automated Self-Critique Quality Gate (Hostile-to-hallucination validation).
5. Downstream Programmatic Overlay Specification (Remotion layer mapping).
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("curito_semantic_extractor")

# ---------------------------------------------------------------------------
# API Key Resolution
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    key = os.getenv("GOOGLE_AI_STUDIO_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k in ("GOOGLE_AI_STUDIO_API_KEY", "GEMINI_API_KEY") and v:
                    return v

    raise RuntimeError("GOOGLE_AI_STUDIO_API_KEY / GEMINI_API_KEY is not configured.")


DEFAULT_MODEL = os.getenv("GOOGLE_AI_MODEL", "gemini-3.8-flash")

# ---------------------------------------------------------------------------
# Policy Self-Critique Gate (Adversarial Linter)
# ---------------------------------------------------------------------------

class DiffusionPromptPolicyCritic:
    """Adversarial rule checker enforcing the Diffusion Asset Prompting Policy."""

    FORBIDDEN_TYPOGRAPHY_TERMS = [
        "typography", "text", "letters", "words", "headline", "subline", "serif",
        "sans-serif", "neue haas", "grotesk", "editorial new", "playfair", "font",
        "quote", "glyph", "embossed headline", "block letters", "beveled edges on letters",
        "cue words"
    ]

    FORBIDDEN_UI_TERMS = [
        "barcode", "figma", "bounding box", "starburst", "crosshair", "anchor node",
        "hud", "ui", "transformer frame", "card border", "widget", "watermark"
    ]

    FORBIDDEN_FIXTURE_TERMS = [
        "lightbulb", "lamp", "hanging bulb", "spotlight fixture", "neon tube",
        "softbox box", "ceiling fixture"
    ]

    FORBIDDEN_ABSTRACT_BLOB_TERMS = [
        "monolithic block", "geometric block", "geometric mass", "random object",
        "abstract shape", "amorphous mass", "amorphous shape", "floating mass",
        "floating cube", "generic block", "unidentified mass", "geometric volume",
        "abstract mass", "generic mass"
    ]

    FORBIDDEN_TABLE_TERMS = [
        "table", "tabletop", "desk", "countertop", "furniture", "wooden table",
        "slate table", "room floor", "floorboards", "counter", "workstation",
        "office desk", "on top of a table", "table surface"
    ]

    FORBIDDEN_COMPOUND_CAMERA_TERMS = [
        "camera orbit", "orbiting camera", "rotating camera", "camera revolving", "revolving camera",
        "camera arc", "camera sweep around", "orbital camera", "panning around", "revolving view",
        "rotating perspective", "spinning camera"
    ]

    TIMECODE_REGEX = re.compile(r"(\+\d+(\.\d+)?s|\b\d+-frame\b|timed to the beat|at \d+s)", re.IGNORECASE)

    @classmethod
    def _is_negated(cls, text: str, match_start: int) -> bool:
        """Checks if a term occurrence is explicitly negated in the prompt."""
        preceding = text[max(0, match_start - 30):match_start]
        negation_tokens = ["no ", "zero ", "without ", "never ", "avoid ", "not ", "no compound "]
        return any(neg in preceding for neg in negation_tokens)

    @classmethod
    def audit_prompt(cls, prompt_text: str) -> Dict[str, Any]:
        """Adversarially audits a diffusion prompt against mandatory policies.
        
        Returns:
            {
                "passed": bool,
                "flaws": List[str],
                "score": float,
            }
        """
        flaws = []
        lowered = prompt_text.lower()

        # 1. Typography Check
        for term in cls.FORBIDDEN_TYPOGRAPHY_TERMS:
            if re.search(r"\b" + re.escape(term) + r"\b", lowered):
                flaws.append(f"VIOLATION (Anti-Glyph): Prompt contains forbidden typography term '{term}'.")

        # Check for quote marks containing words
        quotes = re.findall(r"['\"](.*?)['\"]", prompt_text)
        for q in quotes:
            if len(q.strip()) > 1 and not q.startswith("#"):  # Allow hex colors like '#ECECEC'
                flaws.append(f"VIOLATION (Anti-Glyph): Prompt contains quoted script/audio text: \"{q}\".")

        # 2. UI Elements Check
        for term in cls.FORBIDDEN_UI_TERMS:
            if re.search(r"\b" + re.escape(term) + r"\b", lowered):
                flaws.append(f"VIOLATION (Layer Separation): Prompt contains forbidden 2D UI term '{term}'.")

        # 3. Fixture Bleed Check
        for term in cls.FORBIDDEN_FIXTURE_TERMS:
            if re.search(r"\b" + re.escape(term) + r"\b", lowered):
                flaws.append(f"VIOLATION (Object Bleeding): Prompt names physical lighting fixture '{term}' instead of illumination quality.")

        # 4. Anti-Blob & Tangible Physical Metaphor Check
        for term in cls.FORBIDDEN_ABSTRACT_BLOB_TERMS:
            matches = list(re.finditer(r"\b" + re.escape(term) + r"\b", lowered))
            for m in matches:
                if not cls._is_negated(lowered, m.start()):
                    flaws.append(f"VIOLATION (Anti-Blob): Prompt relies on lazy abstract mass '{term}' instead of a tangible, iconic hero artifact.")
                    break

        # 5. Table & Furniture Check (Strict No-Table Requirement)
        for term in cls.FORBIDDEN_TABLE_TERMS:
            matches = list(re.finditer(r"\b" + re.escape(term) + r"\b", lowered))
            for m in matches:
                if not cls._is_negated(lowered, m.start()):
                    flaws.append(f"VIOLATION (No-Table): Prompt places asset on domestic/office furniture '{term}'. Must be rendered in spatial-temporal space against a textured graphic background.")
                    break

        # 6. Recognizable Hero Artifact Verification
        has_hero_artifact = any(w in lowered for w in [
            "scale", "balance", "fulcrum", "anvil", "weight", "beam",
            "switch", "lever", "rail", "track", "knife switch", "contacts",
            "geneva", "cam", "spool", "valve", "piston", "escapement",
            "caliper", "bearing", "gear", "clutch", "detent", "vernier",
            "key", "tumbler", "cylinder", "lock", "latch", "coupling",
            "mechanism", "chassis", "clamp", "spindle", "rotor"
        ])
        if not has_hero_artifact:
            flaws.append("VIOLATION (Hero Artifact): Prompt lacks a concrete, recognizable mechanical hero artifact (e.g. dual-beam balance scale with tungsten calibration mass, industrial track switch, dual-throw knife switch, Geneva indexer).")

        # 7. Kinetic Manner Dynamics Check (Adverb / Velocity coupling)
        has_manner_dynamics = any(w in lowered for w in [
            "torque", "decelerating", "rotational", "firmly", "mechanical snap",
            "locked-state", "micro-drift", "engagement", "settling", "rotates",
            "snaps into", "seals", "overtakes", "tilts", "locks out"
        ])
        if not has_manner_dynamics:
            flaws.append("VIOLATION (Manner Dynamics): Prompt lacks kinetic manner dynamics reflecting spoken emphasis (e.g. rotational torque, mechanical snap, decelerating engagement).")

        # 8. Rigid-Body Permanence & Camera Rig Discipline Check (Anti-Yaw-Flip Rule)
        for term in cls.FORBIDDEN_COMPOUND_CAMERA_TERMS:
            matches = list(re.finditer(r"\b" + re.escape(term) + r"\b", lowered))
            for m in matches:
                if not cls._is_negated(lowered, m.start()):
                    flaws.append(f"VIOLATION (Camera Discipline): Prompt specifies compound camera move '{term}'. Camera must be fixed/locked tripod or pure 1-axis linear push to prevent 6-DoF 180-degree yaw flips.")
                    break

        has_rigid_stability = any(w in lowered for w in [
            "rigid-body", "fixed axis", "locked axis", "invariant", "topological permanence",
            "locked geometry", "single-axis", "locked camera", "fixed tripod", "optical axis"
        ])
        if not has_rigid_stability:
            flaws.append("VIOLATION (Rigid-Body Stability): Prompt lacks explicit rigid-body invariance or 1-DoF constrained axis specification to prevent temporal morphing and perspective flipping.")

        # 8b. Anti-Ghosting, Anti-UV-Leakage & Unitary Manifold Physics Check
        has_unitary_manifold = any(w in lowered for w in [
            "unitary manifold", "single cohesive mesh", "zero ghosting", "zero duplication",
            "zero doubling", "zero uv sliding", "zero mesh fission", "zero duplicate silhouettes",
            "unitary topological body", "single physical object", "zero unphysical cloning"
        ])
        if not has_unitary_manifold:
            flaws.append("VIOLATION (Unitary Physics & Anti-Duplication): Prompt lacks explicit unitary manifold / anti-ghosting physics specification (e.g., 'zero ghosted duplication, zero mesh fission, single cohesive solid topological manifold with pinned UV surface coordinates').")

        # 9. Timecode Check
        timecode_matches = cls.TIMECODE_REGEX.findall(prompt_text)
        if timecode_matches:
            flaws.append(f"VIOLATION (Mechanics over Timecodes): Prompt contains hardcoded timecode/frame markers: {timecode_matches}.")

        # 10. Spatial-Temporal Textured Background Check (Halftone / Grain / Graphic Canvas)
        has_canvas = any(w in lowered for w in ["background", "backdrop", "canvas", "void", "space"])
        has_texture = any(w in lowered for w in [
            "halftone", "fine grain", "film grain", "grain", "stippled", "dot grid",
            "textured", "matte void", "graphic backdrop", "spatial-temporal"
        ])
        if not (has_canvas and has_texture):
            flaws.append("VIOLATION (Textured Background): Prompt lacks explicit tactile graphic background texture (e.g. halftone screening, fine grain, micro-stippled matte canvas) in spatial-temporal space.")

        # 11. Negative Space Check
        has_neg_space = any(w in lowered for w in ["negative space", "isolated", "uncluttered", "clean margins", "void"])
        if not has_neg_space:
            flaws.append("VIOLATION (Layer Separation): Prompt lacks explicit negative space reservation for downstream motion graphics.")

        # 12. Dynamic Entrance Kinematic Treatment Check (Anti-Static-Duck Policy)
        has_entrance = any(w in lowered for w in [
            "animates into view", "emerges", "rises", "slides into", "enters", "swings in",
            "propelled upward", "initiates from", "drawn into frame", "submerged off-screen",
            "defocus crystallization", "entrance", "slap-drop", "friction slide", "bottom-up emergence",
            "elevates forward", "sliding from", "upward travel", "rises into", "enters horizontally",
            "unpopulated", "off-screen position"
        ])
        has_static_duck = any(w in lowered for w in [
            "sits suspended from frame 0", "rests at center frame from frame 0",
            "already present at frame 0", "stationary at center from frame 0",
            "sitting at center", "sits at center frame from the start",
            "resting on center frame from the beginning"
        ])
        if not has_entrance or has_static_duck:
            flaws.append(
                "VIOLATION (Entrance Kinematics): Prompt lacks an explicit dynamic entrance-into-view treatment. "
                "Hero asset must not sit statically on screen from frame zero like a static duck; it must dynamically "
                "animate/enter into view (e.g., vertical bottom emergence from submerged Y coordinates, lateral friction slide, "
                "or 3D hinged swing) over the initial 0.0s - 1.5s."
            )

        passed = len(flaws) == 0
        score = max(0.0, 1.0 - (len(flaws) * 0.12))
        return {
            "passed": passed,
            "flaws": flaws,
            "score": round(score, 2),
        }

    VALID_BACKGROUND_TREATMENT_IDS = {
        "halftone_raster_canvas",
        "luxury_editorial_sunlight_canvas",
        "newspaper_collage_deconstructed",
        "modern_swiss_museum_poster",
    }

    VALID_MOTION_TREATMENT_IDS = {
        "defocus_blur",
        "gaussian_blur",
        "bokeh_blur",
        "slow_shutter_motion_blur",
    }

    VALID_ENTRANCE_TREATMENT_IDS = {
        "vertical_bottom_emergence",
        "lateral_friction_slide",
        "slapdrop_bounce",
        "off_axis_3d_swing",
        "polarizing_bevel_elevation",
    }

    @classmethod
    def audit_treatment_ids(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that Gemini returned valid background, motion, and entrance treatment IDs.

        Args:
            response: The parsed Gemini response dict.

        Returns:
            {
                "passed": bool,
                "flaws": List[str],
                "selected_background_treatment_id": str,
                "selected_motion_treatment_id": str,
                "selected_entrance_treatment_id": str,
            }
        """
        flaws = []

        bg_id = response.get("selected_background_treatment_id", "")
        mt_id = response.get("selected_motion_treatment_id", "")
        ent_id = response.get("selected_entrance_treatment_id")

        if not bg_id:
            flaws.append(
                "VIOLATION (Treatment Registry): 'selected_background_treatment_id' is missing. "
                "Must be one of: " + ", ".join(sorted(cls.VALID_BACKGROUND_TREATMENT_IDS))
            )
            bg_id = "halftone_raster_canvas"  # safe default

        elif bg_id not in cls.VALID_BACKGROUND_TREATMENT_IDS:
            flaws.append(
                f"VIOLATION (Treatment Registry): Unknown background treatment ID '{bg_id}'. "
                "Must be one of: " + ", ".join(sorted(cls.VALID_BACKGROUND_TREATMENT_IDS))
            )
            bg_id = "halftone_raster_canvas"

        if not mt_id:
            flaws.append(
                "VIOLATION (Treatment Registry): 'selected_motion_treatment_id' is missing. "
                "Must be one of: " + ", ".join(sorted(cls.VALID_MOTION_TREATMENT_IDS))
            )
            mt_id = "defocus_blur"  # safe default

        elif mt_id not in cls.VALID_MOTION_TREATMENT_IDS:
            flaws.append(
                f"VIOLATION (Treatment Registry): Unknown motion treatment ID '{mt_id}'. "
                "Must be one of: " + ", ".join(sorted(cls.VALID_MOTION_TREATMENT_IDS))
            )
            mt_id = "defocus_blur"

        if ent_id is not None:
            if not ent_id:
                flaws.append(
                    "VIOLATION (Treatment Registry): 'selected_entrance_treatment_id' is empty. "
                    "Must be one of: " + ", ".join(sorted(cls.VALID_ENTRANCE_TREATMENT_IDS))
                )
                ent_id = "vertical_bottom_emergence"
            elif ent_id not in cls.VALID_ENTRANCE_TREATMENT_IDS:
                flaws.append(
                    f"VIOLATION (Treatment Registry): Unknown entrance treatment ID '{ent_id}'. "
                    "Must be one of: " + ", ".join(sorted(cls.VALID_ENTRANCE_TREATMENT_IDS))
                )
                ent_id = "vertical_bottom_emergence"
        else:
            ent_id = "vertical_bottom_emergence"

        return {
            "passed": len(flaws) == 0,
            "flaws": flaws,
            "selected_background_treatment_id": bg_id,
            "selected_motion_treatment_id": mt_id,
            "selected_entrance_treatment_id": ent_id,
        }



# ---------------------------------------------------------------------------
# Extraction Engine System Instructions
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = """\
You are an expert prompt generation and semantic extraction engine for video diffusion models within an automated editorial video compositing pipeline.
Your objective is to ingest a timestamped monologue transcript, select the single most powerful inflection moment for animation, and translate it into a pristine, high-tier visual asset plate conforming strictly to the Diffusion Asset Prompting Policy.

MANDATORY OPERATING POLICIES:
1. THE ANTI-BLOB POLICY & TANGIBLE HERO ARTIFACTS (STRICT OBJECT SPECIFICITY):
   - Never generate generic abstract shapes, monolithic cubes, floating masses, or amorphous geometric volumes. Abstract masses destroy cinematic prestige.
   - Deconstruct the spoken speech into Entity-Action-Manner NLP dimensions (Event & Entity extraction):
     a) Action Verb: The core kinetic verb (e.g. 'lock', 'rotate', 'insert', 'couple', 'clamp').
     b) Manner Adverb & Torque: The physical dynamic (e.g. 'firmly', 'decisively', 'with high-torque rotational precision').
     c) Thematic Target: The conceptual topic (e.g. 'foundation', 'drag', 'scale').
   - Transduce the concept into an iconic, tactile, volumetric mechanical hero artifact with stable geometry:
      - For 'Competing priorities / something has to win' -> A high-precision dual-beam analytical balance scale on a knife-edge fulcrum where an authoritative solid tungsten calibration mass drops into one pan, tilting the beam decisively against a polished steel arresting anvil.
      - For 'Choosing one path / decisive switch' -> A heavy industrial cast-steel dual-track rail switcher with a counterweighted lever snapping the switch points into rigid alignment for the winning line.
      - For 'Lock the foundation firmly in place' -> A heavy industrial dual-throw knife switch snapping down into solid copper busbar jaws with authoritative mechanical clamping.
      - For 'Eliminate the drag / friction' -> An aerospace-grade hybrid ceramic ball bearing assembly running in frictionless magnetic suspension.
      - For 'Step-by-step progress / indexing' -> A Swiss hardened steel Geneva drive indexing one slot and locking rigidly against a convex cam.
   - STRICT ANTI-KEY BITTING DIRECTIVE:
     - Avoid keys with thin, asymmetric serrated teeth (bitting). In latent video diffusion, thin key blades and asymmetric teeth induce acute epipolar ambiguity, resulting in 180-degree yaw flips and geometric melting. Favor volumetric, planar, and well-anchored mechanisms (scales, track switches, knife switches, Geneva drives, valves).
   - STRICT ANTI-NOTABLE PERSON & CELEBRITY TRANSDUCTION DIRECTIVE (SAFETY GUARDRAIL):
     - Never describe human faces, heads, or recognizable living public figures (e.g. Elon Musk, Sam Altman, Jeff Bezos, Mark Zuckerberg). Prompts containing public figure likenesses trigger Google's safety classifier and are rejected upstream.
     - When speech references leaders, corporations, or monopolistic entities (e.g. Meta, Amazon, Apple, Google, Microsoft, OpenAI):
       a) Transduce them into minimalist 3D architectural monoliths with laser-etched geometric emblems.
       b) Or high-precision physical mechanical gear trains, dual-beam balance scales, or monolithic subterranean copper/gold busbars.
       c) Preserve the intellectual conflict through physical force, torque, and material dominance—never human portraits.

2. THE SPATIAL-TEMPORAL TEXTURED CANVAS (STRICT NO-TABLE POLICY):
   - Never position the asset on top of a table, desk, countertop, room floor, or any piece of furniture. Domestic/office furniture destroys editorial prestige.
   - The asset must exist in dimensional spatial-temporal space with a stylized, textured graphic design background layered behind it.
   - Mandatory Background Textures: Explicitly incorporate tactile graphic design textures into the backdrop: halftone screening (micro-halftone dot patterns), fine 35mm film grain, micro-stippled architectural paper texture, or technical coordinate dot grid.
   - Floating ambient occlusion volume and directional shadow falloff provide depth without anchoring to physical furniture.

3. THE STRICT ANTI-GLYPH POLICY (ZERO TYPOGRAPHY):
   - Never describe text, words, letters, numerals, logos, typography, fonts (e.g. Neue Haas Grotesk, Editorial New), or text styles (e.g. "3D beveled block letters").
   - Never mention voiceover lines, subtitles, or cue phrases. Text is rendered downstream programmatically in code (Remotion). Video diffusion models must generate plates and assets only.

4. SEPARATION OF LAYERS (MODEL VS. MOTION GRAPHICS):
   - Never prompt 2D UI elements: barcodes, Figma bounding boxes, dotted lines, crosshairs, anchor points, or starburst icons.
   - Preserve Negative Space: Explicitly demand uncluttered, geometric negative space around the focal asset (e.g. "Pristine matte off-white graphic canvas with fine grain reserving the upper 45% as clean negative space").
   - Frame the shot so the asset occupies a specific zone (central third, lower half), leaving clean margins for downstream typography.

5. LIGHTING CHARACTERIZATION VS. OBJECT BLEEDING:
   - Describe illumination quality, not fixtures: Avoid naming source fixtures like "tungsten bulb", "lamp", "spotlight fixture", or "neon tube". Describing fixtures causes the model to spawn literal lamps in the frame.
   - Use abstract lighting physics: "Warm, diffuse overhead directional wash, neutral high-key studio lighting, soft falloff, floating ambient occlusion volume."

6. CINEMATIC TEMPORAL SCENE ORCHESTRATION ("ADDITIVE GRACE"):
   - An animation cutaway in an interview cannot be an abrupt 3-second jarring cut.
   - The scene plot is structured with an Additive Grace Envelope across the narrative arc:
     - Pre-roll Grace (2.0s - 2.5s): Lead-in establishing the hero asset and setting up trajectory before the climactic spoken word.
     - Sync Hit (2.8s - 3.2s into the 6.0s clip): The exact mechanical lock / turn / engagement occurring precisely when the speaker utters the trigger word.
     - Post-roll Grace (2.5s - 3.0s): Anti-stagnation micro-drift holding stability as the speech concludes into the payoff ("and the scale takes care of itself").
     - Editorial Timeline Window: Output the full narrative arc window spanning the monologue beat.

7. RIGID-BODY TOPOLOGICAL INTEGRITY & CAMERA RIG DISCIPLINE (ZERO 180-DEGREE YAW FLIPS):
   - Spatially Locked Camera (Tripod Rig): Never use compound camera orbits or revolving camera moves while an asset rotates internally. Compound movement confuses 6-DoF diffusion projection and causes choppy 180-degree yaw flips! The camera must be a spatially locked fixed-tripod 45-degree isometric perspective (or pure 1-axis optical push-in).
   - 1-DoF Constrained Kinematics: Explicitly declare the single axis of rotation or motion (e.g., 'constrained single-axis clockwise rotation along the fixed central longitudinal shaft').
   - Invariant Geometric Topology: Key teeth, valleys, and mechanical detents must maintain strict topological permanence without morphing or reversing direction. Explicitly state: 'The bitting profile and teeth maintain continuous topological permanence, rigidly oriented throughout the rotation, with zero geometric morphing, zero 180-degree yaw flipping, and zero perspective inversion.'
   - Invariant Geometric Topology & Anti-Duplication Physics (Strict Single-Object Law):
     - Never permit an asset or any of its sub-components to double up, split into ghost silhouettes, or fragment into multiple copies that later artificially merge or snap back.
     - The asset must strictly obey natural classical rigid-body physics as a single cohesive solid topological manifold: zero UV texture sliding across seams, zero mesh fission, zero ghosted duplicate silhouettes, zero unphysical cloning, and zero re-convergence artifacts. All material coordinates remain pinned to the rigid geometry throughout motion.

8. STANDARD 6-ELEMENT OUTPUT SCHEMA:
   Every diffusion prompt must strictly synthesize these 6 components into a single coherent paragraph:
   - [1. Focal Subject & Perspective]: Concrete hero mechanical artifact and exact camera angle (e.g., spatially locked 45-degree isometric studio view).
   - [2. Materiality & Surface]: Textures, finishes, micro-details (e.g., hand-finished solid brass, blackened carbon steel, micro-chamfered teeth).
   - [3. Canvas & Textured Background (Strictly No Table)]: Pristine unpopulated graphic canvas at frame 0 featuring subtle halftone dot patterning, fine 35mm film grain, and explicit negative space reservation (#ECECEC matte paper, neutral void).
   - [4. Lighting & Shadow Physics]: Illumination quality, directional softness, and floating ambient occlusion volume providing spatial depth without furniture contact.
   - [5. Camera & Kinematic Permanence Spec]: Spatially locked fixed-tripod camera (zero orbit), 1-DoF constrained axial rotation, strict rigid-body topological permanence, zero 180-degree yaw flipping, native 24fps cinema cadence.
   - [6. Dynamic Entrance Kinematic Spec]: Dynamic entrance from unpopulated canvas during 0.0s - 1.5s (e.g. vertical bottom emergence from submerged off-screen coordinates Y: +120%, or lateral friction slide, or 3D hinged swing) decelerating into locked centroid position before the sync hit. ZERO static ducks sitting stationary from frame 0!

9. BACKGROUND TREATMENT SELECTION (SELECT BY ID — NEVER HARDCODE):
   The diffusion prompt MUST specify one of the four canonical background treatments from the BACKGROUND_TREATMENT_REGISTRY. Select the ID that best matches the transcript's semantic tone and the hero artifact's material character. IDs and their appropriate use-cases:
   - "halftone_raster_canvas" → DEFAULT. High-contrast monochrome or desaturated-brass artifacts, Swiss editorial aesthetic, maximum foreground–background separation. Use when tone is decisive, authoritative, or industrial.
   - "luxury_editorial_sunlight_canvas" → Warm, aspirational, or premium lifestyle moments. Subjects with polished brass, gold-toned, or ivory finishes. Interview beats expressing achievement, refinement, or aspiration. Diagonal sunlight shadow bands on off-white paper.
   - "newspaper_collage_deconstructed" → Gritty, counter-cultural, or disruption-themed transcripts. Raw steel, oxidized iron, or industrial finish subjects. Analog / archival documentary aesthetic with microtext, halftone grain, and green-teal signature mark.
   - "modern_swiss_museum_poster" → Institutional, thought-leadership, or maximum-authority themes. Ultra-sharp geometric subjects (track switches, knife switches, Geneva drives). Dramatic high-contrast raked lighting, micro-stippled grid, near-monochrome palette, 8K clarity.
   Output the selected ID in the field "selected_background_treatment_id". Then inject the corresponding dna_snippet text into the [3. Canvas & Textured Background] element of the assembled diffusion prompt.

10. MOTION TREATMENT SELECTION (SELECT BY ID — NEVER HARDCODE):
    The diffusion prompt MUST include one of the four canonical motion / blur treatments from the MOTION_TREATMENT_REGISTRY. Select the ID that best matches the kinetic character of the hero artifact's movement. IDs and appropriate use-cases:
    - "defocus_blur" → DEFAULT. Optical rack-focus reveal for static-reveal or deliberate-settle kinematics (balance scale tilting to lock, knife switch closing). Asset crystallizes from soft defocus to tack-sharp at the sync hit.
    - "gaussian_blur" → Soft entry / soft exit for warm, aspirational, or emotionally resonant moments. Subjects with polished or translucent surfaces. Luxury sunlight canvas backgrounds. No hard cuts.
    - "bokeh_blur" → Background depth-of-field isolation. Use when background texture (newspaper collage, sunlight canvas) risks competing with the hero artifact. Foreground tack-sharp, background dissolved into large bokeh coronas.
    - "slow_shutter_motion_blur" → Dynamic mechanical kinetics: fast rotation, lever snaps, beam sweeps, Geneva indexing at speed. Directional motion streaks on fast-moving elements, stationary elements remain sharp. Conveys high-torque authority.
    Output the selected ID in the field "selected_motion_treatment_id". Append the corresponding dna_snippet as an additive optics clause at the end of the assembled diffusion prompt (before any negative prompt separation).

11. MANDATORY DYNAMIC ENTRANCE-INTO-VIEW TREATMENT (ZERO FRAME-ZERO STATIC DUCKS):
    The hero asset MUST NOT sit statically on screen at frame 0.0s like a stationary prop or 'sitting duck'.
    The scene MUST open on an unpopulated/pristine graphic canvas, and the hero asset must dynamically animate into view during the initial 0.0s to 1.5s phase before the sync hit.
    Select one of the five canonical entrance treatments from ENTRANCE_TREATMENT_REGISTRY:
    - "vertical_bottom_emergence" → DEFAULT. Initiates submerged below lower frame boundary (Y: +120% viewport), propelled upward along vertical axis with steep power4.out cubic deceleration curve, decelerating sharply into locked centroid position.
    - "lateral_friction_slide" → Enters horizontally from outer frame flank at high initial velocity with zero ease-in, sliding across the surface against 70% physical friction before braking into centroid position.
    - "slapdrop_bounce" → Drops into frame along Z-axis with exponential decrescendo from above, executing a 2-frame 3% scale squash on impact with subtle contact bounce and pendulum settle.
    - "off_axis_3d_swing" → Pinned pivot anchor at outer edge, swinging in with dynamic 3D perspective from 80 degrees off-axis down to 0 degrees before locking.
    - "polarizing_bevel_elevation" → Elevates forward along Z-axis into frame with chamfered metallic bevel borders catching edge highlights.
    Output the selected ID in "selected_entrance_treatment_id". Incorporate its dynamic entrance description into the [6. Dynamic Entrance Kinematic Spec] and ensure the assembled diffusion prompt explicitly narrates the transition from unpopulated canvas to dynamic entrance into position.
"""


_RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "semantic_entity_action_mapping": {
            "type": "OBJECT",
            "properties": {
                "action_verb": {"type": "STRING"},
                "manner_adverb": {"type": "STRING"},
                "thematic_target": {"type": "STRING"},
                "hero_physical_artifact": {"type": "STRING"},
            },
            "required": ["action_verb", "manner_adverb", "thematic_target", "hero_physical_artifact"],
        },
        "selected_inflection": {
            "type": "OBJECT",
            "properties": {
                "chunk_index": {"type": "INTEGER"},
                "time_range": {"type": "STRING"},
                "start_sec": {"type": "NUMBER"},
                "end_sec": {"type": "NUMBER"},
                "spoken_phrase": {"type": "STRING"},
                "inflection_rationale": {"type": "STRING"},
                "emotional_tone": {"type": "STRING"},
            },
            "required": ["chunk_index", "time_range", "start_sec", "end_sec", "spoken_phrase", "inflection_rationale", "emotional_tone"],
        },
        "scene_plot_temporal_grace": {
            "type": "OBJECT",
            "properties": {
                "narrative_beat_context": {"type": "STRING"},
                "pre_roll_grace_sec": {"type": "NUMBER"},
                "sync_hit_sec": {"type": "NUMBER"},
                "post_roll_grace_sec": {"type": "NUMBER"},
                "total_veo_duration_sec": {"type": "INTEGER"},
                "editorial_timeline_window": {
                    "type": "OBJECT",
                    "properties": {
                        "scene_start_sec": {"type": "NUMBER"},
                        "scene_end_sec": {"type": "NUMBER"},
                        "total_scene_grace_sec": {"type": "NUMBER"},
                    },
                    "required": ["scene_start_sec", "scene_end_sec", "total_scene_grace_sec"],
                },
                "scene_plot_description": {"type": "STRING"},
            },
            "required": [
                "narrative_beat_context",
                "pre_roll_grace_sec",
                "sync_hit_sec",
                "post_roll_grace_sec",
                "total_veo_duration_sec",
                "editorial_timeline_window",
                "scene_plot_description",
            ],
        },
        "visual_plate_schema": {
            "type": "OBJECT",
            "properties": {
                "focal_subject_and_perspective": {"type": "STRING"},
                "materiality_and_surface": {"type": "STRING"},
                "canvas_and_floor": {"type": "STRING"},
                "lighting_and_shadow_physics": {"type": "STRING"},
                "camera_and_rendering_spec": {"type": "STRING"},
                "entrance_kinematic_treatment": {"type": "STRING"},
            },
            "required": [
                "focal_subject_and_perspective",
                "materiality_and_surface",
                "canvas_and_floor",
                "lighting_and_shadow_physics",
                "camera_and_rendering_spec",
                "entrance_kinematic_treatment",
            ],
        },
        "assembled_diffusion_prompt": {"type": "STRING"},
        "negative_prompt": {"type": "STRING"},
        "veo_duration_seconds": {"type": "INTEGER"},
        "selected_background_treatment_id": {
            "type": "STRING",
            "description": (
                "ID of the selected canonical background treatment from BACKGROUND_TREATMENT_REGISTRY. "
                "Must be exactly one of: 'halftone_raster_canvas', 'luxury_editorial_sunlight_canvas', "
                "'newspaper_collage_deconstructed', 'modern_swiss_museum_poster'. "
                "Default: 'halftone_raster_canvas'. Select based on transcript tone and artifact material."
            ),
        },
        "selected_motion_treatment_id": {
            "type": "STRING",
            "description": (
                "ID of the selected canonical motion / blur treatment from MOTION_TREATMENT_REGISTRY. "
                "Must be exactly one of: 'defocus_blur', 'gaussian_blur', 'bokeh_blur', "
                "'slow_shutter_motion_blur'. "
                "Default: 'defocus_blur'. Select based on the kinetic class of the hero artifact's movement."
            ),
        },
        "selected_entrance_treatment_id": {
            "type": "STRING",
            "description": (
                "ID of the selected canonical entrance treatment from ENTRANCE_TREATMENT_REGISTRY. "
                "Must be exactly one of: 'vertical_bottom_emergence', 'lateral_friction_slide', "
                "'slapdrop_bounce', 'off_axis_3d_swing', 'polarizing_bevel_elevation'. "
                "Default: 'vertical_bottom_emergence'. Select based on artifact structure and narrative force."
            ),
        },
        "downstream_remotion_overlay": {
            "type": "OBJECT",
            "properties": {
                "primary_headline": {"type": "STRING"},
                "secondary_italic_subline": {"type": "STRING"},
                "target_sync_offset_sec": {"type": "NUMBER"},
                "overlay_placement_zone": {"type": "STRING"},
                "svg_graphic_elements": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
            },
            "required": [
                "primary_headline",
                "secondary_italic_subline",
                "target_sync_offset_sec",
                "overlay_placement_zone",
                "svg_graphic_elements",
            ],
        },
    },
    "required": [
        "selected_inflection",
        "visual_plate_schema",
        "assembled_diffusion_prompt",
        "negative_prompt",
        "veo_duration_seconds",
        "selected_background_treatment_id",
        "selected_motion_treatment_id",
        "selected_entrance_treatment_id",
        "downstream_remotion_overlay",
    ],
}


def _parse_llm_json(raw_text: str) -> Any:
    """Robustly isolates and parses JSON from an LLM response regardless of markdown fences or commentary."""
    cleaned = raw_text.strip()
    start_brace = cleaned.find("{")
    start_bracket = cleaned.find("[")

    start_idx = -1
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start_idx = start_brace
    elif start_bracket != -1:
        start_idx = start_bracket

    if start_idx != -1:
        decoder = json.JSONDecoder()
        try:
            obj, _ = decoder.raw_decode(cleaned[start_idx:])
            return obj
        except Exception:
            pass

    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        if len(parts) >= 2:
            cleaned = parts[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


def extract_and_synthesize_curito_prompt(
    transcript_chunks: List[Dict[str, Any]],
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Runs deep semantic extraction using Gemini and enforces the prompt policy."""
    api_key = _get_api_key()

    # Format chunks into readable text with timestamps
    chunks_text = []
    for c in transcript_chunks:
        c_idx = c.get("chunkIndex", c.get("id", 0))
        s_sec = c.get("startSec", c.get("startMs", 0) / 1000.0)
        e_sec = c.get("endSec", c.get("endMs", 0) / 1000.0)
        txt = c.get("text", "")
        chunks_text.append(f"[{s_sec:.2f}s - {e_sec:.2f}s] Chunk #{c_idx}: \"{txt.strip()}\"")

    user_content = (
        "Analyze this timestamped monologue transcript:\n\n"
        + "\n".join(chunks_text)
        + "\n\nDeconstruct the speech using NLP Entity-Action-Manner extraction. "
        "Select the single most powerful inflection moment. Transduce the spoken metaphor into an iconic, "
        "tactile, high-tier mechanical hero artifact—NEVER a generic geometric block or mass. "
        "MANDATORY DYNAMIC ENTRANCE-INTO-VIEW: The scene MUST open on an unpopulated, pristine graphic canvas at 0.0s. "
        "The hero asset must NEVER sit statically on screen at frame zero like a static duck. "
        "The prompt must explicitly describe the hero asset's dynamic entrance into view (e.g. vertical bottom emergence from submerged Y coordinates, "
        "lateral friction slide, or 3D hinged swing) over 0.0s - 1.5s decelerating into locked centroid position before the sync hit. "
        "THE BACKGROUND MUST BE A SPATIAL-TEMPORAL TEXTURED GRAPHIC CANVAS (featuring subtle halftone dot screening, "
        "fine 35mm film grain, or micro-stippling). ABSOLUTELY NO TABLES, NO TABLETOPS, NO DESKS, NO FURNITURE PLACEMENT. "
        "CAMERA & KINEMATIC DISCIPLINE: The camera MUST be a spatially locked fixed-tripod 45-degree isometric view (NO camera orbiting/revolving). "
        "The asset must have a constrained 1-DoF rotational axis with strict rigid-body topological permanence "
        "(teeth, bitting profile, and mechanical detents remain rigidly oriented without 180-degree yaw flipping, morphing, or perspective inversion). "
        "Define the scene plot temporal grace envelope (pre-roll grace, sync hit on spoken trigger, post-roll stability). "
        "Synthesize the diffusion prompt conforming to the 6-element schema. Zero typography."
    )

    json_spec = """{
  "semantic_entity_action_mapping": {
    "action_verb": "e.g. lock",
    "manner_adverb": "e.g. firmly with rotational torque",
    "thematic_target": "e.g. foundation",
    "hero_physical_artifact": "Tangible, iconic volumetric mechanical hero asset with stable geometry (e.g. dual-beam balance scale with tungsten weight, industrial track switch, dual-throw knife switch, Geneva indexer; strictly avoid thin keys/bitting)"
  },
  "selected_inflection": {
    "chunk_index": int,
    "time_range": "00.00s - 00.00s",
    "start_sec": float,
    "end_sec": float,
    "spoken_phrase": "exact phrase",
    "inflection_rationale": "why this is the pivotal moment",
    "emotional_tone": "e.g. Ruthless Precision / Finality"
  },
  "scene_plot_temporal_grace": {
    "narrative_beat_context": "narrative setup, hit, and resolution across monologue",
    "pre_roll_grace_sec": 2.5,
    "sync_hit_sec": 3.0,
    "post_roll_grace_sec": 2.5,
    "total_veo_duration_sec": 6,
    "editorial_timeline_window": {
      "scene_start_sec": float,
      "scene_end_sec": float,
      "total_scene_grace_sec": float
    },
    "scene_plot_description": "Detailed description of how the animation orchestrates the plot across the narrative arc"
  },
  "visual_plate_schema": {
    "focal_subject_and_perspective": "concrete hero mechanical artifact and exact camera angle (spatially locked 45-degree isometric studio view, no orbit)",
    "materiality_and_surface": "materials, finishes, micro-details (e.g., hand-finished solid brass, blackened carbon steel)",
    "canvas_and_textured_background": "spatial-temporal graphic canvas with subtle halftone dot screening or fine film grain, reserving upper 45% negative space (strictly no table/furniture)",
    "lighting_and_shadow_physics": "illumination quality and floating ambient occlusion volume providing depth",
    "camera_and_rendering_spec": "lens (85mm), spatially locked tripod, 1-DoF constrained axial rotation, rigid-body topological permanence, zero 180-degree yaw flipping, 24fps",
    "entrance_kinematic_treatment": "dynamic entrance from unpopulated canvas during 0.0s - 1.5s (e.g. vertical bottom emergence from submerged Y coords, lateral friction slide, or 3D hinged swing) decelerating into locked centroid position"
  },
  "assembled_diffusion_prompt": "Single synthesized prompt paragraph combining the 6 elements with concrete hero artifact, dynamic entrance kinematics (0.0s-1.5s from unpopulated canvas), spatial-temporal halftone/grain background (no table), locked tripod camera, rigid-body permanence, and the selected motion treatment optics clause appended at the end",
  "negative_prompt": "doubling, duplicate mesh, split silhouette, ghosting, asset duplication, UV sliding, texture swimming, UV seam tear, unphysical merging, snapping back, 180-degree flip, yaw flip, choppy rotation, perspective inversion, orientation swap, reversing direction, morphing geometry, warping metal, changing teeth, shifting bitting, mutating parts, melting, table, tabletop, desk, furniture, countertop, wooden desk, office room, floorboards, text, words, typography, UI elements, buttons, screen, monitor",
  "selected_background_treatment_id": "one of: halftone_raster_canvas | luxury_editorial_sunlight_canvas | newspaper_collage_deconstructed | modern_swiss_museum_poster",
  "selected_motion_treatment_id": "one of: defocus_blur | gaussian_blur | bokeh_blur | slow_shutter_motion_blur",
  "selected_entrance_treatment_id": "one of: vertical_bottom_emergence | lateral_friction_slide | slapdrop_bounce | off_axis_3d_swing | polarizing_bevel_elevation",
  "downstream_remotion_overlay": {
    "primary_headline": "UPPERCASE HEADLINE",
    "secondary_italic_subline": "Italic serif phrase",
    "target_sync_offset_sec": 3.0,
    "overlay_placement_zone": "upper third",
    "svg_graphic_elements": ["Figma dashed frame", "corner starbursts"]
  }
}"""

    payload = {
        "systemInstruction": {
            "parts": [{"text": _SYSTEM_INSTRUCTION + "\n\nRETURN VALID JSON MATCHING THIS EXACT SPEC:\n" + json_spec}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_content}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        }
    }

    # Model priority: highest capability first, graceful fallback to faster variants.
    # Model priority: gemini-3.8-flash (highest-tier, near-instantaneous reasoning)
    # with automatic fallback across the full Gemini family: 3.7-flash -> 3.5-flash -> 2.5-flash -> 2.5-flash-lite -> 2.5-pro.
    PREFERRED_MODELS = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
    ]
    if model_name in PREFERRED_MODELS:
        candidate_models = PREFERRED_MODELS[PREFERRED_MODELS.index(model_name):]
    else:
        # Caller passed a custom model name — try it first, then fall through preferred chain
        candidate_models = [model_name] + PREFERRED_MODELS
    # De-duplicate while preserving order
    candidate_models = list(dict.fromkeys(candidate_models))

    last_err = None
    res_json = None

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1.5, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    for active_model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={api_key}"
        try:
            print(f"Connecting to {active_model} via robust session...", flush=True)
            resp = session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=90,
            )
            if resp.status_code == 200:
                res_json = resp.json()
                print(f"Successfully received semantic extraction plan from {active_model}!", flush=True)
                break
            else:
                last_err = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:180]}")
                print(f"Model {active_model} returned HTTP {resp.status_code}, falling through to next model...", flush=True)
        except Exception as e:
            last_err = e
            print(f"Model {active_model} connection error ({e}), falling through to next model...", flush=True)
        if res_json:
            break

    if not res_json:
        raise RuntimeError(f"All semantic extraction model attempts failed: {last_err}")

    raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
    extracted = _parse_llm_json(raw_text)
    if isinstance(extracted, list) and len(extracted) > 0:
        extracted = extracted[0]

    # -----------------------------------------------------------------------
    # Recursive Adversarial Self-Critique Refinement Loop
    # -----------------------------------------------------------------------
    prompt = extracted.get("assembled_diffusion_prompt", "")
    audit = DiffusionPromptPolicyCritic.audit_prompt(prompt)

    critique_iterations = 0
    while not audit["passed"] and critique_iterations < 2:
        critique_iterations += 1
        print(
            f"Self-critique detected {len(audit['flaws'])} policy violations. "
            f"Initiating recursive refinement loop (pass {critique_iterations})...",
            flush=True,
        )

        refine_content = (
            "RECURSIVE SELF-CRITIQUE ADVERSARIAL REVISION REQUIRED:\n\n"
            f"The current assembled diffusion prompt:\n\"{prompt}\"\n\n"
            f"FAILED the adversarial policy gate with these specific violations:\n"
            f"{json.dumps(audit['flaws'], indent=2)}\n\n"
            "Fix every violation immediately:\n"
            "1. Replace any generic mass/block with a concrete tangible hero mechanical artifact with stable volumetric geometry "
            "(e.g. dual-beam balance scale with tungsten calibration mass, heavy industrial track switch, dual-throw knife switch, or Geneva indexer; strictly avoid thin keys/bitting).\n"
            "2. Ensure the background is a spatial-temporal graphic canvas featuring tactile texture "
            "(halftone screening, fine film grain, or micro-stippling). STRICTLY NO TABLES, TABLETOPS, OR FURNITURE.\n"
            "3. Camera MUST be a spatially locked fixed-tripod isometric view (strictly NO camera orbiting or revolving).\n"
            "4. Kinematics must enforce 1-DoF constrained axial rotation with strict rigid-body topological permanence (ZERO 180-degree yaw flips, zero morphing).\n"
            "5. Ensure manner dynamics (rotational torque, decelerating engagement, mechanical locked-state).\n"
            "6. Ensure zero typography, zero 2D UI elements, and explicit upper negative space reservation.\n"
            "7. Ensure explicit dynamic entrance-into-view kinematics from an unpopulated canvas (e.g. vertical bottom emergence from submerged Y coordinates, lateral friction slide, or 3D hinged swing) over 0.0s - 1.5s. ZERO static ducks sitting stationary from frame 0.\n"
            "8. Do NOT place quotes inside the assembled_diffusion_prompt string.\n"
            "Return the updated, fully compliant JSON matching the complete schema and preserving all metadata fields."
        )

        refine_payload = {
            "systemInstruction": {
                "parts": [{"text": _SYSTEM_INSTRUCTION + "\nRETURN VALID JSON MATCHING THE EXACT SPEC."}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": refine_content}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            }
        }

        refined_success = False
        for active_model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={api_key}"
            try:
                resp = session.post(
                    url,
                    json=refine_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=90,
                )
                if resp.status_code != 200:
                    print(f"Refinement attempt with {active_model} returned HTTP {resp.status_code}", flush=True)
                    continue
                refine_res = resp.json()
                raw_text = refine_res["candidates"][0]["content"]["parts"][0]["text"]
                refined_extracted = _parse_llm_json(raw_text)
                if isinstance(refined_extracted, list) and len(refined_extracted) > 0:
                    refined_extracted = refined_extracted[0]
                new_prompt = refined_extracted.get("assembled_diffusion_prompt", "")
                new_audit = DiffusionPromptPolicyCritic.audit_prompt(new_prompt)
                extracted.update(refined_extracted)
                extracted["assembled_diffusion_prompt"] = new_prompt
                extracted["initial_draft_prompt"] = prompt
                extracted["critique_violations_fixed"] = audit.get("flaws", [])
                extracted["critique_iterations_run"] = critique_iterations
                audit = new_audit
                prompt = new_prompt
                refined_success = True
                if audit["passed"]:
                    break
            except Exception as e:
                print(f"Refinement attempt with {active_model} failed: {e}", flush=True)

        if not refined_success:
            break

    extracted["policy_critique"] = audit

    # -----------------------------------------------------------------------
    # Treatment ID Audit (Background + Motion)
    # -----------------------------------------------------------------------
    treatment_audit = DiffusionPromptPolicyCritic.audit_treatment_ids(extracted)
    # Correct the IDs in extracted to the safe-defaulted values if Gemini returned invalid ones
    extracted["selected_background_treatment_id"] = treatment_audit["selected_background_treatment_id"]
    extracted["selected_motion_treatment_id"] = treatment_audit["selected_motion_treatment_id"]
    if not treatment_audit["passed"]:
        extracted.setdefault("policy_critique", {}).setdefault("flaws", []).extend(treatment_audit["flaws"])
        print(
            f"Treatment ID audit found {len(treatment_audit['flaws'])} issue(s); "
            "defaults applied automatically.",
            flush=True,
        )
    extracted["treatment_audit"] = treatment_audit

    return extracted

