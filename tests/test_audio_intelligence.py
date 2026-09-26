import unittest
from mini_run_pipeline.song_program import load_song_catalog, plan_song_program
from mini_run_pipeline.orchestration import plan_mini_run_orchestration


class AudioIntelligenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_song_catalog()
        cls.sample_chunks = [
            {
                "chunkIndex": 0,
                "startMs": 0,
                "endMs": 3200,
                "outputStartMs": 0,
                "outputEndMs": 3200,
                "text": "The greatest mistake entrepreneurs make",
                "words": [
                    {"word": "The", "start_ms": 100, "end_ms": 300},
                    {"word": "greatest", "start_ms": 320, "end_ms": 800},
                    {"word": "mistake", "start_ms": 850, "end_ms": 1400},
                    {"word": "entrepreneurs", "start_ms": 1450, "end_ms": 2300},
                    {"word": "make", "start_ms": 2350, "end_ms": 2900},
                ],
                "fontFamily": "Apple Garamond",
                "treatmentSystem": "hierarchical_asymmetric_lockup",
                "layers": [
                    {"role": "primary_focus_word", "text": "mistake", "fontFamily": "Apple Garamond", "isHero": True}
                ],
            },
            {
                "chunkIndex": 1,
                "startMs": 3200,
                "endMs": 6800,
                "outputStartMs": 3200,
                "outputEndMs": 6800,
                "text": "is focusing entirely on vanity metrics",
                "words": [
                    {"word": "is", "start_ms": 3300, "end_ms": 3500},
                    {"word": "focusing", "start_ms": 3550, "end_ms": 4100},
                    {"word": "entirely", "start_ms": 4150, "end_ms": 4800},
                    {"word": "on", "start_ms": 4850, "end_ms": 5100},
                    {"word": "vanity", "start_ms": 5150, "end_ms": 5800},
                    {"word": "metrics", "start_ms": 5850, "end_ms": 6500},
                ],
                "fontFamily": "Apple Garamond",
                "treatmentSystem": "hierarchical_asymmetric_lockup",
                "layers": [
                    {"role": "primary_focus_word", "text": "vanity", "fontFamily": "Apple Garamond", "isHero": True}
                ],
            },
            {
                "chunkIndex": 2,
                "startMs": 6800,
                "endMs": 10500,
                "outputStartMs": 6800,
                "outputEndMs": 10500,
                "text": "RETENTION",
                "words": [{"word": "RETENTION", "start_ms": 6900, "end_ms": 7800}],
                "fontFamily": "Anton",
                "treatmentSystem": "single_word_punch",
                "layers": [{"role": "punch", "text": "RETENTION", "fontFamily": "Anton"}],
            },
            {
                "chunkIndex": 3,
                "startMs": 10500,
                "endMs": 15000,
                "outputStartMs": 10500,
                "outputEndMs": 15000,
                "text": "terminal.execute(audit)",
                "words": [
                    {"word": "terminal", "start_ms": 10600, "end_ms": 11200},
                    {"word": "execute", "start_ms": 11250, "end_ms": 12000},
                    {"word": "audit", "start_ms": 12050, "end_ms": 13000},
                ],
                "fontFamily": "JetBrains Mono",
                "treatmentSystem": "hierarchical_asymmetric_lockup",
                "layers": [{"role": "code", "text": "audit", "fontFamily": "JetBrains Mono"}],
            },
        ]

    def test_softmax_temperature_sampling_guarantees_entropy_across_seeds(self):
        """Verify that across 10 random seeds, song program does not lock to a single hardcoded track."""
        chosen_titles = []
        for seed in range(10):
            design = {"seed": seed}
            program = plan_song_program(
                catalog=self.catalog,
                chunks=self.sample_chunks,
                duration_ms=15000,
                design=design,
            )
            events = program.get("events", [])
            self.assertTrue(events, f"Seed {seed} failed to produce song events")
            chosen_titles.append(events[0]["title"])

        unique_titles = set(chosen_titles)
        # Must select at least 2 distinct high-affinity tracks across 10 seeds (anti-monotony guarantee)
        self.assertGreaterEqual(
            len(unique_titles),
            2,
            f"Expected multiple distinct tracks across seeds, but got: {chosen_titles}",
        )

    def test_text_sfx_synchronizes_with_visual_peak_offset(self):
        """Verify that text SFX trigger is offset to Remotion visual peak, not raw speech onset."""
        orch = plan_mini_run_orchestration(
            chunks=self.sample_chunks,
            probe={"width": 1080, "height": 1920},
            duration_ms=15000,
        )
        sfx_events = orch.get("sfx", [])
        self.assertTrue(sfx_events, "Expected SFX events to be scheduled")

        # Check lockup and single word text events
        text_sfx = [
            e for e in sfx_events
            if e.get("causedByTreatment") in ("hierarchical_asymmetric_lockup", "opening_hook")
            or e.get("visualPeakOffsetMs") is not None
        ]
        self.assertTrue(text_sfx, "Expected text SFX events")

        for event in text_sfx:
            chunk_id = event.get("causedByChunkId")
            if chunk_id is not None and chunk_id != "0":
                chunk = next((c for c in self.sample_chunks if str(c["chunkIndex"]) == chunk_id), None)
                if chunk:
                    # Trigger time must include visual peak offset (at least +100ms after chunk start)
                    self.assertGreaterEqual(
                        event["triggerMs"],
                        chunk["startMs"] + 100,
                        f"SFX {event['id']} triggered at {event['triggerMs']}ms, before visual peak of chunk starting at {chunk['startMs']}ms",
                    )

    def test_context_aware_acoustic_palettes_for_typography(self):
        """Verify that serif lockups receive velvet acoustic cues and NEVER typewriter clicks."""
        orch = plan_mini_run_orchestration(
            chunks=self.sample_chunks,
            probe={"width": 1080, "height": 1920},
            duration_ms=15000,
        )
        sfx_events = orch.get("sfx", [])

        # Find SFX for chunk 1 (Apple Garamond serif lockup)
        garamond_sfx = [e for e in sfx_events if e.get("causedByChunkId") == "1"]
        for event in garamond_sfx:
            self.assertNotEqual(
                event["cue"],
                "mechanical_click",
                "Serif typography must never be paired with mechanical typewriter click",
            )
            self.assertIn(
                event["cue"],
                ["slow_whoosh_reverb", "whoosh_slow", "sub_impact_reverb", "shutter_snap"],
                f"Unexpected acoustic cue {event['cue']} for serif typography",
            )

        # Find SFX for chunk 3 (JetBrains Mono tech lockup)
        tech_sfx = [e for e in sfx_events if e.get("causedByChunkId") == "3"]
        for event in tech_sfx:
            self.assertIn(
                event["cue"],
                ["glitch_digital", "click_bupu", "shutter_snap", "shutter_clicks_v2_bupu", "mechanical_click"],
                f"Unexpected acoustic cue {event['cue']} for tech typography",
            )


if __name__ == "__main__":
    unittest.main()
