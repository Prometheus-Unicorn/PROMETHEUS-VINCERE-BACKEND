"""Unit tests for Laya System-1 Autonomous Decision Engine."""

import unittest
from mini_run_pipeline.laya_director import (
    LayaEditorialDirector,
    LayaBrollDecision,
    LayaCameraDecision,
    LayaMusicDecision,
    BROLL_TREATMENT_CRITERIA,
    ZOOM_ARCHETYPE_CRITERIA,
)


class TestLayaEditorialDirector(unittest.TestCase):
    """Test suite verifying Laya decision director behavior, schemas, and fallbacks."""

    def setUp(self):
        self.director = LayaEditorialDirector.get_instance()

    def test_singleton_instance(self):
        """Verify that get_instance returns a consistent singleton."""
        instance2 = LayaEditorialDirector.get_instance()
        self.assertIs(self.director, instance2)

    def test_broll_cutaway_decision_contract(self):
        """Verify that decide_broll_cutaway returns a valid LayaBrollDecision schema."""
        chunk_text = "We signed the contract on the desk and wired $50,000 immediately."
        candidates = [
            {"id": "asset_contract_signing", "description": "Hands signing business contract with fountain pen"},
            {"id": "asset_city_skyline", "description": "Time-lapse of bustling urban city skyline"},
        ]
        decision = self.director.decide_broll_cutaway(
            chunk_text,
            beat_type="evidence",
            candidate_assets=candidates,
            duration_sec=3.2,
        )

        self.assertIsInstance(decision, LayaBrollDecision)
        self.assertIsInstance(decision.should_cutaway, bool)
        self.assertGreaterEqual(decision.cutaway_probability, 0.0)
        self.assertLessEqual(decision.cutaway_probability, 1.0)
        self.assertIn(decision.treatment_style, BROLL_TREATMENT_CRITERIA.keys())
        self.assertIn(decision.provider, ("laya_local", "heuristic_fallback"))
        self.assertTrue(len(decision.rationale) > 0)

    def test_camera_movement_decision_contract(self):
        """Verify that decide_camera_movement returns a valid LayaCameraDecision schema."""
        chunk_text = "The entire server cluster collapsed in 12 seconds."
        decision = self.director.decide_camera_movement(
            chunk_text,
            is_hero=True,
            salience_delta=0.35,
        )

        self.assertIsInstance(decision, LayaCameraDecision)
        self.assertIsInstance(decision.should_zoom, bool)
        self.assertGreaterEqual(decision.zoom_probability, 0.0)
        self.assertLessEqual(decision.zoom_probability, 1.0)
        self.assertIn(decision.zoom_kind, ZOOM_ARCHETYPE_CRITERIA.keys())
        self.assertIn(decision.provider, ("laya_local", "heuristic_fallback"))

    def test_music_curation_decision_contract(self):
        """Verify that decide_music_curation returns a valid LayaMusicDecision schema."""
        monologue = "A high-stakes founder breakdown explaining how they survived an existential funding crisis."
        candidates = [
            {"id": "track_intense_trailer", "title": "Intense Trailer", "category": "trailer", "genreTags": ["epic", "intense"]},
            {"id": "track_lofi_chill", "title": "The Way", "category": "lofi", "genreTags": ["chill", "calm"]},
        ]
        decision = self.director.decide_music_curation(
            monologue,
            candidate_tracks=candidates,
        )

        self.assertIsInstance(decision, LayaMusicDecision)
        self.assertIn(decision.energy_intensity, ("soft", "medium", "hard"))
        self.assertIn(decision.provider, ("laya_local", "heuristic_fallback"))
        if candidates:
            self.assertIn(decision.recommended_track_id, ["track_intense_trailer", "track_lofi_chill"])


if __name__ == "__main__":
    unittest.main()
