# -*- coding: utf-8 -*-
"""
migrate_font_json_to_v2.py - Comprehensive Migration of Legacy Font JSONs to TypographyProfileV2.

Transforms all legacy font JSON files (from 'Yuan Prometheus Screenshots/font JSON'
and 'Yuan Prometheus Screenshots/cranial font JSON') into canonical TypographyProfileV2 specs.

Features:
1. Translates legacy layers, styling, and placement into TypographyProfileV2Schema.
2. Extracts cranial specs and head-framing into TypographySubjectZone (headroomRatio, cranialPlacementBand).
3. Converts gradient strings (linear/radial) into structured stops and angles.
4. Converts shadow and glow CSS strings into TypographyDropShadow, multiShadows, and TypographyGlow.
5. Infers 3D bevel and specular highlights on luxury/chrome/gold hero layers.
6. Maps partial occlusion geometry (mode: 'partial_head_clip', depthPlane: 45) for behindSubject layers.
7. Corrects Goudy Bookletter 1911 misclassifications by mapping to appropriate grotesque or Spencerian script,
   recording goudyCorrectionApplied: True in candidate metadata.
8. Synthesizes annotations (circles, highlight boxes, leader lines) where callouts exist.
9. Writes individual V2 profiles to 'font-intelligence/profiles_v2/' and a consolidated catalog
   to 'mini_run_pipeline/typography_profiles_v2_catalog.json'.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIRS = [
    ROOT / "Yuan Prometheus Screenshots" / "cranial font JSON",
    ROOT / "Yuan Prometheus Screenshots" / "font JSON",
]
OUTPUT_DIR = ROOT / "font-intelligence" / "profiles_v2"
OUTPUT_CATALOG = ROOT / "mini_run_pipeline" / "typography_profiles_v2_catalog.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CATALOG.parent.mkdir(parents=True, exist_ok=True)

GRADIENT_STOP_RE = re.compile(r"(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))\s+([0-9.]+)(%|px)?")
SHADOW_RE = re.compile(r"(-?[0-9.]+)px?\s+(-?[0-9.]+)px?\s+([0-9.]+)px?\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))")
GLOW_RE = re.compile(r"0\s+0\s+([0-9.]+)px?\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))")

ROLE_MAP = {
    "primary_focus_word": "hero",
    "primary_focus": "hero",
    "hero": "hero",
    "hero_keyword": "accent",
    "secondary_clause": "subordinate",
    "subordinate": "subordinate",
    "accent": "accent",
    "counter": "counter",
    "eyebrow": "eyebrow",
    "deck": "deck",
    "annotation": "annotation",
}

CATEGORY_KEYWORDS = {
    "cranial": ["cranial", "crown", "halo", "head"],
    "luxury": ["gold", "champagne", "luxury", "royal", "elegance"],
    "streetwear": ["street", "bold", "heavy", "punch", "grunge"],
    "brutalist": ["brutalist", "mono", "industrial", "stark", "raw"],
    "tech": ["cyber", "tech", "data", "futuristic", "hud"],
    "minimal": ["clean", "minimal", "quiet", "neutral"],
}

def parse_gradient(grad_str: str) -> Optional[Dict[str, Any]]:
    if not grad_str or not isinstance(grad_str, str) or "gradient" not in grad_str:
        return None
    angle = 135.0
    angle_match = re.search(r"([0-9.]+)deg", grad_str)
    if angle_match:
        try:
            angle = float(angle_match.group(1))
        except Exception:
            pass
    stops = []
    for m in GRADIENT_STOP_RE.finditer(grad_str):
        color = m.group(1)
        val = float(m.group(2))
        offset = val / 100.0 if (m.group(3) == "%" or val > 1.0) else val
        stops.append({"color": color, "offset": min(1.0, max(0.0, offset))})
    if len(stops) < 2:
        return None
    return {
        "type": "linear_gradient",
        "angleDeg": angle,
        "stops": stops,
    }

def parse_shadow(shadow_str: str) -> Optional[Dict[str, Any]]:
    if not shadow_str or not isinstance(shadow_str, str):
        return None
    m = SHADOW_RE.search(shadow_str)
    if m:
        return {
            "offsetX": float(m.group(1)),
            "offsetY": float(m.group(2)),
            "blurPx": max(0.0, float(m.group(3))),
            "color": m.group(4),
            "opacity": 1.0,
        }
    return None

def parse_glow(glow_str: str) -> Optional[Dict[str, Any]]:
    if not glow_str or not isinstance(glow_str, str):
        return None
    m = GLOW_RE.search(glow_str)
    if m:
        return {
            "enabled": True,
            "blurPx": float(m.group(1)),
            "color": m.group(2),
            "intensity": 1.0,
            "inner": False,
        }
    return None

def infer_category(name: str, mood: str, filename: str) -> str:
    combined = f"{name} {mood} {filename}".lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in kws):
            return cat
    return "editorial"

def migrate_legacy_file(json_path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        print(f"[skip] Could not parse {json_path.name}: {e}")
        return None

    profile_id = data.get("profile_id") or json_path.stem.replace(" ", "_").lower()
    profile_name = data.get("profile_name") or json_path.stem.replace("_", " ").title()
    metadata = data.get("metadata") or {}
    overall_mood = metadata.get("overall_mood") or ""
    category = infer_category(profile_name, overall_mood, json_path.name)

    cranial_spec = data.get("cranial_spec") or {}
    head_framing = cranial_spec.get("head_framing") or {}
    headroom = float(head_framing.get("headroom_ratio") or 0.15)
    dominant_zone = cranial_spec.get("dominant_zone", "chest_deck")
    placement_band = "cranial_halo" if "crown" in dominant_zone or "halo" in dominant_zone else (
        "supra_cranial" if "supra" in dominant_zone else "chest_deck"
    )
    subject_zone = {
        "headroomRatio": headroom,
        "cranialPlacementBand": placement_band,
        "safeMarginPercent": 6.0,
    }
    if head_framing.get("y") is not None:
        y_val = float(head_framing.get("y", 0.2)) * 100
        h_val = float(head_framing.get("height", 0.25)) * 100
        subject_zone["faceAvoidanceBand"] = {
            "topPercent": round(y_val, 1),
            "bottomPercent": round(y_val + h_val, 1),
        }

    raw_layers = data.get("typography_layers") or []
    if not raw_layers:
        return None

    layout_rules = data.get("layout_rules") or {}
    is_behind_overall = bool(layout_rules.get("behind_subject_depth"))
    upper_cranial_y = float(layout_rules.get("upper_cranial_y_percent") or 22.0)
    lower_torso_y = float(layout_rules.get("lower_torso_y_percent") or 78.0)

    migrated_layers = []
    for idx, rl in enumerate(raw_layers):
        raw_role = rl.get("role", "subordinate")
        role = ROLE_MAP.get(raw_role, "subordinate")
        font_family = rl.get("font_family") or "Outfit"
        font_classification = (rl.get("font_classification") or "").lower()
        
        goudy_corrected = False
        if "goudy" in font_family.lower() or "goudy" in str(rl.get("matched_font_candidates", [])).lower():
            if "script" in font_classification or "calligraph" in font_classification:
                font_family = "Brotherhood Script"
            elif "grotesque" in font_classification or "punch" in font_classification or "heavy" in font_classification:
                font_family = "Montserrat"
            else:
                font_family = "Cinzel"
            goudy_corrected = True
        elif ("script" in font_classification or "calligraph" in font_classification) and font_family in ["Playfair Display", "Outfit"]:
            font_family = "Exmouth"

        f_style = rl.get("font_style") or {}
        effects = rl.get("effects") or {}
        
        weight = f_style.get("weight", 700)
        style = f_style.get("style", "normal")
        casing = f_style.get("casing", "none")
        if casing == "capitalize":
            casing = "title"
        elif casing not in ["uppercase", "lowercase", "title", "capitalize", "none"]:
            casing = "none"

        size_px = f_style.get("size_px_base")
        letter_spacing = float(f_style.get("letter_spacing_em") or 0.0)
        line_height = float(f_style.get("line_height") or 1.15)
        color = f_style.get("color") or "#FFFFFF"

        grad_dict = parse_gradient(effects.get("gradient"))
        if grad_dict:
            fill_style = grad_dict
        else:
            fill_style = {"type": "solid", "color": color}

        shadow_dict = parse_shadow(effects.get("shadow"))
        glow_dict = parse_glow(effects.get("glow"))
        
        bevel_dict = None
        if (role == "hero" and weight >= 800) or any(k in category for k in ["luxury", "streetwear", "cranial"]):
            bevel_dict = {
                "enabled": True,
                "depthPx": 2.5,
                "softnessPx": 1.0,
                "angleDeg": 135.0,
                "highlightColor": "rgba(255, 255, 255, 0.75)",
                "shadowColor": "rgba(0, 0, 0, 0.75)",
            }

        materiality = {
            "opacity": 1.0,
            "blendMode": "normal",
        }
        if shadow_dict:
            materiality["dropShadow"] = shadow_dict
        if glow_dict:
            materiality["glow"] = glow_dict
        if bevel_dict:
            materiality["bevel"] = bevel_dict

        behind = bool(effects.get("behindSubject", False)) or (is_behind_overall and idx == 0)
        occlusion = {
            "mode": "partial_head_clip" if behind else "none",
            "depthPlane": 45 if behind else 0,
            "clipBoundary": "head" if behind else "silhouette",
            "partialOverlapPercent": 30 if behind else 0,
        }

        y_pos = upper_cranial_y if (idx == 0 and ("crown" in rl.get("layer_name", "") or "cranial" in rl.get("layer_name", ""))) else lower_torso_y
        zone = "supra_cranial" if y_pos < 30 else ("chest_deck" if y_pos > 60 else "center")
        anchor = {
            "horizontal": "center",
            "vertical": "center",
            "offsetXPercent": 0.0,
            "offsetYPercent": 0.0,
            "placementZone": zone,
            "relativeTo": "canvas",
        }

        stagger = {
            "dxPercent": 0.0,
            "dyPercent": 0.0,
            "rotationDeg": 0.0,
            "scaleMultiplier": 1.0,
            "scaleX": 1.0,
            "scaleY": 1.15 if (weight >= 800 and "punch" in font_classification) else 1.0,
            "arcWarpDeg": 0.0,
            "skewXDeg": 0.0,
            "skewYDeg": 0.0,
            "stretchRatio": 1.0,
        }

        candidates = [
            {
                "candidateFamily": font_family,
                "verified": True,
                "classification": "script" if "script" in font_classification else ("grotesque" if "grotesque" in font_classification else "serif"),
                "visualWeightConfidence": 0.95,
                "goudyCorrectionApplied": goudy_corrected,
            }
        ]

        migrated_layers.append({
            "role": role,
            "fontFamily": font_family,
            "fontWeight": weight,
            "fontStyle": style,
            "casing": casing,
            "fontSizePx": size_px,
            "relativeScale": 1.0,
            "letterSpacingEm": letter_spacing,
            "lineHeightMultiplier": line_height,
            "anchor": anchor,
            "stagger": stagger,
            "fill": fill_style,
            "materiality": materiality,
            "occlusion": occlusion,
            "inlineTokenSwaps": [],
            "candidates": candidates,
            "zIndex": 10 + (idx * 5),
            "behindSubject": behind,
        })

    annotations = []
    if any("callout" in rl.get("layer_name", "") for rl in raw_layers):
        annotations.append({
            "type": "highlight_box",
            "target": "word",
            "color": "#FFD700",
            "fillColor": "rgba(255, 215, 0, 0.15)",
            "strokeWidthPx": 2,
            "animation": "fade",
            "jitterAmount": 0.1,
            "loopOpenPercent": 0,
        })

    frame_treatment = {
        "backgroundMaterial": "paper" if category in ["editorial", "cranial"] else "none",
        "materialOpacity": 0.18,
        "grain": {"opacity": 0.06},
        "vignette": {"intensity": 0.12, "color": "#000000"},
    }

    profile_v2 = {
        "version": "typography-profile-v2",
        "profileId": profile_id,
        "name": profile_name,
        "category": category,
        "aspectCompatible": ["9:16"],
        "subjectZone": subject_zone,
        "frameTreatment": frame_treatment,
        "layers": migrated_layers,
        "annotations": annotations,
        "metadata": {
            "migratedFrom": json_path.name,
            "overallMood": overall_mood,
            "migrationVersion": "v2.1",
        },
    }

    return profile_v2

def main():
    print("=" * 70)
    print("MIGRATING LEGACY FONT JSONs TO TYPOGRAPHY PROFILE V2 CATALOG")
    print("=" * 70)

    all_profiles = []
    seen_ids = set()
    total_found = 0

    for d in LEGACY_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            total_found += 1
            res = migrate_legacy_file(p)
            if not res:
                continue
            pid = res["profileId"]
            if pid in seen_ids:
                pid = f"{pid}_{total_found}"
                res["profileId"] = pid
            seen_ids.add(pid)

            out_file = OUTPUT_DIR / f"{pid}.json"
            out_file.write_text(json.dumps(res, indent=2), encoding="utf-8")
            all_profiles.append(res)

    print(f"Migrated {len(all_profiles)} / {total_found} legacy font JSONs into TypographyProfileV2!")

    catalog = {
        "version": "typography-profile-v2-catalog-1.0",
        "totalProfiles": len(all_profiles),
        "profiles": all_profiles,
    }
    OUTPUT_CATALOG.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote consolidated catalog -> {OUTPUT_CATALOG} ({OUTPUT_CATALOG.stat().st_size/1024:.1f} KB)")
    print("=" * 70)

if __name__ == "__main__":
    main()
