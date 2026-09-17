import unittest
from mini_run_pipeline.curito_animation_dna import (
    CuritoOutfitReference,
    CuritoPromptStitcher,
    CuritoSentimentBlendShape,
    CuritoWordSyncCalculator,
)
from mini_run_pipeline.curito_animation_orchestrator import (
    CuritoAnimationOrchestrator,
)
from mini_run_pipeline.google_flow_client import GoogleFlowMCPClient, CuritoAnimationReport


class CuritoCauseAndEffectTests(unittest.TestCase):
    def test_three_second_segment_extrapolates_for_two_seconds_to_produce_five_seconds(self):
        """Verify: 3s mapped speech window extrapolates by +2s hold to produce 5s generative duration."""
        # 3.0s speech window, target phrase climax at 2.5s
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:10.000",
            target_phrase="exponential cash flow",
            target_word_offset_sec=2.5,
            desired_duration_sec=3.0,
            extrapolate_hold_sec=2.0,
        )

        # Total duration must equal 5 seconds (not old 4s or 6s clamp)
        self.assertEqual(word_sync.total_duration_sec, 5)
        # Hold runway must be >= 2.0 seconds after the climax sync moment
        self.assertGreaterEqual(word_sync.hold_sec, 2.0)
        self.assertIn("holding firmly with continuous sub-pixel drift for", word_sync.timing_cue)

    def test_outfit_reference_is_stitched_into_subject_and_lighting(self):
        """Verify: Speaker's outfit from reference video is stitched into Part 1 and Part 4."""
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:05.000",
            target_phrase="asymmetric advantage",
            target_word_offset_sec=2.0,
            desired_duration_sec=3.0,
            extrapolate_hold_sec=2.0,
        )
        outfit = CuritoOutfitReference(
            description="charcoal fine-knit wool turtleneck",
            palette=["#1E1E1E", "#383838"],
            material_texture="matte woven texture",
            reference_frame_ms=5000,
            style_category="editorial_luxury",
        )

        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="Rotating monolithic chrome titanium vault",
            word_sync=word_sync,
            outfit_reference=outfit,
            aesthetic="curito_editorial_paper",
        )

        # Subject element must contain reference outfit
        self.assertIn("charcoal fine-knit wool turtleneck", stitched.subject_element)
        self.assertIn("matte woven texture", stitched.subject_element)

        # Lighting profile must echo wardrobe palette specular bounce
        self.assertIn("#1E1E1E", stitched.context_lighting)
        self.assertIsNotNone(stitched.outfit_reference)

    def test_sentiment_blendshape_interpolates_motion_direction_and_dynamics(self):
        """Verify: Expression & sentiment blend shape drives motion direction and velocity curve."""
        word_sync = CuritoWordSyncCalculator.compute_word_sync(
            interview_start_timestamp="00:15.000",
            target_phrase="breakthrough architecture",
            target_word_offset_sec=2.2,
            desired_duration_sec=3.0,
            extrapolate_hold_sec=2.0,
        )
        sentiment = CuritoSentimentBlendShape(
            primary_emotion="intellectual_urgency",
            intensity=0.92,
            blendshape_weights={"brow_furrow": 0.85, "eye_focus": 0.90},
            motion_direction="forward_push_incline",
            energy_velocity_curve="exponential_surge",
        )

        stitched = CuritoPromptStitcher.stitch_prompt(
            subject_metaphor="Kinetic golden ratio Fibonacci spiral",
            word_sync=word_sync,
            sentiment_blendshape=sentiment,
        )

        # Action movement must incorporate blendshape motion direction and dynamics
        self.assertIn("forward_push_incline", stitched.action_movement)
        self.assertIn("exponential_surge", stitched.action_movement)
        self.assertIn("intellectual_urgency", stitched.action_movement)
        self.assertIn("0.92", stitched.action_movement)
        self.assertIsNotNone(stitched.sentiment_blendshape)

    def test_end_to_end_orchestrator_directive_cause_and_effect_flow(self):
        """Verify: CuritoAnimationOrchestrator generates directive carrying extrapolated window, outfit, and sentiment."""
        class MockFlowClient:
            def generate_curito_animation(self, prompt, concept_title, clip_filename):
                return CuritoAnimationReport(
                    job_id="mock_job_1",
                    treatment_family="animations_curito",
                    concept_title=concept_title,
                    model="Veo 3.1 - Fast",
                    duration_sec=prompt.duration_sec,
                    aspect_ratio="9:16",
                    prompt=prompt,
                    word_sync=prompt.word_sync,
                    storyboard_beats=[],
                    mp4_asset_path=f"docs/mini_run_studio/flow_clips/{clip_filename}",
                    generated_at=1000.0,
                    status="SUCCESS",
                )

        orchestrator = CuritoAnimationOrchestrator(client=MockFlowClient())
        chunk = {
            "chunkIndex": 2,
            "text": "The fundamental law of leverage in software",
            "startMs": 4000,
            "endMs": 7000,  # 3.0s duration
        }

        directive = orchestrator.plan_and_generate_animation(
            chunk=chunk,
            chunk_index=2,
            target_phrase="law of leverage",
            sync_offset_sec=2.2,
            extrapolate_hold_sec=2.0,
        )

        # 3s chunk + 2s extrapolate = 5s total
        self.assertEqual(directive.duration_sec, 5)
        self.assertEqual(directive.duration_ms, 5000)
        self.assertEqual(directive.timeline_end_ms, 4000 + 5000)
        self.assertIsNotNone(directive.outfit_reference)
        self.assertIsNotNone(directive.sentiment_blendshape)
        self.assertEqual(directive.word_sync.total_duration_sec, 5)


if __name__ == "__main__":
    unittest.main()
