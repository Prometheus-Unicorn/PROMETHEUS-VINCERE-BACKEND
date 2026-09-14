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

    # 4. Large raw count
    m_count = re.search(r"\b(\d{1,3}(?:,\d{3})+|\d{3,9})\s+([a-zA-Z]+)\b", text)
    if m_count:
        num_str = m_count.group(1).replace(",", "")
        val = float(num_str)
        noun = m_count.group(2).upper()
        if val >= 50:
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

def detect_and_plan_visual_helpers(
    chunks: List[Dict[str, Any]],
    design: Optional[Dict[str, Any]] = None,
) -> Dict[int, Dict[str, Any]]:
    """Scan transcript chunks and generate structured visual helper overlays.
    
    Supports:
    - Manual overrides from design_input or chunk['visualHelper'].
    - Automatic semantic detection for comparison, metric/number, listicle, and callout badge.
    - Anti-fatigue cooldown so helpers don't overcrowd the screen (minimum 2 chunks gap).
    """
    design_dict = design if isinstance(design, dict) else {}
    explicit_helpers = design_dict.get("visualHelpers") or {}

    plans: Dict[int, Dict[str, Any]] = {}
    last_helper_idx = -999

    for idx, chunk in enumerate(chunks):
        raw_text = str(chunk.get("text", "")).strip()
        if not raw_text:
            continue

        # 1. Manual chunk override
        if chunk.get("visualHelper"):
            plans[idx] = chunk["visualHelper"]
            last_helper_idx = idx
            continue

        # 2. Manual index override in design
        if idx in explicit_helpers:
            plans[idx] = explicit_helpers[idx]
            last_helper_idx = idx
            continue

        # Enforce minimum cooldown gap between automated visual helpers (≥ 2 chunks apart)
        if idx - last_helper_idx < 2:
            continue

        # 3. Check for Comparison
        comp = _extract_comparison(raw_text)
        if comp:
            plans[idx] = comp
            last_helper_idx = idx
            continue

        # 4. Check for Metric / Motion Number
        metric = _extract_metric_number(raw_text)
        if metric:
            plans[idx] = metric
            last_helper_idx = idx
            continue

        # 5. Check for Callout Badge
        callout = _extract_callout_badge(raw_text)
        if callout:
            plans[idx] = callout
            last_helper_idx = idx
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
