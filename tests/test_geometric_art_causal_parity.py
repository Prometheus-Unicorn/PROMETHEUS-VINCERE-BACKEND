import unittest
from mini_run_pipeline.typography import generate_font_manifest
from mini_run_pipeline.geometric_art import (
    plan_photo_treatment,
    plan_multi_image_strobe_transition,
    plan_geometric_contact_sheet,
)

class TestGeometricArtCausalParity(unittest.TestCase):
    def test_causal_manifest_integration(self):
        """Verifies geometricArtCatalog, photoTreatment, strobeTransition, and contactSheet in manifest."""
        sample_chunks = [
            {
                "chunkIndex": 0,
                "text": "ARCHITECTURAL BLUEPRINT AND SYSTEM DRAFTING",
                "startMs": 0,
                "endMs": 2500,
                "words": [{"text": w, "start_ms": i * 300, "end_ms": (i + 1) * 300} for i, w in enumerate("ARCHITECTURAL BLUEPRINT AND SYSTEM DRAFTING".split())],
                "photoTreatment": plan_photo_treatment("blueprint_01", tone="technical precision"),
            },
            {
                "chunkIndex": 1,
                "text": "RAPID FIRE SHUTTER FLASH TRANSITION",
                "startMs": 2500,
                "endMs": 4500,
                "words": [{"text": w, "start_ms": 2500 + i * 300, "end_ms": 2500 + (i + 1) * 300} for i, w in enumerate("RAPID FIRE SHUTTER FLASH TRANSITION".split())],
                "strobeTransition": plan_multi_image_strobe_transition(
                    images=["/img1.jpg", "/img2.jpg", "/img3.jpg"],
                    duration_frames=10,
                    strobe_interval=1,
                ),
            },
            {
                "chunkIndex": 2,
                "text": "EDITORIAL CONTACT SHEET MULTI PANE",
                "startMs": 4500,
                "endMs": 7500,
                "words": [{"text": w, "start_ms": 4500 + i * 300, "end_ms": 4500 + (i + 1) * 300} for i, w in enumerate("EDITORIAL CONTACT SHEET MULTI PANE".split())],
                "contactSheet": plan_geometric_contact_sheet(
                    images=["/c1.jpg", "/c2.jpg", "/c3.jpg"],
                    layout="asymmetric_hero",
                ),
            },
        ]

        manifest = generate_font_manifest(sample_chunks)
        
        # 1. Check top-level catalog presence
        self.assertIn("geometricArtCatalog", manifest)
        cat = manifest["geometricArtCatalog"]
        self.assertIn("treatments", cat)
        self.assertEqual(cat["activePhotoTreatments"], 1)
        self.assertEqual(cat["activeStrobeTransitions"], 1)

        # 2. Check chunk-level preservation and parity
        chunks = manifest["chunks"]
        self.assertEqual(len(chunks), 3)

        # Chunk 0: photoTreatment
        self.assertIn("photoTreatment", chunks[0])
        self.assertEqual(chunks[0]["photoTreatment"]["type"], "geometric_drafting")
        self.assertTrue(chunks[0]["photoTreatment"]["drafting"]["showBrackets"])

        # Chunk 1: strobeTransition
        self.assertIn("strobeTransition", chunks[1])
        self.assertEqual(chunks[1]["strobeTransition"]["type"], "multi_image_strobe")
        self.assertEqual(chunks[1]["strobeTransition"]["durationInFrames"], 10)
        self.assertEqual(chunks[1]["strobeTransition"]["slicesShown"], 10)

        # Chunk 2: contactSheet
        self.assertIn("contactSheet", chunks[2])
        self.assertEqual(chunks[2]["contactSheet"]["type"], "geometric_contact_sheet")
        self.assertEqual(chunks[2]["contactSheet"]["layout"], "asymmetric_hero")

if __name__ == "__main__":
    unittest.main()
