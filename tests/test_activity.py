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
        self.assertIn("0 contributions", svg)
        self.assertNotIn("nan", svg.lower())
        self.assertNotIn("infinity", svg.lower())

    def test_counts_are_derived_from_actual_days(self):
        data = calendar([0, 1, 0, 5, 0, 0, 2])
        data["totalContributions"] = 999
        svg = activity.render(data)
        self.assertIn("8 contributions", svg)
        self.assertIn("3 active days", svg)
        self.assertNotIn("999", svg)
        ET.fromstring(svg)

    def test_flat_static_output_has_no_dependencies_or_motion(self):
        svg = activity.render(calendar([1] * 7))
        self.assertNotIn("animation:", svg)
        self.assertNotIn("<animate", svg)
        self.assertNotIn("A year of building", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("<foreignObject", svg)
        self.assertNotIn("xlink:href", svg)

    def test_mobile_total_matches_daily_total(self):
        data = calendar([0, 1, 0, 5, 0, 0, 2])
        svg = activity.render_mobile(data)
        self.assertIn("8 contributions", svg)
        ET.fromstring(svg)
        ET.fromstring(activity.render_mobile(calendar([0] * 7)))

    def test_private_contributions_are_counted_without_repository_details(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / "response.json"
            collection = {
                "hasAnyRestrictedContributions": True,
                "restrictedContributionsCount": 5,
                "contributionCalendar": calendar([1, 5, 0]),
                "privateRepository": {"name": "never-publish-this-name"},
            }
            fixture.write_text(json.dumps({"data": {"user": {"contributionsCollection": collection}}}))
            data = activity.load_calendar("t0ttora", fixture, require_private=True)
            for svg in [activity.render(data), activity.render_mobile(data)]:
                self.assertIn("6 contributions", svg)
                self.assertNotIn("never-publish-this-name", svg)
                self.assertIn("Public + private", svg)

    def test_missing_private_counts_cannot_silently_publish_public_only(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / "response.json"
            collection = {"hasAnyRestrictedContributions": False, "contributionCalendar": calendar([1])}
            fixture.write_text(json.dumps({"data": {"user": {"contributionsCollection": collection}}}))
            with self.assertRaisesRegex(ValueError, "private"):
                activity.load_calendar("t0ttora", fixture, require_private=True)

    def test_invalid_response_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / "response.json"
            data = calendar([-1])
            fixture.write_text(json.dumps({"data": {"user": {"contributionsCollection": {"contributionCalendar": data}}}}))
            with self.assertRaises(ValueError):
                activity.load_calendar("t0ttora", fixture)


if __name__ == "__main__":
    unittest.main()
