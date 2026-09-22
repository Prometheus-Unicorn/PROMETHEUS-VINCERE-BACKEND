"""Deterministic verification tests for critique fixes:
1. Curated mechanical sound effects & elevated broadcast gains
2. Behind-subject cranial occlusion prevention & middle-third companion positioning
3. De-spamming origin_shiny_pill
4. Song selection diversity & cross-genre synergy
"""

import unittest
from mini_run_pipeline.orchestration import plan_mini_run_orchestration
from mini_run_pipeline.subject_placement import plan_subject_safe_placements
from mini_run_pipeline.typography import ANIMA_RUNTIME_TREATMENTS
from mini_run_pipeline.song_program import plan_song_program, BUILTIN_SANCTIONED_TRACKS


class TestCritiqueFixes(unittest.TestCase):
    def test_sfx_mechanical_pool_and_broadcast_gains(self) -> None:
        """SFX events use tactile mechanical sounds and broadcast-audible gains (-4.5 to -9.0 dB)."""
        chunks = [
            {
                "chunkIndex": 0,
                "text": "Opening hook line",
                "startMs": 0,
                "endMs": 1500,
                "words": [{"text": "Opening", "start_ms": 0, "end_ms": 700}, {"text": "hook", "start_ms": 720, "end_ms": 1500}],
                "fxPreset": "origin_outline_flicker_fill",
            },
            {
                "chunkIndex": 1,
                "text": "Second sentence here",
                "startMs": 2000,
                "endMs": 3500,
                "words": [{"text": "Second", "start_ms": 2000, "end_ms": 2700}, {"text": "sentence", "start_ms": 2720, "end_ms": 3500}],
                "visualHelper": {"type": "callout_badge"},
            },
        ]
        manifest = plan_mini_run_orchestration(
            chunks=chunks,
            probe={"width": 1080, "height": 1920},
            duration_ms=4000,
        )
        sfx_events = manifest.get("sfx", [])
        self.assertGreaterEqual(len(sfx_events), 2)

        valid_cues = {
            "mechanical_click", "camera_shutter_bupu", "shutter_snap",
            "shutter_clicks_v2_bupu", "click_bupu", "mechanical_click_bupu",
            "impact_deep", "glitch_digital", "whoosh_fast", "slow_whoosh_reverb",
        }
        for s in sfx_events:
            self.assertIn(s.get("cue"), valid_cues)
            self.assertGreaterEqual(s.get("gainDb"), -10.0)
            self.assertLessEqual(s.get("gainDb"), -4.0)

    def test_behind_subject_cranial_occlusion_and_companion_placement(self) -> None:
        """Behind-subject text in tight headroom stays above hair (y<=10%) and companion sits in middle third (55-59%)."""
        observation = {
            "frames": [
                {"sourceMs": 6000, "faceBox": {"x": 0.35, "y": 0.207, "width": 0.30, "height": 0.337}},
            ]
        }
        chunk = {
            "chunkIndex": 4,
            "startMs": 5500,
            "endMs": 7000,
            "text": "See, this video",
            "subjectLayering": {"behindSubject": True},
            "layers": [
                {"role": "companion", "text": "See, This", "behindSubject": False},
                {"role": "hero", "text": "VIDEO", "fontSizePx": 210.0, "behindSubject": True},
            ],
        }
        placements = plan_subject_safe_placements([chunk], observation)
        self.assertEqual(len(placements), 1)
        p = placements[0]

        # Cranial crown text must be elevated to <= 10.0% Y and maxWidthPercent >= 80%
        self.assertEqual(p["dominantZone"], "cranial_crown")
        y_pct = float(p["yPercent"].replace("%", ""))
        self.assertLessEqual(y_pct, 10.0)
        self.assertEqual(p["maxWidthPercent"], "85%")

        # Hero layer font size must be clamped to prevent skull/hair swallowing
        hero_layer = [l for l in chunk["layers"] if l.get("behindSubject")][0]
        self.assertLessEqual(hero_layer.get("fontSizePx"), 135.0)

        # Companion placement must sit in the natural middle third (55% - 59%)
        comp = p.get("companionPlacement", {})
        comp_y = float(comp.get("yPercent", "0%").replace("%", ""))
        self.assertGreaterEqual(comp_y, 55.0)
        self.assertLessEqual(comp_y, 59.0)

    def test_origin_shiny_pill_deprecate_from_candidates(self) -> None:
        """origin_shiny_pill is excluded from active candidate treatments."""
        candidate_ids = {item["id"] for item in ANIMA_RUNTIME_TREATMENTS}
        self.assertNotIn("origin_shiny_pill", candidate_ids)
        self.assertIn("origin_kinetic_editorial_v2", candidate_ids)

    def test_song_selection_dynamism_and_cross_genre_synergy(self) -> None:
        """Educational videos select varied, speech-friendly tracks across seeds without deterministic EARFQUAKE lock."""
        chunks = [
            {"startMs": 0, "endMs": 5000, "text": "Welcome to the tutorial on how this works"},
            {"startMs": 5000, "endMs": 10000, "text": "Here is the step by step process to learn"},
            {"startMs": 10000, "endMs": 15000, "text": "Now you understand how everything connects together"},
        ]
        selected_titles = set()
        for seed in [111, 222, 333, 444, 555]:
            prog = plan_song_program(
                catalog=BUILTIN_SANCTIONED_TRACKS,
                chunks=chunks,
                duration_ms=15000,
                design={"seed": seed},
            )
            ev = prog["events"][0]
            selected_titles.add(ev["title"])

        # Multiple unique songs must be chosen across different seeds
        self.assertGreaterEqual(len(selected_titles), 2)


if __name__ == "__main__":
    unittest.main()
