#!/usr/bin/env python3
"""Build a self-contained animated SVG from GitHub's public contribution calendar.

No third-party service, secret in an image URL, or private repository name.
Fetching/render failures leave the last committed visual untouched.
"""
import argparse
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import urllib.request

INK = "#10100e"
PAPER = "#f8f7ef"
MUTED = "#a5a59a"
BLUE = "#1688e8"

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{
contributionCount date weekday}}}}}}"""


def load_calendar(login, fixture=None):
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
    calendar = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    if not days or len(days) > 380:
        raise ValueError("Unexpected contribution calendar length")
    for day in days:
        dt.date.fromisoformat(day["date"])
        if not isinstance(day["contributionCount"], int) or day["contributionCount"] < 0:
            raise ValueError("Invalid contribution count")
        if day["weekday"] not in range(7):
            raise ValueError("Invalid weekday")
    return calendar


def text(x, y, value, size=16, fill=PAPER, **attrs):
    extra = " ".join(f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
                     for key, value in attrs.items())
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>'
            f'{html.escape(str(value))}</text>')


def render(calendar):
    weeks = calendar["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total = sum(d["contributionCount"] for d in days)
    active = sum(d["contributionCount"] > 0 for d in days)
    peak = max(d["contributionCount"] for d in days)
    start, end = days[0]["date"], days[-1]["date"]
    # Daily heights are logarithmic. Weeks run left-to-right; weekdays recede.
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="440" '
           'viewBox="0 0 1080 440" role="img" aria-labelledby="title desc">',
           '<title id="title">A year of building — public GitHub activity</title>',
           f'<desc id="desc">{total} public contributions, {active} active days, '
           f'from {start} to {end}. Peak: {peak} in a day. '
           'Each column is a week; seven rows are weekdays. '
           'Vertical height uses log(1 + daily contributions). '
           'The moving blue survey light is decorative and does not represent live events.</desc>',
           '<defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
           '<circle cx="1" cy="1" r=".7" fill="#f8f7ef" opacity=".07"/></pattern>'
           '<linearGradient id="survey"><stop stop-color="#1688e8" stop-opacity="0"/>'
           '<stop offset=".7" stop-color="#1688e8" stop-opacity=".2"/>'
           '<stop offset="1" stop-color="#1688e8" stop-opacity="0"/></linearGradient>'
           '<clipPath id="field"><rect x="30" y="100" width="1020" height="270"/></clipPath></defs>',
           '<style>text{font-family:Arial,Helvetica,sans-serif}'
           '.survey{animation:survey 9s linear infinite}'
           '.spark{animation:light 7s ease-in-out infinite;animation-delay:var(--delay)}'
           '@keyframes survey{0%{transform:translateX(-200px)}100%{transform:translateX(1300px)}}'
           '@keyframes light{0%,80%,100%{opacity:.45}40%{opacity:1}}'
           '@media(prefers-reduced-motion:reduce){.survey,.spark{animation:none}.survey{display:none}}'
           '</style>',
           f'<rect width="1080" height="440" fill="{INK}"/>',
           '<rect width="1080" height="440" fill="url(#dots)"/>',
           text(38, 54, 'A year of building.', 34),
           text(1042, 50, 'PUBLIC GITHUB ACTIVITY', 12, MUTED, text_anchor="end"),
           '<path d="M38 78H1042" stroke="#393934"/>']
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            month = day["date"][:7]
            if day["date"][8:] <= "07" and day["weekday"] == 0 and month != last_month:
                label = dt.date.fromisoformat(day["date"]).strftime("%b")
                out.append(text(62 + wi * 17.7, 361, label, 11, MUTED))
                last_month = month
        # Draw far to near so real foreground cells occlude far ones.
        for day in reversed(week["contributionDays"]):
            count = day["contributionCount"]
            row = day["weekday"]
            x = 66 + wi * 17.7 + row * 9
            y = 291 - row * 13.5
            h = 0 if not count else 8 + math.log1p(count) * 30
            top = y - h
            w, dx, dy = 12.5, 7, -5.2
            if count:
                intensity = math.log1p(count) / math.log1p(max(peak, 1))
                out.extend([
                    f'<path d="M{x:.1f},{y:.1f}v{-h:.1f}l{w},0v{h:.1f}Z" fill="#0c416b" stroke="#1688e8" stroke-opacity=".4" stroke-width=".6"/>',
                    f'<path d="M{x+w:.1f},{y:.1f}v{-h:.1f}l{dx},{dy}v{h:.1f}Z" fill="#125c99"/>',
                    f'<path class="spark" style="--delay:{-(wi*.19+row*.3):.2f}s" d="M{x:.1f},{top:.1f}h{w}l{dx},{dy}h{-w}Z" fill="{BLUE}" opacity="{.6+intensity*.4:.2f}"/>',
                    f'<path d="M{x:.1f},{top:.1f}h{w}l{dx},{dy}" fill="none" stroke="#9fd4ff" stroke-width=".7"/>'
                ])
            else:
                out.append(f'<path d="M{x:.1f},{y:.1f}h{w}l{dx},{dy}h{-w}Z" fill="#21211e" stroke="#393934" stroke-width=".6"/>')
    out.extend([
        '<g clip-path="url(#field)"><rect class="survey" x="-160" y="100" width="160" height="250" fill="url(#survey)"/></g>',
        '<path d="M38 382H1042" stroke="#393934"/>',
        text(38, 412, f'{total:,} public contributions', 16),
        text(350, 412, f'{active} active days', 14, MUTED),
        text(620, 412, f'Peak {peak} / day', 14, MUTED),
        text(1042, 412, f'{start} — {end}', 12, MUTED, text_anchor="end"),
        '</svg>'
    ])
    return "\n".join(out)


def render_mobile(calendar):
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]
    monthly = {}
    for day in days:
        key = day["date"][:7]
        monthly[key] = monthly.get(key, 0) + day["contributionCount"]
    peak = max(monthly.values(), default=0)
    total = sum(monthly.values())
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="380" viewBox="0 0 480 380" role="img" aria-labelledby="title desc">',
        '<title id="title">A year of building — monthly public activity</title>',
        f'<desc id="desc">{total} public contributions grouped by calendar month. Bar heights use log(1 + monthly contributions).</desc>',
        '<style>text{font-family:Arial,Helvetica,sans-serif}.pulse{animation:light 7s ease-in-out infinite}@keyframes light{0%,100%{opacity:.65}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.pulse{animation:none}}</style>',
        f'<rect width="480" height="380" fill="{INK}"/>',
        text(24, 48, "A year of building.", 30),
        text(25, 78, "PUBLIC ACTIVITY / MONTHLY OVERVIEW", 11, MUTED),
        '<path d="M24 99H456M24 293H456" stroke="#393934"/>'
    ]
    for index, (month, count) in enumerate(monthly.items()):
        x = 28 + index * (419 / len(monthly))
        height = 0 if not count else 10 + math.log1p(count) / math.log1p(peak) * 145
        out.append(f'<rect class="pulse" x="{x:.2f}" y="{280-height:.2f}" width="18" height="{max(height,2):.2f}" fill="{BLUE if count else "#393934"}"/>')
        out.append(text(round(x), 312, dt.date.fromisoformat(month+"-01").strftime("%b")[0], 12, MUTED))
    out.extend([
        text(24, 350, f"{total:,} public contributions", 18),
        text(455, 350, days[-1]["date"], 12, MUTED, text_anchor="end"),
        '</svg>'
    ])
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default="t0ttora")
    parser.add_argument("--fixture")
    parser.add_argument("--output", default="assets/contributions.svg")
    args = parser.parse_args()
    calendar = load_calendar(args.login, args.fixture)
    rendered = render(calendar)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(target)
    mobile = target.with_name(target.stem + "-mobile.svg")
    mobile_temp = mobile.with_suffix(".tmp")
    mobile_temp.write_text(render_mobile(calendar), encoding="utf-8")
    mobile_temp.replace(mobile)
    print(f"Rendered {target} using {sum(d['contributionCount'] for w in calendar['weeks'] for d in w['contributionDays'])} public contributions")


if __name__ == "__main__":
    main()

