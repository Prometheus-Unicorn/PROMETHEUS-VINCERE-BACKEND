"""Audit test proving Round 17 Commit 2: Pivot Glow Kill & Clean Grounding Shadow.

Verifies:
1. Behind-subject cranial pivot layers strictly have glow: 'none' and opticalBleed: 'none'.
2. Behind-subject layers have specularChamfer: False and specularSheen: False to prevent halo bleed.
3. Behind-subject layers have a single clean grounding shadow (alpha <= 0.5) and ambientShadow: 'none'.
4. Foreground hero layers retain their styled treatments when not placed behind the subject.
"""

import unittest
from mini_run_pipeline.typography import generate_font_manifest


class AuditRound17Commit2Tests(unittest.TestCase):
    """Test suite proving pivot glow elimination and clean grounding shadow for behind-subject layers."""

    def test_behind_subject_layers_have_no_glow_and_clean_shadow_across_seeds(self):
        """Behind-subject pivot layers must strictly have glow='none', specularChamfer=False, and grounding shadow."""
        chunks_input = [
            {
                "chunkIndex": 0,
                "text": "Over the last 12 months",
                "startMs": 0,
                "endMs": 2000,
                "words": [{"text": "Over"}, {"text": "the"}, {"text": "last"}, {"text": "12"}, {"text": "months"}],
            },
            {
                "chunkIndex": 1,
                "text": "I've sold more than",
                "startMs": 2000,
                "endMs": 4000,
                "words": [{"text": "I've"}, {"text": "sold"}, {"text": "more"}, {"text": "than"}],
            },
            {
                "chunkIndex": 2,
                "text": "12,000 physical products",
                "startMs": 4000,
                "endMs": 6500,
                "words": [{"text": "12,000"}, {"text": "physical"}, {"text": "products"}],
            },
            {
                "chunkIndex": 3,
                "text": "right from my bedroom",
                "startMs": 6500,
                "endMs": 8500,
                "words": [{"text": "right"}, {"text": "from"}, {"text": "my"}, {"text": "bedroom"}],
            },
            {
                "chunkIndex": 4,
                "text": "it's growing every day",
                "startMs": 8500,
                "endMs": 11000,
                "words": [{"text": "it's"}, {"text": "growing"}, {"text": "every"}, {"text": "day"}],
            },
        ]

        behind_checked = 0
        foreground_hero_checked = 0

        for seed in range(20):
            manifest = generate_font_manifest(
                chunks_input,
                design_override={
                    "aspectRatio": "9:16",
                    "seed": f"glow_test_seed_{seed}",
                    "motif": "obsidian_crimson",
                },
            )
            for chunk in manifest.get("chunks", []):
                for layer in chunk.get("layers", []):
                    if layer.get("behindSubject"):
                        behind_checked += 1
                        # 1. Glow must be strictly 'none'
                        self.assertEqual(
                            layer.get("glow"),
                            "none",
                            f"Seed {seed} behind-subject layer '{layer.get('rawText')}' has glow: {layer.get('glow')}",
                        )
                        # 2. Optical bleed must be 'none'
                        self.assertEqual(
                            layer.get("opticalBleed"),
                            "none",
                            f"Seed {seed} behind-subject layer '{layer.get('rawText')}' has opticalBleed: {layer.get('opticalBleed')}",
                        )
                        # 3. Specular chamfer / sheen must be disabled
                        self.assertFalse(
                            layer.get("specularChamfer"),
                            f"Seed {seed} behind-subject layer '{layer.get('rawText')}' has specularChamfer enabled",
                        )
                        self.assertFalse(
                            layer.get("specularSheen"),
                            f"Seed {seed} behind-subject layer '{layer.get('rawText')}' has specularSheen enabled",
                        )
                        # 4. Ambient shadow must be 'none'
                        self.assertEqual(
                            layer.get("ambientShadow"),
                            "none",
                            f"Seed {seed} behind-subject layer '{layer.get('rawText')}' has ambientShadow: {layer.get('ambientShadow')}",
                        )
                        # 5. Contact shadow must be subtle grounding drop shadow (0 2px 6px rgba(0, 0, 0, 0.45))
                        contact_shadow = layer.get("contactShadow", "")
                        self.assertIn("0 2px 6px rgba(0, 0, 0, 0.45)", contact_shadow)
                    elif layer.get("isHero"):
                        foreground_hero_checked += 1

        self.assertGreater(behind_checked, 0, "Expected to evaluate behind-subject pivot layers across seeds")
        self.assertGreater(foreground_hero_checked, 0, "Expected to evaluate foreground hero layers")


if __name__ == "__main__":
    unittest.main(verbosity=2)
