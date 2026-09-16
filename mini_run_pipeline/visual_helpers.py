"""Visual Helper Intelligence & Cinematic Animation Engine for Prometheus Mini-Run.

Provides high-tier visual assets that slide in to bolster key talking points:
1. before_after_comparison: Split-view comparison or reveal wipe divider (e.g. before/after, vs, instead of).
2. listicle: Staggered animated bullet-card reveals with liquid glass backplates.
3. motion_number: Kinetic rolling digit odometer / count-up metric display.
4. callout_badge: Sliding high-impact asset card with iconography and key takeaways.

Cinematic textures & shaders:
- liquid_glass: SVG feTurbulence + feDisplacementMap + multi-layer inner shadow & specular glow.
- blur_vignette: Radial edge blur vignette container.
- liquid_gradient / mesh_gradient: Multi-stop undulating radial gradients.
- liquid_ripple: Frame-driven sinusoidal wave displacement.
- noise_overlay: Organic film grain texture.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Semantic Trigger Patterns
# ---------------------------------------------------------------------------

COMPARISON_PATTERNS = [
    re.compile(r"\b(?:before\s+and\s+after)\b", re.IGNORECASE),
    re.compile(r"\b(\w+[\w\s]{1,20}?)\s+(?:vs\.?|versus|compared\s+to|as\s+opposed\s+to)\s+(\w+[\w\s]{1,20}?)\b", re.IGNORECASE),
    re.compile(r"\b(?:instead\s+of)\s+([^,.;]+?)(?:,\s*|\s+we\s+|\s+use\s+|\s+choose\s+|\s+do\s+)([^,.;]+)", re.IGNORECASE),
    re.compile(r"\b(?:switch(?:ed)?\s+from)\s+([^,.;]+?)\s+to\s+([^,.;]+)", re.IGNORECASE),
    re.compile(r"\b(?:difference\s+between)\s+([^,.;]+?)\s+and\s+([^,.;]+)", re.IGNORECASE),
]

MOTION_NUMBER_PATTERNS = [
    # Currency values like $50,000, $1.5M, $250k
    re.compile(r"(\$|€|£)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*([kmbt])?\b", re.IGNORECASE),
    # Percentages like 300%, 85.5%
    re.compile(r"\b(\d+(?:,\d+)*(?:\.\d+)?)\s*%\b"),
    # Multipliers like 10x, 3.5x
    re.compile(r"\b(\d+(?:\.\d+)?)\s*x\b", re.IGNORECASE),
    # Numerical counts over 100 with metric nouns: 10,000 users, 500 hours
    re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d{3,9})\s+([a-zA-Z]+)\b"),
]

CALLOUT_PATTERNS = [
    re.compile(r"\b(?:pro\s*tip|golden\s*rule|key\s*takeaway|the\s*secret\s*is|remember\s*this|rule\s*number\s*one|bottom\s*line)\b", re.IGNORECASE),
    re.compile(r"\b(?:warning|critical|crucial|essential|fundamental|do\s*not\s*forget)\b", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Helper Extraction & Planning
# ---------------------------------------------------------------------------

def _extract_metric_number(text: str) -> Optional[Dict[str, Any]]:
    """Inspect text for strong numerical/metric claims suitable for motion_number."""
    # 1. Currency
    m_curr = re.search(r"(\$|€|£)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*([kmbtKMBT])?", text)
    if m_curr:
        curr_sym = m_curr.group(1)
        raw_val = float(m_curr.group(2).replace(",", ""))
        unit = (m_curr.group(3) or "").upper()
        multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000, "T": 1_000_000_000_000}.get(unit, 1)
        full_value = raw_val * multiplier if unit else raw_val
        return {
            "type": "motion_number",
            "value": full_value,
            "targetValue": full_value,
            "prefix": curr_sym,
            "suffix": unit if unit else "",
            "format": "currency",
            "texture": "liquid_glass",
            "title": "METRIC IMPACT",
            "position": "flank_right",
        }

    # 2. Percentage
    m_pct = re.search(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*%", text)
    if m_pct:
        val = float(m_pct.group(1).replace(",", ""))
        return {
            "type": "motion_number",
            "value": val,
            "targetValue": val,
            "prefix": "+",
            "suffix": "%",
            "format": "percent",
            "texture": "liquid_glass",
            "title": "PERFORMANCE",
            "position": "flank_right",
        }

    # 3. Multiplier
    m_mult = re.search(r"\b(\d+(?:\.\d+)?)\s*[xX]\b", text)
    if m_mult:
        val = float(m_mult.group(1))
        return {
            "type": "motion_number",
            "value": val,
            "targetValue": val,
            "prefix": "",
            "suffix": "X",
            "format": "number",
            "texture": "mesh_gradient",
            "title": "MULTIPLIER",
            "position": "flank_right",
        }

    VALID_METRIC_NOUNS = {
        "USERS", "CLIENTS", "CUSTOMERS", "DOWNLOADS", "SUBSCRIBERS",
        "MEMBERS", "REVIEWS", "HOURS", "DAYS", "WEEKS", "MONTHS", "YEARS",
        "UNITS", "ORDERS", "TRANSACTIONS", "SALES", "LEADS", "PEOPLE",
        "STUDENTS", "PRODUCTS", "ITEMS", "COMPANIES", "BUSINESSES", "BRANDS",
        "DOLLARS", "EUROS", "POUNDS", "CALLS", "VISITORS", "VIEWS", "IMPRESSIONS",
    }

    # 4. Large raw count (Strict noun gate: requires a recognized metric noun, prevents capturing adjectives like 'physical')
    m_count = re.search(r"\b(\d{1,3}(?:,\d{3})+|\d{3,9})\s+([a-zA-Z]+)\b", text)
    if m_count:
        num_str = m_count.group(1).replace(",", "")
        val = float(num_str)
        noun = m_count.group(2).upper()
        if noun in VALID_METRIC_NOUNS and val >= 50:
            return {
                "type": "motion_number",
                "value": val,
                "targetValue": val,
                "prefix": "",
                "suffix": f" {noun}",
                "format": "number",
                "texture": "liquid_glass",
                "title": f"TOTAL {noun}",
                "position": "flank_right",
            }

    return None

def _extract_comparison(text: str) -> Optional[Dict[str, Any]]:
    """Inspect text for contrasting entities or before/after comparison."""
    # Before and after
    if re.search(r"\b(?:before\s+and\s+after)\b", text, re.IGNORECASE):
        return {
            "type": "before_after_comparison",
            "title": "TRANSFORMATION",
            "beforeLabel": "BEFORE",
            "beforeValue": "Old Method",
            "afterLabel": "AFTER",
            "afterValue": "Streamlined",
            "texture": "liquid_glass",
            "splitRatio": 0.5,
            "position": "lower_deck",
            "rippleEffect": True,
        }

    # "X vs Y" or "X versus Y"
    m_vs = re.search(r"\b([a-zA-Z0-9\s]{2,30})\s+(?:vs\.?|versus|compared\s+to)\s+([a-zA-Z0-9\s]{2,30})", text, re.IGNORECASE)
    if m_vs:
        left = m_vs.group(1).strip().title()
        right = m_vs.group(2).strip().title()
        return {
            "type": "before_after_comparison",
            "title": "HEAD TO HEAD",
            "beforeLabel": left[:24],
            "beforeValue": "Standard",
            "afterLabel": right[:24],
            "afterValue": "Optimized",
            "texture": "liquid_glass",
            "splitRatio": 0.5,
            "position": "lower_deck",
            "rippleEffect": True,
        }

    # "Instead of X, Y"
    m_instead = re.search(r"\b(?:instead\s+of)\s+([^,.;]+?)(?:,\s*|\s+we\s+|\s+use\s+|\s+choose\s+|\s+do\s+)([^,.;]+)", text, re.IGNORECASE)
    if m_instead:
        old_opt = m_instead.group(1).strip().title()
        new_opt = m_instead.group(2).strip().title()
        return {
            "type": "before_after_comparison",
            "title": "THE PARADIGM SHIFT",
            "beforeLabel": "OBSOLETE",
            "beforeValue": old_opt[:20],
            "afterLabel": "RECOMMENDED",
            "afterValue": new_opt[:20],
            "texture": "liquid_gradient",
            "splitRatio": 0.5,
            "position": "lower_deck",
            "rippleEffect": True,
        }

    # "Moving / shifting / switching from X to Y"
    m_shift = re.search(r"\b(?:moving|shifting|switching)\s+(?:now\s+)?(?:from\s+|for\s+)?([^,.;]+?)\s+to\s+([^,.;]+)", text, re.IGNORECASE)
    if m_shift:
        old_opt = m_shift.group(1).strip().title()
        new_opt = m_shift.group(2).strip().title()
        return {
            "type": "before_after_comparison",
            "title": "THE PARADIGM SHIFT",
            "beforeLabel": "OLD FOCUS",
            "beforeValue": old_opt[:24],
            "afterLabel": "NEW FOCUS",
            "afterValue": new_opt[:24],
            "texture": "liquid_gradient",
            "splitRatio": 0.5,
            "position": "lower_deck",
            "rippleEffect": True,
        }

    return None

def _extract_callout_badge(text: str) -> Optional[Dict[str, Any]]:
    """Inspect text for golden rules, pro tips, and crucial warnings."""
    text_lower = text.lower()
    if any(k in text_lower for k in ("pro tip", "protip")):
        return {
            "type": "callout_badge",
            "title": "PRO TIP",
            "subtitle": text[:48],
            "badge": "TACTICAL INSIGHT",
            "icon": "zap",
            "texture": "mesh_gradient",
            "position": "flank_right",
        }
    if "golden rule" in text_lower or "rule number one" in text_lower:
        return {
            "type": "callout_badge",
            "title": "GOLDEN RULE",
            "subtitle": text[:48],
            "badge": "NON-NEGOTIABLE",
            "icon": "star",
            "texture": "liquid_glass",
            "position": "flank_right",
        }
    if "key takeaway" in text_lower or "bottom line" in text_lower:
        return {
            "type": "callout_badge",
            "title": "KEY TAKEAWAY",
            "subtitle": text[:48],
            "badge": "CORE PRINCIPLE",
            "icon": "target",
            "texture": "liquid_glass",
            "position": "flank_right",
        }
    if "warning" in text_lower or "critical" in text_lower:
        return {
            "type": "callout_badge",
            "title": "CRITICAL ALERT",
            "subtitle": text[:48],
            "badge": "ATTENTION",
            "icon": "alert",
            "texture": "liquid_glass",
            "position": "flank_right",
        }
    return None

def _extract_calendar_widget(text: str) -> Optional[Dict[str, Any]]:
    """Inspect text for calendar, scheduling, or agenda concepts to trigger Origin UI calendar widget."""
    text_lower = text.lower()
    calendar_keywords = ["calendar", "calendars", "schedule", "scheduling", "day planner", "agenda", "timeline"]
    if any(re.search(rf"\b{k}\b", text_lower) for k in calendar_keywords):
        return {
            "type": "calendar_widget",
            "title": "October 2026",
            "subtitle": "Packed Calendar ≠ True Progress",
            "badge": "CALENDAR OVERLOAD",
            "texture": "liquid_glass",
            "position": "flank_right",
            "durationMs": 4800,
        }
    return None

def _extract_time_widget(text: str) -> Optional[Dict[str, Any]]:
    """Inspect text for finite time, time capital, or non-renewable hours to trigger Origin UI time/hourglass widget."""
    text_lower = text.lower()
    if re.search(r"\btime\b", text_lower) and any(
        re.search(rf"\b{k}\b", text_lower)
        for k in ["managed", "manage", "management", "capital", "finite", "non-renewable", "allocation", "waste"]
    ):
        return {
            "type": "time_widget",
            "title": "Time Is Non-Renewable",
            "badge": "FINITE CAPITAL",
            "subtitle": "Fixed 24h allocation — zero carryover",
            "texture": "geometric_drafting",
            "position": "cranial_top",
            "imageSrc": "showcase-assets/hourglass-sand.png",
            "durationMs": 5200,
            "accentColor": "#FBBF24",
        }
    return None

def _extract_optical_rack_focus(text: str) -> Optional[Dict[str, Any]]:
    """Inspect text for cinematic focus, priority inflection, or pivotal decisions."""
    text_lower = text.lower()
    if any(re.search(rf"\b{k}\b", text_lower) for k in [
        "rack focus", "lens breathing", "focal point", "priorities", "competing priorities",
        "inflection point", "something has to win", "sharp focus"
    ]):
        m_pri = re.search(r"\b(competing\s+priorities|something\s+has\s+to\s+win|inflection\s+point|focal\s+point|priorities)\b", text_lower)
        headline = m_pri.group(1).upper() if m_pri else "CINEMATIC FOCUS"
        return {
            "type": "optical_rack_focus",
            "headlineText": headline,
            "subtitleText": "PHYSICAL LENS BREATHING & KINETIC COMPRESSION",
            "position": "fullscreen",
            "enableBloom": True,
            "enableVignette": True,
            "enableLetterbox": False,
            "enableFilmGrain": True,
            "enableFloorShadow": True,
            "focalPlaneRole": "primary",
        }
    return None

def detect_and_plan_visual_helpers(
    chunks: List[Dict[str, Any]],
    design: Optional[Dict[str, Any]] = None,
) -> Dict[int, Dict[str, Any]]:
    """Scan transcript chunks and generate structured visual helper overlays.
    
    Supports:
    - Manual overrides from design_input or chunk['visualHelper'].
    - Automatic semantic detection for calendar widget, time widget, comparison, metric/number, listicle, and callout badge.
    - Anti-fatigue cooldown so helpers don't overcrowd the screen (minimum 2 chunks gap).
    """
    design_dict = design if isinstance(design, dict) else {}
    explicit_helpers = design_dict.get("visualHelpers") or {}

    # Strict governance: check if automated visual helpers are disabled
    auto_helpers_allowed = design_dict.get("allowAutoVisualHelpers", True)
    if design_dict.get("disableVisualHelpers") or design_dict.get("enableVisualHelpers") is False:
        auto_helpers_allowed = False

    plans: Dict[int, Dict[str, Any]] = {}
    last_helper_idx = -999
    last_type_idx: Dict[str, int] = {}

    for idx, chunk in enumerate(chunks):
        raw_text = str(chunk.get("text", "")).strip()
        if not raw_text:
            continue

        # 1. Manual chunk override
        if chunk.get("visualHelper"):
            vh = chunk["visualHelper"]
            plans[idx] = vh
            last_helper_idx = idx
            if vh.get("type"):
                last_type_idx[vh["type"]] = idx
            continue

        # 2. Manual index override in design
        if idx in explicit_helpers:
            vh = explicit_helpers[idx]
            plans[idx] = vh
            last_helper_idx = idx
            if isinstance(vh, dict) and vh.get("type"):
                last_type_idx[vh["type"]] = idx
            continue

        # Skip automated heuristic injection if auto helpers are disabled by governance
        if not auto_helpers_allowed:
            continue

        # Enforce minimum cooldown gap between automated visual helpers (≥ 2 chunks apart)
        if idx - last_helper_idx < 2:
            continue

        prev_text = str(chunks[idx - 1].get("text", "")).strip() if idx > 0 else ""
        next_text = str(chunks[idx + 1].get("text", "")).strip() if idx + 1 < len(chunks) else ""
        context_text = f"{prev_text} {raw_text} {next_text}".strip()

        # 3. Check for Time / Hourglass Widget (physical 3D asset)
        time_w = _extract_time_widget(raw_text) or _extract_time_widget(context_text)
        if time_w and idx - last_type_idx.get("time_widget", -999) >= 6:
            plans[idx] = time_w
            last_helper_idx = idx
            last_type_idx["time_widget"] = idx
            continue

        # 4. Check for Calendar Widget (physical UI component)
        cal = _extract_calendar_widget(raw_text) or _extract_calendar_widget(context_text)
        if cal and idx - last_type_idx.get("calendar_widget", -999) >= 6:
            plans[idx] = cal
            last_helper_idx = idx
            last_type_idx["calendar_widget"] = idx
            continue

        # 5. Check for Comparison (paradigm shift / split card)
        comp = _extract_comparison(raw_text) or _extract_comparison(context_text)
        if comp and idx - last_type_idx.get("before_after_comparison", -999) >= 6:
            plans[idx] = comp
            last_helper_idx = idx
            last_type_idx["before_after_comparison"] = idx
            continue

        # 6. Check for Optical Rack Focus (Cinematic Inflection / Focus on raw_text only)
        rack = _extract_optical_rack_focus(raw_text)
        if rack and idx - last_type_idx.get("optical_rack_focus", -999) >= 6:
            plans[idx] = rack
            last_helper_idx = idx
            last_type_idx["optical_rack_focus"] = idx
            continue

        # 6. Check for Metric / Motion Number
        metric = _extract_metric_number(raw_text)
        if metric and idx - last_type_idx.get("motion_number", -999) >= 6:
            plans[idx] = metric
            last_helper_idx = idx
            last_type_idx["motion_number"] = idx
            continue

        # 7. Check for Callout Badge
        callout = _extract_callout_badge(raw_text) or _extract_callout_badge(context_text)
        if callout and idx - last_type_idx.get("callout_badge", -999) >= 6:
            plans[idx] = callout
            last_helper_idx = idx
            last_type_idx["callout_badge"] = idx
            continue

        # 6. Check for Listicle bullet announcement
        if chunk.get("listicle") and chunk["listicle"].get("isListicle"):
            listicle_data = chunk["listicle"]
            if listicle_data.get("mode") == "teaser_blur":
                items = [
                    {
                        "id": f"item-{t.get('itemNumber', i+1)}",
                        "text": t.get("label", f"Step {i+1}"),
                        "label": t.get("indexFormatted", f"{i+1:02d}"),
                        "highlight": not t.get("blurred", False),
                    }
                    for i, t in enumerate(listicle_data.get("teaserItems", []))
                ]
                plans[idx] = {
                    "type": "listicle",
                    "title": listicle_data.get("badgeText") or "KEY POINTS",
                    "items": items,
                    "texture": "liquid_glass",
                    "position": "flank_right",
                }
                last_helper_idx = idx
                continue

    return plans
