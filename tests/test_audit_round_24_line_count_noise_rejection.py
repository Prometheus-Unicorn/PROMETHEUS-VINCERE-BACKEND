import unittest
import numpy as np
from mini_run_pipeline.policy_check import measure_pixel_row_projection_lines


class TestAuditRound24LineCountNoiseRejection(unittest.TestCase):
    def test_rejects_sub_glyph_noise_and_preserves_real_text_bands(self):
        """
        A valid line of text on 1080x1920 canvas has substantial vertical glyph stroke (>=25px)
        and substantial stroke mass (max_row_px >= 65 and total_px >= 2500) across the row projection.
        Background highlights (skin tone warm highlights, jewelry reflections) that produce
        small or diffuse row projections (<65px peak, <2500 total area) must be rejected
        so they do not cause false wrap-induced row violations.
        """
        canvas = np.zeros((1920, 1080, 3), dtype=np.uint8)
        
        # Line 1: Strong text line "WELL." at y=1145..1235 (height 90px, width 300px, bright white)
        canvas[1145:1235, 390:690] = 255
        
        # Line 2: Strong text line "FOR ME IT WAS." at y=1265..1325 (height 60px, width 400px, bright white)
        canvas[1265:1325, 340:740] = 255
        
        # Noise band: Diffuse warm skin tone patch at y=1345..1389 (height 44px, width 50px peak)
        # R > 160, G > 120, B < 80 (typical skin tone matching warm_text)
        canvas[1345:1389, 530:575] = [200, 140, 70]
        
        placement = {
            "xPercent": "50%",
            "yPercent": "65%",
            "maxWidthPercent": "85%",
        }
        layers = [
            {"fontSizePx": 104, "rawText": "WELL."},
            {"fontSizePx": 64, "rawText": "FOR ME IT WAS."},
        ]
        
        res = measure_pixel_row_projection_lines(canvas, placement=placement, layers=layers)
        
        self.assertEqual(res["status"], "passed")
        self.assertTrue(res["detected"])
        # Must detect exactly the 2 true text lines, cleanly rejecting the noise band
        self.assertEqual(res["rowCount"], 2, f"Expected 2 rows, detected {res['rowCount']}: bands={res.get('bands')}")
        
        bands = res["bands"]
        self.assertEqual(len(bands), 2)
        # First band: around y=1145..1235
        self.assertAlmostEqual(bands[0]["y0"], 1145, delta=10)
        # Second band: around y=1265..1325
        self.assertAlmostEqual(bands[1]["y0"], 1265, delta=10)


if __name__ == "__main__":
    unittest.main()
