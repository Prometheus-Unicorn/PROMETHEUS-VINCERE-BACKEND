import unittest
from mini_run_pipeline.visual_helpers import (
    detect_and_plan_visual_helpers,
    _extract_comparison,
    _extract_metric_number,
    _extract_callout_badge,
)
from mini_run_pipeline.typography import generate_font_manifest

class TestVisualHelpersEngine(unittest.TestCase):
    def test_before_after_comparison_extraction(self):
        """Phrases indicating comparison or transformation trigger before_after_comparison."""
        # Case A: Before and after
        text_a = "LOOK AT THE BEFORE AND AFTER TRANSFORMATION"
        res_a = _extract_comparison(text_a)
        self.assertIsNotNone(res_a)
        self.assertEqual(res_a["type"], "before_after_comparison")
        self.assertEqual(res_a["title"], "TRANSFORMATION")

        # Case B: VS / Versus
        text_b = "Manual Outreach vs Automated Inbound"
        res_b = _extract_comparison(text_b)
        self.assertIsNotNone(res_b)
        self.assertEqual(res_b["type"], "before_after_comparison")
        self.assertEqual(res_b["beforeLabel"], "Manual Outreach")
        self.assertEqual(res_b["afterLabel"], "Automated Inbound")

        # Case C: Instead of
        text_c = "Instead of guessing keywords, use high-intent buyer search terms"
        res_c = _extract_comparison(text_c)
        self.assertIsNotNone(res_c)
        self.assertEqual(res_c["type"], "before_after_comparison")
        self.assertEqual(res_c["title"], "THE PARADIGM SHIFT")

    def test_motion_number_metric_extraction(self):
        """Numbers with currency, percentages, multipliers, or metric nouns trigger motion_number."""
        # Case A: Currency
        text_curr = "WE GENERATED OVER $50,000 IN 48 HOURS"
        res_curr = _extract_metric_number(text_curr)
        self.assertIsNotNone(res_curr)
        self.assertEqual(res_curr["type"], "motion_number")
        self.assertEqual(res_curr["value"], 50000.0)
        self.assertEqual(res_curr["prefix"], "$")
        self.assertEqual(res_curr["format"], "currency")

        # Case B: Percentage
        text_pct = "THAT PRODUCED A 300% INCREASE IN REVENUE"
        res_pct = _extract_metric_number(text_pct)
        self.assertIsNotNone(res_pct)
        self.assertEqual(res_pct["type"], "motion_number")
        self.assertEqual(res_pct["value"], 300.0)
        self.assertEqual(res_pct["suffix"], "%")
        self.assertEqual(res_pct["format"], "percent")

        # Case C: Multiplier
        text_mult = "OUR CONVERSION JUMPED 10X ALMOST IMMEDIATELY"
        res_mult = _extract_metric_number(text_mult)
        self.assertIsNotNone(res_mult)
        self.assertEqual(res_mult["type"], "motion_number")
        self.assertEqual(res_mult["value"], 10.0)
        self.assertEqual(res_mult["suffix"], "X")

        # Case D: Large count
        text_count = "WE SCALED TO 15,000 USERS GLOBALLY"
        res_count = _extract_metric_number(text_count)
        self.assertIsNotNone(res_count)
        self.assertEqual(res_count["type"], "motion_number")
        self.assertEqual(res_count["value"], 15000.0)
        self.assertIn("USERS", res_count["suffix"])

    def test_callout_badge_extraction(self):
        """High-impact advice triggers callout_badge with appropriate icons."""
        # Case A: Pro tip
        text_tip = "HERE IS A PRO TIP YOU SHOULD ALWAYS REMEMBER"
        res_tip = _extract_callout_badge(text_tip)
        self.assertIsNotNone(res_tip)
        self.assertEqual(res_tip["type"], "callout_badge")
        self.assertEqual(res_tip["title"], "PRO TIP")
        self.assertEqual(res_tip["icon"], "zap")

        # Case B: Golden rule
        text_rule = "THE GOLDEN RULE OF RETENTION IS CONSISTENCY"
        res_rule = _extract_callout_badge(text_rule)
        self.assertIsNotNone(res_rule)
        self.assertEqual(res_rule["type"], "callout_badge")
        self.assertEqual(res_rule["title"], "GOLDEN RULE")
        self.assertEqual(res_rule["icon"], "star")

        # Case C: Key takeaway
        text_key = "THE KEY TAKEAWAY IS VELOCITY BEATS PERFECTION"
        res_key = _extract_callout_badge(text_key)
        self.assertIsNotNone(res_key)
        self.assertEqual(res_key["type"], "callout_badge")
        self.assertEqual(res_key["title"], "KEY TAKEAWAY")
        self.assertEqual(res_key["icon"], "target")

    def test_detect_and_plan_visual_helpers_flow_and_cooldown(self):
        """detect_and_plan_visual_helpers plans helpers and enforces anti-fatigue cooldown."""
        chunks = [
            {"chunkIndex": 0, "text": "HERE IS A PRO TIP YOU MUST HEAR"},
            {"chunkIndex": 1, "text": "WE HIT $100,000 IN MONTHLY SALES"},  # adjacent -> suppressed by cooldown
            {"chunkIndex": 2, "text": "ORDINARY TALKING POINT HERE"},
            {"chunkIndex": 3, "text": "WE HIT $100,000 IN MONTHLY SALES"},  # gap >= 2 -> admitted
        ]

        plans = detect_and_plan_visual_helpers(chunks)
        self.assertIn(0, plans)
        self.assertEqual(plans[0]["type"], "callout_badge")
        self.assertNotIn(1, plans)  # cooldown suppression
        self.assertIn(3, plans)
        self.assertEqual(plans[3]["type"], "motion_number")

    def test_manual_override_support(self):
        """Manual visualHelper specifications take top priority."""
        custom_helper = {
            "type": "before_after_comparison",
            "title": "CUSTOM TEST",
            "beforeLabel": "A",
            "afterLabel": "B",
        }
        chunks = [
            {"chunkIndex": 0, "text": "NORMAL TEXT", "visualHelper": custom_helper},
        ]
        plans = detect_and_plan_visual_helpers(chunks)
        self.assertIn(0, plans)
        self.assertEqual(plans[0]["title"], "CUSTOM TEST")

    def test_typography_manifest_visual_helper_integration(self):
        """generate_font_manifest stamps visualHelper onto manifest chunks."""
        chunks = [
            {
                "chunkIndex": 0,
                "text": "HERE IS A PRO TIP FOR SCALING",
                "startMs": 0,
                "endMs": 1500,
                "words": [
                    {"word": "HERE", "startMs": 0, "endMs": 300},
                    {"word": "IS", "startMs": 310, "endMs": 500},
                    {"word": "A", "startMs": 510, "endMs": 700},
                    {"word": "PRO", "startMs": 710, "endMs": 1000},
                    {"word": "TIP", "startMs": 1010, "endMs": 1300},
                    {"word": "FOR", "startMs": 1310, "endMs": 1400},
                    {"word": "SCALING", "startMs": 1410, "endMs": 1500},
                ],
            }
        ]

        manifest = generate_font_manifest(chunks)
        m_chunks = manifest["chunks"]
        self.assertEqual(len(m_chunks), 1)
        self.assertIn("visualHelper", m_chunks[0])
        self.assertIsNotNone(m_chunks[0]["visualHelper"])
        self.assertEqual(m_chunks[0]["visualHelper"]["type"], "callout_badge")
        self.assertEqual(m_chunks[0]["visualHelper"]["title"], "PRO TIP")

if __name__ == "__main__":
    unittest.main()
