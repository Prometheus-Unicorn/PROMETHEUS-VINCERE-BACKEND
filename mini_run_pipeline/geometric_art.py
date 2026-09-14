"""Geometric Art & Taste Creator Photo Treatment Engine for Prometheus Mini-Run.

Provides high-tier cinematic treatments for images and rapid-fire multi-image transitions:
1. Geometric Drafting: Technical architectural drafting overlay (corner brackets ⌜⌟, crosshairs ＋,
   coordinate labels, modular dividers, frame telemetry).
2. Dither Print: Bayer 4x4 and Atkinson dither matrices with duotone ink palettes (Cobalt Paper,
   Signal Red, Mono Press, Cyan Spectral, Electric Ultraviolet).
3. Contour Atlas: Topographic isocontour lines and Marching Squares flowline elevation maps.
4. Spectral Curtain: Vertical slit extrusion with chromatic separation (red/cyan channel offset)
   and scanlines.
5. Multi-Image Strobe Transition: Rapid-fire photo burst across a single beat/transition
   (3-8 image variations flashing at 1-2 frames/slice with chromatic aberration, white lens flash burn,
   and shutter telemetry).
6. Geometric Contact Sheet: Editorial split-screen layouts (split_duo, quad_grid, asymmetric_hero)
   with technical drafting coordinates.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


VALID_PHOTO_TREATMENTS = {
    "none",
    "geometric_drafting",
    "dither_print",
    "contour_atlas",
    "spectral_curtain",
}

VALID_DITHER_PALETTES = {"cobalt", "signal", "mono", "cyan", "electric"}
VALID_DITHER_ALGORITHMS = {"bayer4", "atkinson", "floyd-steinberg"}
VALID_CONTACT_LAYOUTS = {"split_duo", "tri_slice", "quad_grid", "asymmetric_hero"}


def plan_photo_treatment(
    asset_id: str,
    tone: str = "technical",
    treatment_type: Optional[str] = None,
    seed: int = 42,
    custom_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generates a deterministic photo treatment configuration for an image asset."""
    opts = custom_options or {}

    # Auto-resolve treatment if not explicitly specified
    if not treatment_type or treatment_type not in VALID_PHOTO_TREATMENTS:
        tone_lower = tone.lower()
        if any(w in tone_lower for w in ["tech", "code", "architecture", "precision", "draft"]):
            treatment_type = "geometric_drafting"
        elif any(w in tone_lower for w in ["print", "editorial", "retro", "raw", "dither"]):
            treatment_type = "dither_print"
        elif any(w in tone_lower for w in ["topography", "map", "nature", "contour", "elevation"]):
            treatment_type = "contour_atlas"
        elif any(w in tone_lower for w in ["cyber", "glitch", "spectral", "light", "energy"]):
            treatment_type = "spectral_curtain"
        else:
            treatment_type = "geometric_drafting"

    plan: Dict[str, Any] = {
        "assetId": asset_id,
        "type": treatment_type,
        "seed": seed,
    }

    if treatment_type == "geometric_drafting":
        accent = opts.get("accentColor", "#00F0FF" if "cyber" in tone else "#38BDF8")
        plan["drafting"] = {
            "gridModules": opts.get("gridModules", 8),
            "showCoordinates": opts.get("showCoordinates", True),
            "showBrackets": opts.get("showBrackets", True),
            "showCrosshairs": opts.get("showCrosshairs", True),
            "accentColor": accent,
            "textColor": opts.get("textColor", "rgba(255, 255, 255, 0.75)"),
            "seed": seed,
            "metadataLabels": opts.get("metadataLabels", []),
        }

    elif treatment_type == "dither_print":
        palette = opts.get("palette", "cobalt")
        if palette not in VALID_DITHER_PALETTES:
            palette = "cobalt"
        algo = opts.get("algorithm", "bayer4")
        if algo not in VALID_DITHER_ALGORITHMS:
            algo = "bayer4"
        plan["dither"] = {
            "algorithm": algo,
            "palette": palette,
            "cellSize": opts.get("cellSize", 6),
            "contrast": opts.get("contrast", 1.4),
            "invert": opts.get("invert", False),
            "blendMode": opts.get("blendMode", "multiply"),
            "opacity": opts.get("opacity", 0.95),
        }

    elif treatment_type == "contour_atlas":
        plan["contour"] = {
            "levels": opts.get("levels", 12),
            "opacity": opts.get("opacity", 0.65),
            "drift": opts.get("drift", 16),
            "style": opts.get("style", "topographic"),
            "strokeColor": opts.get("strokeColor", "rgba(0, 240, 255, 0.45)"),
            "seed": seed,
        }

    elif treatment_type == "spectral_curtain":
        plan["curtain"] = {
            "curtainDensity": opts.get("curtainDensity", 32),
            "curtainLength": opts.get("curtainLength", 0.65),
            "curtainOpacity": opts.get("curtainOpacity", 0.55),
            "direction": opts.get("direction", "down"),
            "chromaticShift": opts.get("chromaticShift", 4),
        }

    return plan


def plan_multi_image_strobe_transition(
    images: List[str],
    duration_frames: int = 10,
    strobe_interval: int = 1,
    enable_lens_flash: bool = True,
    enable_chromatic_aberration: bool = True,
    enable_drafting_hud: bool = True,
    accent_color: str = "#00F0FF",
    sfx_cue: Optional[str] = "shutter_burst_whoosh",
) -> Dict[str, Any]:
    """Plans a rapid-fire multi-image strobe transition across a cut or asset reveal."""
    safe_images = list(images) if images else ["/placeholder.jpg"]

    # Calculate total unique slices shown during transition
    slices_shown = max(1, duration_frames // max(1, strobe_interval))

    return {
        "type": "multi_image_strobe",
        "images": safe_images,
        "imageCount": len(safe_images),
        "durationInFrames": duration_frames,
        "strobeInterval": strobe_interval,
        "slicesShown": slices_shown,
        "enableLensFlash": enable_lens_flash,
        "enableChromaticAberration": enable_chromatic_aberration,
        "enableDraftingHUD": enable_drafting_hud,
        "accentColor": accent_color,
        "sfxCue": sfx_cue,
    }


def plan_geometric_contact_sheet(
    images: List[str],
    layout: str = "asymmetric_hero",
    duration_frames: int = 30,
    accent_color: str = "#00F0FF",
    coordinates: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Plans a geometric contact sheet multi-pane layout."""
    if layout not in VALID_CONTACT_LAYOUTS:
        layout = "asymmetric_hero"

    safe_coords = coordinates or [f"SEC-{str(i+1).zfill(2)}" for i in range(len(images))]

    return {
        "type": "geometric_contact_sheet",
        "images": images,
        "layout": layout,
        "durationInFrames": duration_frames,
        "accentColor": accent_color,
        "coordinates": safe_coords,
        "showDraftingMarks": True,
    }
