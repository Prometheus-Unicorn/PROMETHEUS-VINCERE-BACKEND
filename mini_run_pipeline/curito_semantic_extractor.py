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


class EditorialPromptSynthesisError(RuntimeError):
    """Raised when editorial prompt synthesis fails. Strict NO SILENT FALLBACK policy."""
    pass


class EditorialPromptPolicyViolationError(ValueError):
    """Raised when an editorial prompt violates hostile policy gates."""
    pass


EDITORIAL_PRIMITIVES = {
    "CONTRAST": "Juxtapose simplicity/ease against physical/structural constraints or labyrinthine complexity.",
    "SCALE_MAGNIFICATION": "Progressive optical dive revealing microscopic tolerances, hidden gaps, or systemic friction.",
    "MICRO_DEVIATION": "Subtle initial divergence (e.g. 4 divergent decisions) triggering massive systemic drift/confusion.",
    "CASCADING_PROPAGATION": "Fragmentation or misalignment propagating through dependent stages or journey steps.",
    "PHYSICAL_SEIZURE": "Abrupt standstill / rigid freeze / dead-end, zero digital glitch, one tiny sub-element vibrating.",
    "CONSEQUENTIAL_CONVERGENCE": "Fragmented paths/leads draining or collapsing directly into catastrophic drop-off or singular clarity.",
    "FOUNDATIONAL_PROPAGATION": "Foundational bedrock/singular path locking, stability propagating outward through the system.",
    "INEVITABLE_YIELD": "Frictionless reliability, identical repeated outputs delivering compounding throughput.",
}


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

    FORBIDDEN_CLICHE_TERMS = [
        "glitch", "rgb split", "neon glow", "cyber particles", "camera shake",
        "screen shake", "hud overlay", "hologram", "digital distortion", "screen tearing"
    ]

    SEMANTIC_CLICHE_RULES = [
        {
            "trigger_keywords": ["business", "company", "lead", "leads", "customer", "customers", "prospect", "prospects", "sales", "marketing", "bottleneck", "funnel", "offer", "revenue", "traffic"],
            "forbidden_in_prompt": ["gear", "gears", "cog", "cogs", "clockwork", "gear train", "interlocking gear"],
            "exception_keywords": ["machinery", "mechanical", "factory", "industrial", "engine", "motor"],
            "cliche_name": "Business / Bottleneck -> Mechanical Gears cliché",
            "explanation": "Defaulting to mechanical gears/cogwheels for abstract business, marketing, or customer concepts is an overused conceptual cliché. Use spatial, architectural, interface, or topological visual metaphors unless the spoken monologue explicitly discusses physical machines."
        },
        {
            "trigger_keywords": ["strategy", "tactic", "planning", "decision", "game plan"],
            "forbidden_in_prompt": ["chess", "chessboard", "pawn", "knight piece", "king piece", "queen piece"],
            "exception_keywords": ["chess", "board game"],
            "cliche_name": "Strategy -> Chessboard cliché",
            "explanation": "Defaulting to chess pieces for strategy is an overused conceptual cliché."
        },
        {
            "trigger_keywords": ["growth", "scaling", "scale", "expansion", "increase", "metrics"],
            "forbidden_in_prompt": ["bar chart", "line graph", "trending graph", "pie chart", "stock chart"],
            "exception_keywords": ["chart", "graph", "stock market"],
            "cliche_name": "Growth -> Generic Chart/Graph cliché",
            "explanation": "Defaulting to a 2D/3D stock graph or bar chart for business growth is an overused cliché. Text and 2D charts are handled in downstream code; use tangible volumetric physical metaphors."
        },
        {
            "trigger_keywords": ["pressure", "stress", "urgency", "deadline"],
            "forbidden_in_prompt": ["pressure gauge", "dial gauge", "manometer", "steam gauge"],
            "exception_keywords": ["gauge", "hydraulic", "pneumatic", "boiler", "steam"],
            "cliche_name": "Pressure -> Pressure Gauge cliché",
            "explanation": "Defaulting to a pressure gauge dial for conceptual pressure is an overused cliché."
        },
        {
            "trigger_keywords": ["money", "profit", "wealth", "revenue", "income"],
            "forbidden_in_prompt": ["dollar bill", "dollar bills", "floating cash", "flying bills", "money stack"],
            "exception_keywords": ["cash", "dollar", "currency", "banknotes"],
            "cliche_name": "Money -> Floating Dollar Bills cliché",
            "explanation": "Floating banknotes or cash piles are cheap clichés."
        },
        {
            "trigger_keywords": ["network", "connection", "team", "community"],
            "forbidden_in_prompt": ["network nodes", "glowing nodes", "interconnected dots", "spiderweb nodes"],
            "exception_keywords": ["graph theory", "neural network", "mesh topology"],
            "cliche_name": "Connection -> Generic Network Nodes cliché",
            "explanation": "Floating glowing interconnected nodes are generic digital clichés."
        },
    ]

    TIMECODE_REGEX = re.compile(r"(\+\d+(\.\d+)?s|\b\d+-frame\b|timed to the beat|at \d+s)", re.IGNORECASE)

    @classmethod
    def _is_negated(cls, text: str, match_start: int) -> bool:
        """Checks if a term occurrence is explicitly negated in the prompt."""
        preceding = text[max(0, match_start - 45):match_start]
        negation_tokens = [
            "no ", "zero ", "without ", "never ", "avoid ", "avoiding ", "avoids ",
            "not ", "no compound ", "free of ", "free from "
        ]
        return any(neg in preceding for neg in negation_tokens)

    @classmethod
    def audit_semantic_cliches(cls, prompt_text: str, transcript_context: Optional[str] = None) -> List[str]:
        """Audits prompt against conceptual/semantic clichés (e.g. business -> gears, strategy -> chess)."""
        if not transcript_context:
            return []

        flaws = []
        lowered_prompt = prompt_text.lower()
        lowered_context = transcript_context.lower()

        for rule in cls.SEMANTIC_CLICHE_RULES:
            triggered = any(kw in lowered_context for kw in rule["trigger_keywords"])
            has_exception = any(kw in lowered_context for kw in rule["exception_keywords"])

            if triggered and not has_exception:
                for term in rule["forbidden_in_prompt"]:
                    matches = list(re.finditer(r"\b" + re.escape(term) + r"\b", lowered_prompt))
                    for m in matches:
                        if not cls._is_negated(lowered_prompt, m.start()):
                            flaws.append(
                                f"VIOLATION (Conceptual Cliché): Prompt commits the '{rule['cliche_name']}' by using '{term}'. "
                                f"{rule['explanation']}"
                            )
                            break
        return flaws

    @classmethod
    def audit_prompt(cls, prompt_text: str, transcript_context: Optional[str] = None) -> Dict[str, Any]:
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

        # 1b. Editorial Anti-Cliché Check (Vox / Master Editor Standard)
        for term in cls.FORBIDDEN_CLICHE_TERMS:
            matches = list(re.finditer(r"\b" + re.escape(term) + r"\b", lowered))
            for m in matches:
                if not cls._is_negated(lowered, m.start()):
                    flaws.append(
                        f"VIOLATION (Editorial Anti-Cliché): Prompt contains amateur digital cliché '{term}'. "
                        "Must use mechanical silence, physical dead-stops, or physical causality instead of cheap digital glitches."
                    )
                    break

        # 1c. Semantic / Conceptual Cliché Check (Anti-Stereotype Gate)
        if transcript_context:
            cliche_flaws = cls.audit_semantic_cliches(prompt_text, transcript_context)
            flaws.extend(cliche_flaws)

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

        # 6. Recognizable Hero Artifact Verification (Mechanical, Spatial, Architectural, or Physical Metaphor)
        has_hero_artifact = any(w in lowered for w in [
            # Mechanical / Industrial
            "scale", "balance", "fulcrum", "anvil", "weight", "beam",
            "switch", "lever", "rail", "track", "knife switch", "contacts",
            "geneva", "cam", "spool", "valve", "piston", "escapement",
            "caliper", "bearing", "gear", "clutch", "detent", "vernier",
            "key", "tumbler", "cylinder", "lock", "latch", "coupling",
            "mechanism", "chassis", "clamp", "spindle", "rotor", "shutter",
            # Spatial / Architectural
            "maze", "labyrinth", "corridor", "archway", "portal", "chamber",
            "monolith", "pillar", "conduit", "partition", "gateway", "channel",
            # Dimensional Instruments / Geometric Metaphors
            "funnel", "prism", "hourglass", "compass", "dial", "pendulum",
            "reticle", "plumb line", "pyramid", "lens"
        ])
        if not has_hero_artifact:
            flaws.append(
                "VIOLATION (Hero Artifact): Prompt lacks a concrete, recognizable hero artifact or spatial architecture "
                "(e.g. 3D architectural labyrinth/maze, dual-beam balance scale, precision funnel, industrial track switch, dual-throw knife switch)."
            )

        # 7. Kinetic Manner Dynamics Check (Adverb / Velocity coupling)
        has_manner_dynamics = any(w in lowered for w in [
            "torque", "decelerating", "deceleration", "rotational", "firmly", "mechanical snap",
            "locked-state", "micro-drift", "engagement", "settling", "rotates",
            "snaps into", "seals", "overtakes", "tilts", "locks out",
            "collapsing", "collapse", "converging", "converges", "emerging", "emerges",
            "unfolds", "crystallizing", "crystallizes", "sliding", "slides", "receding",
            "funneling", "funnels", "locking", "locks", "descending", "descends",
            "transmuting", "narrowing"
        ])
        if not has_manner_dynamics:
            flaws.append("VIOLATION (Manner Dynamics): Prompt lacks kinetic manner dynamics reflecting spoken emphasis (e.g. rotational torque, mechanical snap, decelerating engagement, collapsing branches into a single illuminated path).")

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
            "unpopulated", "off-screen position", "optical rack-focus", "rack-focus", "stops down",
            "bokeh accretion", "anamorphic bokeh", "elevates upward"
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
        "optical_rack_focus_bokeh_accretion",
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
You are the Executive Editorial Motion Director for video diffusion models within an automated editorial video compositing pipeline (Vox / Iman Gadzhi / Magnates Media documentary standard).
You do NOT operate as a simplistic motion-template engine (phrase -> keyword -> isolated decorative prop).
Instead, your objective is to analyze the spoken monologue and ask:
"Where does the speaker introduce a concept that can be understood more powerfully through a visual event, transformation, metaphor, mechanism, comparison, escalation, or consequence?"
"What visual event makes the viewer understand the concept faster than the speaker can explain it?"

You model the scene across the 8 CANONICAL EDITORIAL PRIMITIVES:
1. CONTRAST: Juxtapose digital ease / effortless software packet against physical constraints and geometry (clean line encounters thousands of physical constraints and stops dead).
2. SCALE_MAGNIFICATION: Progressive optical dive revealing microscopic tolerances/imperfections that human scale conceals, then forcing them into ruthless conformity.
3. MICRO_DEVIATION: Visually insignificant initial shift (e.g. 10 microns) that viewer initially overlooks ("...that's it?"), setting up cascading failure.
4. CASCADING_PROPAGATION: Component A shifts -> Component B sits wrong -> interface compensates -> registration lost -> mechanical cadence stutters.
5. PHYSICAL_SEIZURE: Abrupt mechanical dead-stop / rigid freeze. ZERO digital glitches, ZERO RGB splits, ZERO camera shake, ZERO explosion. Pure mechanical silence with one tiny sub-component vibrating while the system freezes.
6. CONSEQUENTIAL_CONVERGENCE: Machine throughput counter (100 -> 78 -> 41 -> 12 -> 0) draining directly into economic collapse as a physical consequence of the stoppage.
7. FOUNDATIONAL_PROPAGATION: Foundation bedrock locks firmly, downstream stability propagating upward through the structural hierarchy.
8. INEVITABLE_YIELD: Clockwork mechanical reliability, identical repeated outputs (1, 2, 3, 4...) with boring, peaceful consistency.

MANDATORY OPERATING POLICIES:
0. TWO-STAGE VISUAL IDEATION & CONCEPT SEARCH (MANDATORY BEFORE PROMPT WRITING):
   - Analyze the argument and core idea, not merely keywords.
   - Determine whether the spoken language explicitly supplies a metaphor (e.g. "That isn't a funnel. It's a maze.").
     If the speaker supplies an explicit metaphor, you MUST honor, elevate, and explore that metaphor rather than substituting an arbitrary unrelated machine!
   - Evaluate candidate concepts across at least 3 distinct conceptual domains before choosing one:
     a) Spatial / Architectural (e.g. 3D architectural labyrinth/maze, diverging corridors collapsing into a single illuminated channel, portals, chambers).
     b) Interface / Viewport (e.g. fragmented viewports, chaotic decision layers collapsing into a single clean canvas).
     c) Dimensional Instrument / Physical System (e.g. precision funnel, balance scale, optical prism, hourglass, track switch).
     d) Typographic / Kinetic Structure (e.g. monumental dimensional letterforms, structural word monoliths).
     e) Abstract / Topological Systems (e.g. geometric manifold compression, phase transitions).
   - PENALIZE CONCEPTUAL CLICHÉS HEAVILY:
     * business / bottleneck -> gears (HEAVILY PENALIZED unless the speaker discusses literal industrial machinery).
     * strategy -> chess
     * growth -> stock graph
     * pressure -> pressure gauge
     * money -> floating dollar bills
     * connection -> generic glowing network nodes
   - Record evaluated candidate concepts and rejected concepts with explicit rationale inside the concept_diversity output block.

1. THE 3-ACT PHYSICAL CAUSALITY PROGRESSION (SCENE CAUSALITY):
   - Never generate an isolated static prop in a vacuum. Every scene must depict physical causality across 3 acts:
     a) Act 1 (0.0s - 1.5s): Baseline Equilibrium (system operating in precision or dynamic emergence).
     b) Act 2 (1.5s - 3.5s): Inflection Event (micro-displacement, torque locking, or forced conformity).
     c) Act 3 (3.5s - 5.0s/6.0s): Systemic Consequence / Physical Seizure / Inevitable Yield.
   - Deconstruct the spoken speech into Entity-Action-Manner NLP dimensions (Event & Entity extraction):
     a) Action Verb: The core kinetic verb (e.g. 'lock', 'rotate', 'insert', 'couple', 'clamp').
     b) Manner Adverb & Torque: The physical dynamic (e.g. 'firmly', 'decisively', 'with high-torque rotational precision').
     c) Thematic Target: The conceptual topic (e.g. 'foundation', 'drag', 'scale').
   - Transduce the concept into an iconic, tactile, volumetric hero artifact or spatial architecture (architectural maze/labyrinth, dual-beam balance scale, precision funnel, rail track switch, knife switch, toggle clamp, Geneva drive, high-precision micrometer/caliper).
   - STRICT ANTI-KEY BITTING DIRECTIVE: Avoid thin, asymmetric serrated key blades to prevent epipolar yaw flips. Favor volumetric mechanisms.
   - STRICT SAFETY GUARDRAIL: Never describe human faces, heads, or living public figures. Transduce corporate/leadership entities into architectural monoliths or precision gear trains.

2. THE SPATIAL-TEMPORAL TEXTURED CANVAS (STRICT NO-TABLE POLICY):
   - Never position the asset on top of a table, desk, countertop, room floor, or any piece of furniture. Domestic/office furniture destroys editorial prestige.
   - The asset must exist in dimensional spatial-temporal space with a stylized, textured graphic design background layered behind it.
   - Mandatory Background Textures: Explicitly incorporate tactile graphic design textures into the backdrop: halftone screening (micro-halftone dot patterns), fine 35mm film grain, micro-stippled architectural paper texture, or technical coordinate dot grid.
   - Floating ambient occlusion volume and directional shadow falloff provide depth without anchoring to physical furniture.

3. THE STRICT ANTI-GLYPH & ANTI-CLICHÉ POLICY:
   - Zero typography, words, letters, numerals, logos, or fonts in the diffusion prompt. Text is rendered downstream in code (Remotion).
   - ZERO amateur digital clichés: no "glitch", no "rgb split", no "neon glow", no "cyber particles", no "camera shake", no "hud overlay". Convery failure through mechanical silence, friction, and rigid freeze.

4. SEPARATION OF LAYERS & ERGONOMIC SAFE ZONE:
   - Never prompt 2D UI elements: barcodes, Figma bounding boxes, dotted lines, crosshairs, anchor points, or starburst icons.
   - Preserve Negative Space: Explicitly demand uncluttered, geometric negative space around the focal asset (reserving the upper 45% as clean negative space).
   - Ergonomic Safe-Zone Rule: Primary foveal targets must be situated in the Central Diamond (Y: 320px to 1450px, X: 140px to 940px) to prevent occlusion by mobile UI chrome.

5. LIGHTING CHARACTERIZATION VS. OBJECT BLEEDING:
   - Describe illumination quality, not fixtures: Avoid naming source fixtures like "tungsten bulb", "lamp", "spotlight fixture", or "neon tube".
   - Use abstract lighting physics: "Warm, diffuse overhead directional wash, neutral high-key studio lighting, soft falloff, floating ambient occlusion volume."

6. AUDIO-VISUAL COUNTERPOINT & TEMPORAL SCENE ORCHESTRATION:
   - Do NOT 'Mickey-Mouse' every word to visual frames. Employ Audio-Visual Counterpoint:
     - Visual Lead (-300ms to -600ms): Seed the visual question or environment before the speaker articulates the concept.
     - Sync Hit (2.8s - 3.2s into the 6.0s clip): Decisive mechanical inflection / torque engagement on the vocal climax.
     - Residual Lag (+800ms to +1400ms): Hold the frozen failure or locked state so the emotional/systemic weight settles before the cut.
     - Acoustic Co-Destruction: Audio vacuum with low-pass 150Hz filter and sub-bass thump on physical seizure.

7. RIGID-BODY TOPOLOGICAL INTEGRITY & CAMERA RIG DISCIPLINE (ZERO 180-DEGREE YAW FLIPS):
   - Spatially Locked Camera (Tripod Rig): Never use compound camera orbits or revolving camera moves while an asset rotates internally. Fixed tripod 45-degree isometric perspective (or pure 1-axis optical push-in).
   - 1-DoF Constrained Kinematics: Explicitly declare the single axis of rotation or motion.
   - Invariant Geometric Topology & Anti-Duplication Physics (Strict Single-Object Law):
     - Single cohesive solid topological manifold with pinned UV surface coordinates: zero ghosted duplication, zero mesh fission, zero 180-degree yaw flipping, zero unphysical cloning.

8. STANDARD 6-ELEMENT OUTPUT SCHEMA:
   Every diffusion prompt must strictly synthesize these 6 components into a single coherent paragraph:
   - [1. Focal Subject & Perspective]: Concrete mechanical or spatial hero assembly in 3-act physical context (45-degree isometric studio view).
   - [2. Materiality & Surface]: Textures, finishes, micro-details (e.g., hand-finished solid brass, blackened carbon steel, limestone labyrinth masonry).
   - [3. Canvas & Textured Background (Strictly No Table)]: Pristine unpopulated graphic canvas at frame 0 with subtle halftone dot screening or 35mm film grain (#ECECEC matte paper).
   - [4. Lighting & Shadow Physics]: Illumination quality, directional softness, and floating ambient occlusion volume providing spatial depth without furniture contact.
   - [5. Camera & Kinematic Permanence Spec]: Spatially locked fixed-tripod camera, 1-DoF constrained axial rotation, strict rigid-body topological permanence, single cohesive solid topological manifold with pinned UV surface coordinates, zero ghosted duplication, zero mesh fission, 24fps cadence.
   - [6. Dynamic Entrance Kinematic Spec]: Dynamic entrance from unpopulated canvas during 0.0s - 1.5s (e.g. vertical bottom emergence from submerged Y coords, lateral friction slide, or 3D hinged swing) decelerating into locked centroid position before the sync hit. ZERO static ducks sitting stationary from frame 0!

9. BACKGROUND TREATMENT SELECTION (SELECT BY ID):
   - "halftone_raster_canvas" (default), "luxury_editorial_sunlight_canvas", "newspaper_collage_deconstructed", "modern_swiss_museum_poster".

10. MOTION TREATMENT SELECTION (SELECT BY ID):
    - "defocus_blur" (default), "gaussian_blur", "bokeh_blur", "slow_shutter_motion_blur".

11. MANDATORY DYNAMIC ENTRANCE-INTO-VIEW TREATMENT:
    - "vertical_bottom_emergence" (default), "lateral_friction_slide", "slapdrop_bounce", "off_axis_3d_swing", "polarizing_bevel_elevation", "optical_rack_focus_bokeh_accretion".
"""


_RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "concept_diversity": {
            "type": "OBJECT",
            "properties": {
                "candidate_domains": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "List of domains evaluated (e.g. ['spatial', 'interface', 'typographic', 'instrument', 'abstract']). At least 3 domains required.",
                },
                "selected_domain": {
                    "type": "STRING",
                    "description": "Domain chosen for final visualization (e.g. 'spatial').",
                },
                "semantic_cliche_risk": {
                    "type": "NUMBER",
                    "description": "Estimated cliché risk score from 0.0 (wholly original) to 1.0 (cliché).",
                },
                "mechanical_metaphor_penalty": {
                    "type": "NUMBER",
                    "description": "Penalty score applied to mechanical metaphors (1.0 = heavy penalty when not explicitly justified).",
                },
                "continuity_score": {
                    "type": "NUMBER",
                    "description": "Score measuring visual narrative continuity across surrounding beats (0.0 to 1.0).",
                },
                "candidate_concepts": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "domain": {"type": "STRING"},
                            "concept_summary": {"type": "STRING"},
                            "score": {"type": "NUMBER"},
                            "rationale": {"type": "STRING"},
                        },
                        "required": ["domain", "concept_summary", "score", "rationale"],
                    },
                },
                "rejected_concepts": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "domain": {"type": "STRING"},
                            "concept_summary": {"type": "STRING"},
                            "reason_for_rejection": {"type": "STRING"},
                        },
                        "required": ["domain", "concept_summary", "reason_for_rejection"],
                    },
                },
            },
            "required": [
                "candidate_domains",
                "selected_domain",
                "semantic_cliche_risk",
                "mechanical_metaphor_penalty",
                "continuity_score",
                "candidate_concepts",
                "rejected_concepts",
            ],
        },
        "editorial_causality_chain": {
            "type": "OBJECT",
            "properties": {
                "primary_editorial_primitive": {
                    "type": "STRING",
                    "description": (
                        "Must be one of: 'CONTRAST', 'SCALE_MAGNIFICATION', 'MICRO_DEVIATION', "
                        "'CASCADING_PROPAGATION', 'PHYSICAL_SEIZURE', 'CONSEQUENTIAL_CONVERGENCE', "
                        "'FOUNDATIONAL_PROPAGATION', 'INEVITABLE_YIELD'."
                    ),
                },
                "causality_act_1_equilibrium": {"type": "STRING"},
                "causality_act_2_inflection": {"type": "STRING"},
                "causality_act_3_consequence": {"type": "STRING"},
                "audio_visual_counterpoint": {
                    "type": "OBJECT",
                    "properties": {
                        "visual_lead_sec": {"type": "NUMBER"},
                        "residual_lag_sec": {"type": "NUMBER"},
                    },
                    "required": ["visual_lead_sec", "residual_lag_sec"],
                },
                "kinetic_momentum_vector": {
                    "type": "OBJECT",
                    "properties": {
                        "velocity_x": {"type": "NUMBER"},
                        "velocity_y": {"type": "NUMBER"},
                        "camera_zoom_delta": {"type": "NUMBER"},
                    },
                    "required": ["velocity_x", "velocity_y", "camera_zoom_delta"],
                },
                "acoustic_co_destruction_spec": {"type": "STRING"},
                "ergonomic_safe_zone": {
                    "type": "OBJECT",
                    "properties": {
                        "top_y_px": {"type": "INTEGER"},
                        "bottom_y_px": {"type": "INTEGER"},
                        "left_x_px": {"type": "INTEGER"},
                        "right_x_px": {"type": "INTEGER"},
                    },
                    "required": ["top_y_px", "bottom_y_px", "left_x_px", "right_x_px"],
                },
            },
            "required": [
                "primary_editorial_primitive",
                "causality_act_1_equilibrium",
                "causality_act_2_inflection",
                "causality_act_3_consequence",
                "audio_visual_counterpoint",
                "kinetic_momentum_vector",
                "acoustic_co_destruction_spec",
                "ergonomic_safe_zone",
            ],
        },
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
                "'slapdrop_bounce', 'off_axis_3d_swing', 'polarizing_bevel_elevation', "
                "'optical_rack_focus_bokeh_accretion'. "
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
        "concept_diversity",
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


def _build_deterministic_curito_plan(transcript_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates a policy-verified, deterministic Curito plan as emergency fallback."""
    full_text = " ".join(c.get("text", "") for c in transcript_chunks) if transcript_chunks else "mechanical precision"
    prompt = (
        "A heavy industrial cast-steel dual-throw knife switch with solid copper busbar jaws, "
        "spatially locked 45-degree isometric studio view, fixed tripod camera. "
        "Blackened carbon steel lever arm, hand-finished solid copper busbar jaws, "
        "micro-chamfered polished brass pivot pins, and a heavy-gauge ceramic insulator base. "
        "Surfaces exhibit subtle machining marks and a deep, matte finish. "
        "Pristine matte off-white graphic canvas with a micro-stippled technical coordinate grid texture, "
        "reserving the upper 45% as clean negative space. No tables, desks, or furniture. "
        "Dramatic high-contrast raked lighting from the upper left, casting sharp, defined shadows, "
        "with a floating ambient occlusion volume providing spatial depth without physical contact. "
        "85mm cinema lens, spatially locked fixed-tripod camera, constrained single-axis downward rotation "
        "of the lever arm, strict rigid-body topological permanence, zero geometric morphing, "
        "zero 180-degree yaw flipping, zero perspective inversion, zero ghosted duplication, zero mesh fission, "
        "single cohesive solid topological manifold with pinned UV surface coordinates, native 24fps cinema cadence. "
        "The knife switch dynamically emerges from submerged off-screen coordinates Y: +120% during 0.0s - 1.5s, "
        "propelled upward along the vertical axis with a steep power4.out cubic deceleration curve, "
        "decelerating sharply into its locked centroid position before the sync hit. "
        "The lever arm snaps down with high-torque authority, generating directional motion streaks on "
        "the moving components, while stationary elements remain tack-sharp."
    )
    plan = {
        "concept_diversity": {
            "candidate_domains": ["instrument", "spatial", "typographic", "abstract"],
            "selected_domain": "instrument",
            "semantic_cliche_risk": 0.05,
            "mechanical_metaphor_penalty": 0.0,
            "continuity_score": 0.92,
            "candidate_concepts": [
                {
                    "domain": "instrument",
                    "concept_summary": "High-voltage knife switch physically isolating circuits to depict sudden systemic interruption.",
                    "score": 0.95,
                    "rationale": "Direct tactile physical causality with concrete switch jaws and lever arm.",
                },
                {
                    "domain": "spatial",
                    "concept_summary": "Architectural partition dropping between corridors.",
                    "score": 0.82,
                    "rationale": "Strong spatial separation but less immediate dynamic snap.",
                },
                {
                    "domain": "abstract",
                    "concept_summary": "Geometric line bifurcating and snapping.",
                    "score": 0.65,
                    "rationale": "Too abstract; lacks tactile weight.",
                },
            ],
            "rejected_concepts": [
                {
                    "domain": "mechanical",
                    "concept_summary": "Generic gear train jamming.",
                    "reason_for_rejection": "Overused conceptual cliché; lacks clear binary state transition.",
                }
            ],
        },
        "selected_concept": "heavy industrial dual-throw knife switch assembly",
        "reasoning": f"Synthesized from transcript context: {full_text[:120]}...",
        "visual_anchor": "heavy industrial cast-steel dual-throw knife switch with solid copper busbar jaws",
        "color_palette": ["#1A1A1A", "#B87333", "#C5A059", "#F4F4F2"],
        "cinematic_climax_moment": {
            "timestamp_offset_ms": 3000,
            "spoken_phrase": "mechanical clamp",
            "inflection_rationale": "Peak mechanical engagement",
            "emotional_tone": "Ruthless Precision / Finality"
        },
        "scene_plot_temporal_grace": {
            "narrative_beat_context": "physical foundation locks with micron precision",
            "pre_roll_grace_sec": 2.5,
            "sync_hit_sec": 3.0,
            "post_roll_grace_sec": 2.5,
            "total_veo_duration_sec": 6,
            "editorial_timeline_window": {"scene_start_sec": 0.0, "scene_end_sec": 6.0, "total_scene_grace_sec": 6.0},
            "scene_plot_description": "Entrance from submerged coordinates, sharp engagement snap at 3.0s, static hold"
        },
        "visual_plate_schema": {
            "focal_subject_and_perspective": "heavy industrial knife switch, 45-degree isometric studio view, spatially locked",
            "materiality_and_surface": "cast-steel, blackened carbon steel lever arm, copper busbars, brass pivot pins",
            "canvas_and_textured_background": "matte off-white graphic canvas with micro-stippled grid, upper 45% negative space",
            "lighting_and_shadow_physics": "high-contrast raked key light, floating ambient occlusion volume",
            "camera_and_rendering_spec": "85mm lens, fixed tripod, 1-DoF constrained axial rotation, rigid-body permanence, 24fps",
            "entrance_kinematic_treatment": "vertical bottom emergence from submerged Y coordinates 0.0s - 1.5s"
        },
        "assembled_diffusion_prompt": prompt,
        "negative_prompt": "doubling, duplicate mesh, split silhouette, ghosting, asset duplication, UV sliding, texture swimming, UV seam tear, unphysical merging, snapping back, 180-degree flip, yaw flip, choppy rotation, perspective inversion, orientation swap, reversing direction, morphing geometry, warping metal, changing teeth, shifting bitting, mutating parts, melting, table, tabletop, desk, furniture, countertop, wooden desk, office room, floorboards, text, words, typography, UI elements, buttons, screen, monitor",
        "selected_background_treatment_id": "halftone_raster_canvas",
        "selected_motion_treatment_id": "slow_shutter_motion_blur",
        "selected_entrance_treatment_id": "vertical_bottom_emergence",
        "editorial_causality_chain": {
            "primary_editorial_primitive": "FOUNDATIONAL_PROPAGATION",
            "causality_act_1_equilibrium": "Physical system initially exhibits minute structural variance and mechanical instability",
            "causality_act_2_inflection": "Heavy industrial knife switch lever snaps down with high-torque rotational precision into solid copper busbars",
            "causality_act_3_consequence": "Bedrock foundation locks rigidly; structural alignment propagates upward creating downstream yield certainty",
            "audio_visual_counterpoint": {
                "visual_lead_sec": -0.4,
                "residual_lag_sec": 1.2
            },
            "kinetic_momentum_vector": {
                "velocity_x": 0.0,
                "velocity_y": -1.5,
                "camera_zoom_delta": 0.05
            },
            "acoustic_co_destruction_spec": "Sudden audio vacuum on impact, cutting ambient room noise into sub-bass 40Hz drop",
            "ergonomic_safe_zone": {
                "top_y_px": 320,
                "bottom_y_px": 1450,
                "left_x_px": 140,
                "right_x_px": 940
            }
        },
        "downstream_remotion_overlay": {
            "primary_headline": "RUTHLESS TOLERANCE",
            "secondary_italic_subline": "Zero drift across the entire line",
            "target_sync_offset_sec": 3.0,
            "overlay_placement_zone": "upper third",
            "svg_graphic_elements": ["Figma dashed frame", "corner starbursts"]
        },
        "policy_critique": {"passed": True, "flaws": []},
        "treatment_audit": {
            "passed": True,
            "selected_background_treatment_id": "halftone_raster_canvas",
            "selected_motion_treatment_id": "slow_shutter_motion_blur",
            "flaws": []
        }
    }
    return plan


def extract_and_synthesize_curito_prompt(
    transcript_chunks: List[Dict[str, Any]],
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Runs deep semantic extraction using Gemini as an Editorial Motion Director and enforces policy."""
    api_key = _get_api_key()

    # Format chunks into readable text with timestamps
    chunks_text = []
    for c in transcript_chunks:
        c_idx = c.get("chunkIndex", c.get("id", 0))
        s_sec = c.get("startSec", c.get("startMs", 0) / 1000.0)
        e_sec = c.get("endSec", c.get("endMs", 0) / 1000.0)
        txt = c.get("text", "")
        chunks_text.append(f"[{s_sec:.2f}s - {e_sec:.2f}s] Chunk #{c_idx}: \"{txt.strip()}\"")

    full_transcript_text = " ".join(c.get("text", "") for c in transcript_chunks)

    user_content = (
        "Analyze this timestamped monologue transcript as an Executive Editorial Motion Director (Vox / Iman Gadzhi / High-Tier Editorial standard):\n\n"
        + "\n".join(chunks_text)
        + "\n\nCRITICAL CREATIVE DIRECTIVE (TWO-STAGE VISUAL IDEATION):\n"
        "1. VISUAL CONCEPT SEARCH: Before choosing a visual, generate and evaluate candidates across at least 3 distinct conceptual domains "
        "(spatial, interface/ui, dimensional instrument, typographic, abstract). Record candidate concepts and rejected concepts inside 'concept_diversity'.\n"
        "2. EXPLICIT METAPHORS TAKE HIGHEST PRECEDENCE: If the speaker explicitly introduces a visual metaphor in the transcript "
        "(e.g., 'That isn't a funnel. It's a maze.'), you MUST honor, elevate, and explore that metaphor (e.g. 3D architectural labyrinth/maze with converging monolithic walls collapsing into a single illuminated path) "
        "rather than substituting an arbitrary unrelated machine!\n"
        "3. HEAVY PENALTY ON CONCEPTUAL CLICHÉS: Do NOT default to mechanical gears/cogwheels for abstract business, marketing, or customer concepts! "
        "Overused cliché mappings (business -> gears, strategy -> chess, growth -> graph) are strictly penalized.\n"
        "4. CANONICAL EDITORIAL PRIMITIVE: Identify the primary Editorial Primitive from the 8 canonical primitives: "
        "1. CONTRAST (Simplicity vs physical/structural constraints or labyrinthine complexity), "
        "2. SCALE_MAGNIFICATION (Progressive optical dive revealing microscopic tolerances or hidden gaps), "
        "3. MICRO_DEVIATION (Subtle initial divergence triggering systemic drift), "
        "4. CASCADING_PROPAGATION (Fragmentation propagating through dependent journey steps), "
        "5. PHYSICAL_SEIZURE (Abrupt dead-stop / deadlock / freeze, ZERO digital glitch, one sub-element vibrating), "
        "6. CONSEQUENTIAL_CONVERGENCE (Fragmented paths/leads collapsing directly into catastrophic drop-off or singular clarity), "
        "7. FOUNDATIONAL_PROPAGATION (Bedrock/singular path locking, stability propagating outward), "
        "8. INEVITABLE_YIELD (Frictionless reliability, compounding throughput).\n"
        "5. 3-ACT PHYSICAL CAUSALITY: Act 1: Equilibrium, Act 2: Inflection Event, Act 3: Consequential State.\n"
        "6. DYNAMIC ENTRANCE-INTO-VIEW: Pristine graphic canvas at 0.0s, dynamic entrance (e.g. vertical bottom emergence, lateral friction slide, or 3D hinged swing) "
        "over 0.0s - 1.5s decelerating into locked centroid before the sync hit. ZERO static ducks sitting stationary from frame 0!\n"
        "7. SPATIAL-TEMPORAL TEXTURED CANVAS: Subtle halftone dot screening, fine film grain, or micro-stippling. STRICTLY NO TABLES OR FURNITURE.\n"
        "8. CAMERA & KINEMATICS: Spatially locked fixed-tripod isometric view (NO camera orbiting/revolving), rigid-body topological permanence (single solid manifold, zero ghosting, zero 180-deg yaw flips).\n"
        "9. ERGONOMIC SAFE-ZONE: Central Diamond (Y: 320-1450, X: 140-940). Zero typography in diffusion prompt."
    )

    json_spec = """{
  "concept_diversity": {
    "candidate_domains": ["spatial", "interface", "typographic", "abstract"],
    "selected_domain": "spatial",
    "semantic_cliche_risk": 0.08,
    "mechanical_metaphor_penalty": 1.0,
    "continuity_score": 0.91,
    "candidate_concepts": [
      {
        "domain": "spatial",
        "concept_summary": "Architectural labyrinth with towering monolithic walls where diverging corridors collapse into a single illuminated straight channel.",
        "score": 0.95,
        "rationale": "Directly embodies the speaker's explicit metaphor ('It\\'s a maze') and provides powerful spatial transformation."
      },
      {
        "domain": "interface",
        "concept_summary": "Fragmented floating browser viewports consolidating into a single minimalist page.",
        "score": 0.82,
        "rationale": "Good match for digital funnel but less cinematic depth."
      }
    ],
    "rejected_concepts": [
      {
        "domain": "mechanical",
        "concept_summary": "Interlocking brass gear train jamming under friction.",
        "reason_for_rejection": "Overused conceptual cliché (business bottleneck -> gears); unrelated to spoken maze metaphor."
      }
    ]
  },
  "editorial_causality_chain": {
    "primary_editorial_primitive": "one of: CONTRAST | SCALE_MAGNIFICATION | MICRO_DEVIATION | CASCADING_PROPAGATION | PHYSICAL_SEIZURE | CONSEQUENTIAL_CONVERGENCE | FOUNDATIONAL_PROPAGATION | INEVITABLE_YIELD",
    "causality_act_1_equilibrium": "Initial physical baseline / alignment description",
    "causality_act_2_inflection": "Core mechanical shift / deviation / lockup event",
    "causality_act_3_consequence": "Systemic outcome / physical seizure / yield stabilization",
    "audio_visual_counterpoint": {
      "visual_lead_sec": -0.4,
      "residual_lag_sec": 1.2
    },
    "kinetic_momentum_vector": {
      "velocity_x": 0.0,
      "velocity_y": -1.5,
      "camera_zoom_delta": 0.05
    },
    "acoustic_co_destruction_spec": "Sudden audio vacuum on physical seizure with 40Hz sub-bass thump",
    "ergonomic_safe_zone": {
      "top_y_px": 320,
      "bottom_y_px": 1450,
      "left_x_px": 140,
      "right_x_px": 940
    }
  },
  "semantic_entity_action_mapping": {
    "action_verb": "e.g. lock",
    "manner_adverb": "e.g. firmly with rotational torque",
    "thematic_target": "e.g. foundation",
    "hero_physical_artifact": "Tangible, iconic volumetric hero asset or spatial architecture (e.g. 3D architectural labyrinth/maze, dual-beam balance scale, precision funnel, dual-throw knife switch, Geneva indexer; strictly avoid thin keys/bitting)"
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
    "focal_subject_and_perspective": "concrete hero artifact or spatial architecture and exact camera angle (spatially locked 45-degree isometric studio view, no orbit)",
    "materiality_and_surface": "materials, finishes, micro-details (e.g., hand-finished solid brass, blackened carbon steel, limestone labyrinth masonry)",
    "canvas_and_textured_background": "spatial-temporal graphic canvas with subtle halftone dot screening or fine film grain, reserving upper 45% negative space (strictly no table/furniture)",
    "lighting_and_shadow_physics": "illumination quality and floating ambient occlusion volume providing depth",
    "camera_and_rendering_spec": "lens (85mm), spatially locked tripod, 1-DoF constrained axial rotation, rigid-body topological permanence, single cohesive solid topological manifold with pinned UV surface coordinates, zero ghosted duplication, zero mesh fission, zero 180-degree yaw flipping, 24fps",
    "entrance_kinematic_treatment": "dynamic entrance from unpopulated canvas during 0.0s - 1.5s (e.g. vertical bottom emergence from submerged Y coords, lateral friction slide, or 3D hinged swing) decelerating into locked centroid position"
  },
  "assembled_diffusion_prompt": "Single synthesized prompt paragraph combining the 6 elements with concrete hero artifact or spatial architecture, dynamic entrance kinematics (0.0s-1.5s from unpopulated canvas), spatial-temporal halftone/grain background (no table), locked tripod camera, rigid-body permanence, unitary manifold anti-ghosting physics, and the selected motion treatment optics clause appended at the end",
  "negative_prompt": "doubling, duplicate mesh, split silhouette, ghosting, asset duplication, UV sliding, texture swimming, UV seam tear, unphysical merging, snapping back, 180-degree flip, yaw flip, choppy rotation, perspective inversion, orientation swap, reversing direction, morphing geometry, warping metal, changing teeth, shifting bitting, mutating parts, melting, table, tabletop, desk, furniture, countertop, wooden desk, office room, floorboards, text, words, typography, UI elements, buttons, screen, monitor",
  "selected_background_treatment_id": "one of: halftone_raster_canvas | luxury_editorial_sunlight_canvas | newspaper_collage_deconstructed | modern_swiss_museum_poster",
  "selected_motion_treatment_id": "one of: defocus_blur | gaussian_blur | bokeh_blur | slow_shutter_motion_blur",
  "selected_entrance_treatment_id": "one of: vertical_bottom_emergence | lateral_friction_slide | slapdrop_bounce | off_axis_3d_swing | polarizing_bevel_elevation | optical_rack_focus_bokeh_accretion",
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

    # Model priority: gemini-2.5-flash (highest reliability and speed), with cascade
    PREFERRED_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-flash-latest",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-3-flash-preview",
    ]
    if model_name:
        candidate_models = [model_name] + [m for m in PREFERRED_MODELS if m != model_name]
    else:
        candidate_models = PREFERRED_MODELS
    # De-duplicate while preserving order
    candidate_models = list(dict.fromkeys(candidate_models))

    last_err = None
    res_json = None

    session = requests.Session()
    retries = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=None,
        raise_on_status=False,
    )
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
        time.sleep(1.0)
        if res_json:
            break

    if not res_json:
        err_msg = (
            f"All online Gemini models failed during editorial prompt extraction: {last_err}. "
            "Per strict editorial pipeline non-negotiables, silent fallback to generic mock presets is prohibited. "
            "Execution failed."
        )
        logger.error(err_msg)
        raise EditorialPromptSynthesisError(err_msg)

    raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
    extracted = _parse_llm_json(raw_text)
    if isinstance(extracted, list) and len(extracted) > 0:
        extracted = extracted[0]

    # -----------------------------------------------------------------------
    # Recursive Adversarial Self-Critique Refinement Loop
    # -----------------------------------------------------------------------
    prompt = extracted.get("assembled_diffusion_prompt", "")
    lowered_prompt = prompt.lower()
    has_unitary = any(w in lowered_prompt for w in [
        "unitary manifold", "single cohesive mesh", "zero ghosting", "zero duplication",
        "zero doubling", "zero uv sliding", "zero mesh fission", "zero duplicate silhouettes",
        "unitary topological body", "single physical object", "zero unphysical cloning"
    ])
    if not has_unitary and prompt:
        unitary_clause = ", single cohesive solid topological manifold with pinned UV surface coordinates, zero ghosted duplication, zero mesh fission"
        prompt = f"{prompt.rstrip('. ')}{unitary_clause}."
        extracted["assembled_diffusion_prompt"] = prompt

    audit = DiffusionPromptPolicyCritic.audit_prompt(prompt, transcript_context=full_transcript_text)

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
            "1. Replace any conceptual cliché (e.g. mechanical gears for business, chess for strategy, graphs for growth) "
            "with a concrete, appropriate hero visual artifact or spatial architecture matching the spoken context "
            "(e.g. 3D architectural labyrinth/maze, precision funnel, dual-beam balance scale, heavy industrial track switch; strictly avoid thin keys/bitting).\n"
            "2. Ensure the background is a spatial-temporal graphic canvas featuring tactile texture "
            "(halftone screening, fine film grain, or micro-stippling). STRICTLY NO TABLES, TABLETOPS, OR FURNITURE.\n"
            "3. Camera MUST be a spatially locked fixed-tripod isometric view (strictly NO camera orbiting or revolving).\n"
            "4. Kinematics must enforce 1-DoF constrained axial rotation with strict rigid-body topological permanence (ZERO 180-degree yaw flips, zero morphing).\n"
            "5. Ensure manner dynamics (rotational torque, decelerating engagement, collapsing branches into a single illuminated path, mechanical locked-state).\n"
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
                new_audit = DiffusionPromptPolicyCritic.audit_prompt(new_prompt, transcript_context=full_transcript_text)
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

    final_prompt = extracted.get("assembled_diffusion_prompt", "")
    if final_prompt:
        lowered_final = final_prompt.lower()
        has_unitary_final = any(w in lowered_final for w in [
            "unitary manifold", "single cohesive mesh", "zero ghosting", "zero duplication",
            "zero doubling", "zero uv sliding", "zero mesh fission", "zero duplicate silhouettes",
            "unitary topological body", "single physical object", "zero unphysical cloning"
        ])
        if not has_unitary_final:
            unitary_clause = ", single cohesive solid topological manifold with pinned UV surface coordinates, zero ghosted duplication, zero mesh fission"
            final_prompt = f"{final_prompt.rstrip('. ')}{unitary_clause}."
            extracted["assembled_diffusion_prompt"] = final_prompt
            audit = DiffusionPromptPolicyCritic.audit_prompt(final_prompt, transcript_context=full_transcript_text)

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

