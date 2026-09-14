import unittest
from mini_run_pipeline.geometric_art import (
    plan_photo_treatment,
    plan_multi_image_strobe_transition,
    plan_geometric_contact_sheet,
    VALID_PHOTO_TREATMENTS,
    VALID_DITHER_PALETTES,
)

class TestGeometricPhotoTreatment(unittest.TestCase):
    def test_plan_geometric_drafting_treatment(self):
        """Tone with tech keywords defaults to geometric_drafting with architectural brackets."""
        plan = plan_photo_treatment("asset_101", tone="high-tech architecture", seed=77)
        self.assertEqual(plan["assetId"], "asset_101")
        self.assertEqual(plan["type"], "geometric_drafting")
        self.assertTrue(plan["drafting"]["showBrackets"])
        self.assertTrue(plan["drafting"]["showCoordinates"])
        self.assertTrue(plan["drafting"]["showCrosshairs"])
        self.assertEqual(plan["seed"], 77)

    def test_plan_dither_print_treatment(self):
        """Tone with editorial/print keywords defaults to dither_print with duotone palette."""
        plan = plan_photo_treatment(
            "asset_102",
            tone="editorial print",
            custom_options={"palette": "signal", "algorithm": "bayer4", "cellSize": 8}
        )
        self.assertEqual(plan["type"], "dither_print")
        self.assertEqual(plan["dither"]["palette"], "signal")
        self.assertEqual(plan["dither"]["algorithm"], "bayer4")
        self.assertEqual(plan["dither"]["cellSize"], 8)

    def test_plan_contour_atlas_treatment(self):
        """Topographic tone plans contour atlas with elevation levels and drift."""
        plan = plan_photo_treatment("asset_103", tone="topography elevation map")
        self.assertEqual(plan["type"], "contour_atlas")
        self.assertIn("levels", plan["contour"])
        self.assertIn("drift", plan["contour"])
        self.assertEqual(plan["contour"]["style"], "topographic")

    def test_plan_spectral_curtain_treatment(self):
        """Cyber/spectral tone plans vertical slit extrusion with chromatic separation."""
        plan = plan_photo_treatment("asset_104", tone="cyber spectral energy")
        self.assertEqual(plan["type"], "spectral_curtain")
        self.assertIn("curtainDensity", plan["curtain"])
        self.assertIn("chromaticShift", plan["curtain"])
        self.assertEqual(plan["curtain"]["direction"], "down")

    def test_plan_multi_image_strobe_transition(self):
        """Multi-image strobe transition plans frame duration, slice rate, and flash burns."""
        images = [
            "/img/cut_01.jpg",
            "/img/cut_02.jpg",
            "/img/cut_03.jpg",
            "/img/cut_04.jpg",
        ]
        plan = plan_multi_image_strobe_transition(
            images=images,
            duration_frames=12,
            strobe_interval=2,
            enable_lens_flash=True,
            enable_chromatic_aberration=True,
            enable_drafting_hud=True,
        )
        self.assertEqual(plan["type"], "multi_image_strobe")
        self.assertEqual(plan["imageCount"], 4)
        self.assertEqual(plan["durationInFrames"], 12)
        self.assertEqual(plan["strobeInterval"], 2)
        self.assertEqual(plan["slicesShown"], 6)
        self.assertTrue(plan["enableLensFlash"])
        self.assertTrue(plan["enableChromaticAberration"])
        self.assertTrue(plan["enableDraftingHUD"])

    def test_plan_geometric_contact_sheet(self):
        """Contact sheet plans editorial multi-pane layouts with coordinates."""
        images = ["/img/1.jpg", "/img/2.jpg", "/img/3.jpg"]
        plan = plan_geometric_contact_sheet(
            images=images,
            layout="asymmetric_hero",
            duration_frames=30,
        )
        self.assertEqual(plan["type"], "geometric_contact_sheet")
        self.assertEqual(plan["layout"], "asymmetric_hero")
        self.assertEqual(len(plan["coordinates"]), 3)
        self.assertTrue(plan["showDraftingMarks"])

if __name__ == "__main__":
    unittest.main()
