import unittest
from mini_run_pipeline.visual_helpers import (
    detect_and_plan_visual_helpers,
    _extract_comparison,
    _extract_metric_number,
    _extract_callout_badge,
    _extract_calendar_widget,
    _extract_time_widget,
    _extract_optical_rack_focus,
)
from mini_run_pipeline.typography import generate_font_manifest

class TestVisualHelpersEngine(unittest.TestCase):
    def test_calendar_widget_extraction(self):
        """Phrases referencing calendars, scheduling, or planners trigger calendar_widget with dynamic date."""
        text_cal = "information of how to manage your calendars and how to spend"
        res_cal = _extract_calendar_widget(text_cal)
        self.assertIsNotNone(res_cal)
        self.assertEqual(res_cal["type"], "calendar_widget")
        self.assertEqual(res_cal["position"], "flank_right")
        self.assertEqual(res_cal["badge"], "SCHEDULE MILESTONE")
        self.assertIn("202", res_cal["title"])

        # Rhetorical rejection guard: dismissing calendar advice must NOT trigger a calendar widget (including unicode quote)
        rejection_text = "past the cookie-cutter information of how to manage your calendars"
        self.assertIsNone(_extract_calendar_widget(rejection_text))
        rejection_unicode = "don’t manage your calendars"
        self.assertIsNone(_extract_calendar_widget(rejection_unicode))

    def test_time_widget_extraction(self):
        """Phrases emphasizing finite time allocation trigger time_widget, while negative time statements are guarded."""
        # Legitimate time allocation
        text_time = "strategic time allocation and management across your projects"
        res_time = _extract_time_widget(text_time)
        self.assertIsNotNone(res_time)
        self.assertEqual(res_time["type"], "time_widget")
        self.assertEqual(res_time["badge"], "RESOURCE ALLOCATION")
        self.assertNotIn("imageSrc", res_time, "Time widget must not hardcode static AI slop imageSrc")

        # Negative/rejection statement must NOT trigger time widget (including unicode quotes and colloquial time mentions)
        neg_time = "time doesn't need to be managed your priorities do"
        self.assertIsNone(_extract_time_widget(neg_time))
        neg_time_unicode = "time doesn’t need to be managed your priorities do"
        self.assertIsNone(_extract_time_widget(neg_time_unicode))
        colloquial_time = "how to spend X amount of time on certain things"
        self.assertIsNone(_extract_time_widget(colloquial_time))

    def test_before_after_comparison_extraction(self):
        """Phrases indicating comparison or transformation trigger before_after_comparison with dynamic titles and labels."""
        # Case A: Before and after
        text_a = "LOOK AT THE BEFORE AND AFTER TRANSFORMATION"
        res_a = _extract_comparison(text_a)
        self.assertIsNotNone(res_a)
        self.assertEqual(res_a["type"], "before_after_comparison")
        self.assertEqual(res_a["title"], "TRANSFORMATION")

        # Case B: VS / Versus (dynamic entity title and labels)
        text_b = "Manual Outreach vs Automated Inbound"
        res_b = _extract_comparison(text_b)
        self.assertIsNotNone(res_b)
        self.assertEqual(res_b["type"], "before_after_comparison")
        self.assertEqual(res_b["beforeLabel"], "MANUAL OUTREACH")
        self.assertEqual(res_b["afterLabel"], "AUTOMATED INBOUND")
        self.assertEqual(res_b["title"], "MANUAL OUTRE VS AUTOMATED IN")

        # Case C: Instead of (dynamic entity title and role labels)
        text_c = "Instead of guessing keywords, use high-intent buyer search terms"
        res_c = _extract_comparison(text_c)
        self.assertIsNotNone(res_c)
        self.assertEqual(res_c["type"], "before_after_comparison")
        self.assertEqual(res_c["beforeLabel"], "INSTEAD OF")
        self.assertEqual(res_c["afterLabel"], "CHOOSE")
        self.assertIn("GUESSING", res_c["title"])
        self.assertIn("HIGH-INT", res_c["title"])

        # Case D: Moving from X to Y (dynamic entity title and role labels)
        text_d = "No, we're moving now from managing time to managing priorities."
        res_d = _extract_comparison(text_d)
        self.assertIsNotNone(res_d)
        self.assertEqual(res_d["type"], "before_after_comparison")
        self.assertEqual(res_d["beforeLabel"], "FROM")
        self.assertEqual(res_d["afterLabel"], "TO")
        self.assertIn("MANAGING", res_d["title"])
        self.assertIn("PRIORITIES", res_d["title"])

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

    def test_optical_rack_focus_extraction(self):
        """Phrases referencing priorities, inflection points, or focal pull trigger optical_rack_focus."""
        text_focus = "competing priorities. At some point, something has to win."
        res_focus = _extract_optical_rack_focus(text_focus)
        self.assertIsNotNone(res_focus)
        self.assertEqual(res_focus["type"], "optical_rack_focus")
        self.assertEqual(res_focus["position"], "fullscreen")
        self.assertTrue(res_focus["enableBloom"])
        self.assertTrue(res_focus["enableFilmGrain"])
        self.assertEqual(res_focus["focalPlaneRole"], "primary")

        chunks = [{"chunkIndex": 0, "text": text_focus}]
        plans = detect_and_plan_visual_helpers(chunks)
        self.assertIn(0, plans)
        self.assertEqual(plans[0]["type"], "optical_rack_focus")

    def test_metric_noun_whitelist_rejects_adjectives(self):
        """Phrases with numbers followed by adjectives like 'physical' are rejected to prevent nonsensical cards."""
        text_adjective = "than 12,000 physical products"
        res = _extract_metric_number(text_adjective)
        self.assertIsNone(res, "Should not create a motion_number badge when noun is an unwhitelisted adjective")

        text_legit = "than 12,000 products"
        res_legit = _extract_metric_number(text_legit)
        self.assertIsNotNone(res_legit)
        self.assertEqual(res_legit["type"], "motion_number")
        self.assertEqual(res_legit["value"], 12000.0)

    def test_visual_helpers_governance_toggle(self):
        """When design disables visual helpers, automated extraction is suppressed."""
        chunks = [{"chunkIndex": 0, "text": "than 12,000 products"}]
        plans_enabled = detect_and_plan_visual_helpers(chunks, {"allowAutoVisualHelpers": True})
        self.assertIn(0, plans_enabled)

        plans_disabled = detect_and_plan_visual_helpers(chunks, {"enableVisualHelpers": False})
        self.assertEqual(plans_disabled, {}, "Should be empty when enableVisualHelpers is False")

if __name__ == "__main__":
    unittest.main()

