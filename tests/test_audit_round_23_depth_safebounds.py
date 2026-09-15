import unittest
from mini_run_pipeline.typography import preflight_and_fit_layer_widths, generate_font_manifest, get_font_char_aspect


class TestAuditRound23DepthSafebounds(unittest.TestCase):
    def test_preflight_scales_positive_depthz_foreground_layers(self):
        """
        Layers with positive depthZPx (e.g. 140px foreground hero) are magnified
        by 1200 / (1200 - depthZ) = 1.132x in a 1200px perspective camera.
        Preflight must shrink the layer font size or apply autoFitScale so that
        the true on-screen projected width does not exceed max_safe_width.
        """
        # "sunday best." has 12 chars. In Montserrat (aspect 0.56), at 117px:
        # 2D unprojected width is 12 * 117 * 0.56 = 786.24px <= 790px.
        # But with depthZPx = 140, projected width is 786.24 * (1200/1060) = 890.1px!
        layers = [
            {
                "layerIndex": 0,
                "rawText": "sometimes in my",
                "text": "sometimes in my",
                "fontFamily": "Montserrat",
                "fontSizePx": 64.0,
                "isHero": False,
                "depthZPx": 0,
            },
            {
                "layerIndex": 1,
                "rawText": "sunday best.",
                "text": "sunday best.",
                "fontFamily": "Montserrat",
                "fontSizePx": 117,
                "isHero": True,
                "depthZPx": 140,
            },
        ]

        preflight_and_fit_layer_widths(layers, max_safe_width=790)

        hero = layers[1]
        # Font size must be shrunk from 117 down to 104 (hero floor) to fit within safe width
        self.assertLessEqual(hero["fontSizePx"], 104)
        # Estimated width must reflect the 3D projected width, bounded <= 792px
        self.assertLessEqual(hero["estimatedWidthPx"], 792)
        # Projected width scaled by autoFitScale must not exceed 790px
        projected_scaled_width = hero["estimatedWidthPx"] * hero.get("autoFitScale", 1.0)
        self.assertLessEqual(projected_scaled_width, 790.0)

    def test_authoritative_width_estimator_in_manifest_generation(self):
        """Verify that generate_font_manifest accurately stamps estimatedWidthPx and autoFitScale with depthZ."""
        chunk = {
            "chunkIndex": 1,
            "text": "sometimes in my Sunday best.",
            "startMs": 0,
            "endMs": 1800,
            "words": [
                {"text": "sometimes", "start_ms": 0, "end_ms": 300},
                {"text": "in", "start_ms": 300, "end_ms": 500},
                {"text": "my", "start_ms": 500, "end_ms": 700},
                {"text": "Sunday", "start_ms": 700, "end_ms": 1200},
                {"text": "best.", "start_ms": 1200, "end_ms": 1800},
            ],
        }
        manifest = generate_font_manifest([chunk], design_override={"motif": "pure_editorial_mono", "seed": 42})
        manifest_chunk = manifest["chunks"][0]
        for l in manifest_chunk.get("layers", []):
            est_w = l.get("estimatedWidthPx", 0)
            auto_fit = l.get("autoFitScale", 1.0)
            self.assertLessEqual(est_w * auto_fit, 792.0, f"Layer '{l.get('text')}' exceeds safe bounds")


if __name__ == "__main__":
    unittest.main()
