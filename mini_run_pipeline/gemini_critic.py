"""Prometheus Vincere Backend — The GEMINI CRITIC.

Canonical import interface for the Gemini Critic in the Mineral Section.
"""

from mini_run_pipeline.mineral_vision_critic import (
    GeminiCritic,
    GeminiCriticEngine,
    MineralVisionCriticEngine,
    MineralCorrectionPatch,
    MineralFidelityReport,
    DeclaredMineralContract,
    DeclaredFontContract,
    ObservedMineralFrame,
    PASS_THRESHOLD,
    DEFAULT_ASPECT_RATIO,
    FAILURE_TAG_READABILITY_SACRIFICE,
    FAILURE_TAG_FONT_RUNTIME_FAILURE,
    FAILURE_TAG_CHEAP_TEMPLATE_MOTION,
    FAILURE_TAG_ASSET_TREATMENT_MISMATCH,
    FAILURE_TAG_SILENT_FALLBACK_SUCCESS,
)

__all__ = [
    "GeminiCritic",
    "GeminiCriticEngine",
    "MineralVisionCriticEngine",
    "MineralCorrectionPatch",
    "MineralFidelityReport",
    "DeclaredMineralContract",
    "DeclaredFontContract",
    "ObservedMineralFrame",
    "PASS_THRESHOLD",
    "DEFAULT_ASPECT_RATIO",
]
