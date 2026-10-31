import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("activity", Path(__file__).parents[1] / "scripts/render_activity.py")
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)


def calendar(counts):
    return {"totalContributions": sum(counts), "weeks": [{"contributionDays": [
        {"date": f"2026-10-{25+i:02}", "weekday": i, "contributionCount": n}
        for i, n in enumerate(counts)]}]}


class ActivityTests(unittest.TestCase):
    def test_empty_activity_is_valid_and_not_fabricated(self):
        svg = activity.render(calendar([0] * 7))
        ET.fromstring(svg)
        self.assertIn("0 public contributions", svg)
        self.assertNotIn("nan", svg.lower())
        self.assertNotIn("infinity", svg.lower())

    def test_counts_are_derived_from_actual_days(self):
        data = calendar([0, 1, 0, 5, 0, 0, 2])
        data["totalContributions"] = 999
        svg = activity.render(data)
        self.assertIn("8 public contributions", svg)
        self.assertIn("3 active days", svg)
        self.assertIn("Peak 5 / day", svg)
        self.assertNotIn("999", svg)
        ET.fromstring(svg)

    def test_reduced_motion_and_no_external_dependencies(self):
        svg = activity.render(calendar([1] * 7))
        self.assertIn("prefers-reduced-motion:reduce", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("<foreignObject", svg)
        self.assertNotIn("xlink:href", svg)

    def test_mobile_monthly_total_matches_daily_total(self):
        data = calendar([0, 1, 0, 5, 0, 0, 2])
        svg = activity.render_mobile(data)
        self.assertIn("8 public contributions", svg)
        self.assertIn("monthly contributions", svg)
        ET.fromstring(svg)
        ET.fromstring(activity.render_mobile(calendar([0] * 7)))

    def test_invalid_response_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / "response.json"
            data = calendar([-1])
            fixture.write_text(json.dumps({"data": {"user": {"contributionsCollection": {"contributionCalendar": data}}}}))
            with self.assertRaises(ValueError):
                activity.load_calendar("t0ttora", fixture)


if __name__ == "__main__":
    unittest.main()
