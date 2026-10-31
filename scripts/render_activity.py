#!/usr/bin/env python3
"""Render an anonymous 2D calendar using public and opted-in private counts."""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import urllib.request

INK = "#10100e"
PAPER = "#f8f7ef"
MUTED = "#a5a59a"
BLUE = "#1688e8"
LEVELS = ["#252722", "#183e5b", "#16639a", "#1688e8", "#8ecbff"]
QUERY = """query($login:String!){user(login:$login){contributionsCollection{
hasAnyRestrictedContributions contributionCalendar{
totalContributions weeks{contributionDays{contributionCount date weekday}}}}}}"""


def load_calendar(login, fixture=None, require_private=False):
    if fixture:
        response = json.loads(Path(fixture).read_text(encoding="utf-8-sig"))
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is required")
        request = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json",
                     "User-Agent": "t0ttora-profile-renderer"},
        )
        with urllib.request.urlopen(request, timeout=30) as result:
            response = json.load(result)
    if response.get("errors"):
        raise RuntimeError("GitHub contribution query failed")
    collection = response["data"]["user"]["contributionsCollection"]
    if require_private and not collection.get("hasAnyRestrictedContributions"):
        raise ValueError("Anonymous private counts are unavailable; keeping the previous chart")
    source = collection["contributionCalendar"]
    days = [day for week in source["weeks"] for day in week["contributionDays"]]
    if not days or len(days) > 380:
        raise ValueError("Unexpected contribution calendar length")
    for day in days:
        dt.date.fromisoformat(day["date"])
        if type(day["contributionCount"]) is not int or day["contributionCount"] < 0:
            raise ValueError("Invalid contribution count")
        if day["weekday"] not in range(7):
            raise ValueError("Invalid weekday")
    # Whitelist the complete output contract: dates, counts, weekdays only.
    return {"weeks": [{"contributionDays": [
        {key: day[key] for key in ("date", "contributionCount", "weekday")}
        for day in week["contributionDays"]]} for week in source["weeks"]]}


def text(x, y, value, size=16, fill=PAPER, **attrs):
    extra = " ".join(f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
                     for key, value in attrs.items())
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>'
            f'{html.escape(str(value))}</text>')


def intensity(count, peak):
    if not count:
        return LEVELS[0]
    return LEVELS[1 + sum(count > peak * threshold for threshold in (.05, .2, .5))]


def grid(weeks, x, y, step, cell, peak):
    parts = []
    for weekday, label in [(1, "M"), (3, "W"), (5, "F")]:
        parts.append(text(x - 26, y + weekday * step + cell - 2, label, 11, MUTED))
    previous_month = None
    for index, week in enumerate(weeks):
        first = week["contributionDays"][0]
        month = first["date"][:7]
        if month != previous_month:
            # A new segment always starts with a date label.
            label = dt.date.fromisoformat(first["date"]).strftime("%b")
            if index != 0 or int(first["date"][8:]) <= 15 or len(weeks) < 3:
                parts.append(text(x + index * step, y - 12, label, 11, MUTED))
            previous_month = month
        for day in week["contributionDays"]:
            count = day["contributionCount"]
            parts.append(
                f'<rect x="{x + index * step}" y="{y + day["weekday"] * step}" '
                f'width="{cell}" height="{cell}" rx="2" fill="{intensity(count, peak)}">'
                f'<title>{day["date"]}: {count} contributions</title></rect>'
            )
    return parts


def render_chart(calendar, mobile=False):
    weeks = calendar["weeks"]
    days = [day for week in weeks for day in week["contributionDays"]]
    total = sum(day["contributionCount"] for day in days)
    active = sum(day["contributionCount"] > 0 for day in days)
    peak = max(day["contributionCount"] for day in days)
    width, height = (480, 445) if mobile else (1080, 280)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Contributions</title>',
        f'<desc id="desc">{total:,} contributions over the past year, {active} active days. '
        f'Public + private activity, {days[0]["date"]} to {days[-1]["date"]}. '
        'Only daily counts are shown. Private repository names and details are never included.</desc>',
        '<style>text{font-family:Arial,Helvetica,sans-serif}</style>',
        f'<rect width="{width}" height="{height}" fill="{INK}"/>',
    ]
    if mobile:
        out.extend([text(25, 43, "Contributions", 28),
                    text(25, 73, f"{total:,} contributions · past year", 17, MUTED)])
        split = (len(weeks) + 1) // 2
        out.extend(grid(weeks[:split], 51, 119, 15, 12, peak))
        if weeks[split:]:
            out.extend(grid(weeks[split:], 51, 281, 15, 12, peak))
        out.extend([
            text(25, 418, "Public + private · counts only", 13, MUTED),
            text(454, 418, f"{active} active days", 13, MUTED, text_anchor="end"),
        ])
    else:
        out.extend([text(32, 47, "Contributions", 29),
                    text(1048, 45, f"{total:,} contributions · past year", 18, PAPER, text_anchor="end")])
        out.extend(grid(weeks, 75, 93, 18, 14, peak))
        out.extend([
            text(32, 253, "Public + private · repository details stay private", 13, MUTED),
            text(650, 253, f"{active} active days", 13, MUTED),
            text(891, 253, "Less", 11, MUTED),
        ])
        for index, color in enumerate(LEVELS):
            out.append(f'<rect x="{925+index*18}" y="242" width="12" height="12" rx="2" fill="{color}"/>')
        out.append(text(1048, 253, "More", 11, MUTED, text_anchor="end"))
    out.append("</svg>")
    return "\n".join(out)


def render(calendar):
    return render_chart(calendar)


def render_mobile(calendar):
    return render_chart(calendar, mobile=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default="t0ttora")
    parser.add_argument("--fixture")
    parser.add_argument("--require-private", action="store_true",
                        help="Refuse public-only output if opted-in private counts disappear")
    parser.add_argument("--output", default="assets/contributions.svg")
    args = parser.parse_args()
    calendar = load_calendar(args.login, args.fixture, args.require_private)
    target = Path(args.output)
    outputs = {target: render(calendar),
               target.with_name(target.stem + "-mobile.svg"): render_mobile(calendar)}
    # Validate and render both variants before changing either destination.
    for path, value in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.with_suffix(".tmp").write_text(value, encoding="utf-8")
    for path in outputs:
        path.with_suffix(".tmp").replace(path)
    total = sum(day["contributionCount"] for week in calendar["weeks"] for day in week["contributionDays"])
    print(f"Rendered anonymous calendar with {total:,} contributions")


if __name__ == "__main__":
    main()

