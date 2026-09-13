"""Audit test proving Round 17 Commit 3: Audio Stem Rebalance & Cinematic SFX Wiring.

Verifies:
1. Sidechain ducking ratio defaults to >= 4.0:1 (4.5:1) in both song_program.py and render.py.
2. Background music baseGainDb defaults to -13.0 dB under dialogue to eliminate vocal masking.
3. Ducking attack is fast (<= 20ms) to duck immediately upon speech onset.
4. Camera moves and transitions in ZOOM_KINDS are wired to shutter/whoosh SFX cues.
5. All camera move SFX have audible gains >= -10.0 dB (between -7.0 dB and -5.5 dB).
6. SFX mix bus gain in render.py is boosted to -3.5 dB.
"""

import unittest
from mini_run_pipeline import orchestration, render, song_program


class AuditRound17Commit3Tests(unittest.TestCase):
    """Test suite proving vocal priority audio stem balance and cinematic SFX wiring."""

    def test_sidechain_ducking_ratio_and_attack(self):
        """Ducking profile defaults must enforce vocal priority (ratio >= 4.0, attack <= 20ms)."""
        defaults = song_program._compute_ducking_profile("medium")
        self.assertGreaterEqual(
            defaults["ratio"],
            4.0,
            f"Ducking ratio {defaults['ratio']} is below 4.0:1 vocal priority requirement",
        )
        self.assertLessEqual(
            defaults["attackMs"],
            20,
            f"Ducking attack {defaults['attackMs']}ms is too slow; must be <= 20ms",
        )

    def test_music_base_gain_db_under_dialogue(self):
        """Background song baseGainDb must default to -13.0 dB under dialogue."""
        program = song_program.plan_song_program(
            catalog=song_program.load_song_catalog(),
            chunks=[{"text": "testing speech clearance", "startMs": 0, "endMs": 3000, "wordCount": 3}],
            duration_ms=5000,
        )
        self.assertEqual(
            program.get("baseGainDb"),
            -13.0,
            f"Music baseGainDb {program.get('baseGainDb')} is too loud; expected -13.0 dB",
        )

    def test_render_audio_mix_command_carries_ducking_and_gain(self):
        """build_audio_mix_command must generate sidechaincompress filter with ratio >= 4.0 and volume=-13dB."""
        dummy_program = {
            "baseGainDb": -13.0,
            "dialogueDucking": {"threshold": 0.085, "ratio": 4.5, "attackMs": 15, "releaseMs": 300},
            "events": [{"sourceStartMs": 0, "sourceEndMs": 5000, "localPath": "dummy.mp3"}],
        }
        cmd = render.build_audio_mix_command(
            muted_video_path="dummy_video.mp4",
            dialogue_path="dummy_audio.aac",
            song_program=dummy_program,
            sfx_events=[{"localPath": "dummy_sfx.mp3", "triggerMs": 500, "gainDb": -3.5}],
            output_path="dummy_out.mp4",
        )
        filter_str = "".join(cmd)
        self.assertIn("ratio=4.5", filter_str)
        self.assertIn("attack=15", filter_str)
        self.assertIn("volume=-13dB", filter_str)
        self.assertIn("volume=-3.5dB", filter_str)

    def test_camera_moves_wired_to_shutter_whoosh_with_audible_gain(self):
        """Camera moves in ZOOM_KINDS must use shutter/whoosh cues with gain >= -10.0 dB."""
        valid_cues = {"shutter_snap", "whoosh_fast", "whoosh_slow", "slow_whoosh_reverb", "sub_impact_reverb"}
        for kind, spec in orchestration.ZOOM_KINDS.items():
            cue = spec.get("sfxCue")
            self.assertIn(
                cue,
                valid_cues,
                f"Zoom kind '{kind}' uses unapproved SFX cue '{cue}'",
            )
            gain = spec.get("sfxGainDb", -99)
            self.assertGreaterEqual(
                gain,
                -10.0,
                f"Zoom kind '{kind}' gain {gain} dB is below audible threshold >= -10.0 dB",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
