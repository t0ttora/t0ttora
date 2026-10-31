---
name: Oluş Emre GitHub profile
description: A quiet extension of the olusemre.dev identity.
colors:
  ink: "#10100e"
  paper: "#f8f7ef"
  muted: "#a5a59a"
  blue: "#1688e8"
typography:
  activity:
    fontFamily: "Arial, Helvetica, sans-serif"
components:
  hero:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    width: "100%"
  activity:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    width: "100%"
---

# Profile design

The profile extends the visual identity of [olusemre.dev](https://www.olusemre.dev) and the [Arche research journal](https://t0ttora.github.io/me492-caster-digital-twin/): dark surfaces, clear typography, a restrained blue accent and the original personal mark.

## Overview

The opening introduces the person and their work. Selected projects provide direct routes to the repositories. The activity calendar shows the rhythm of work across both public and private repositories.

The README remains readable as native Markdown. Custom styling is contained within the SVG images.

## Colors

| Token | Value | Purpose |
| --- | --- | --- |
| Ink | `#10100e` | SVG backgrounds |
| Paper | `#f8f7ef` | Main lettering and logo |
| Muted | `#a5a59a` | Dates and supporting labels |
| Blue | `#1688e8` | Contribution intensity |

Calendar cells use a small tonal scale from charcoal to pale blue. Brighter cells represent more daily contributions.

## Typography

- **Opening:** Neue Montreal, converted to vector outlines from the existing brand font.
- **Calendar:** Arial / Helvetica / sans-serif for compact labels.
- **Markdown:** GitHub’s native text, headings and links.

The opening requires no font download at viewing time. Use real text in image alternatives and SVG titles for accessibility.

## Layout

| Asset | Desktop | Mobile |
| --- | --- | --- |
| Opening | 1080 × 430 | 640 × 590 |
| Calendar | 1080 × 280 | 480 × 445 |

At widths of 600px and below, the README selects the mobile image. The mobile calendar divides the same year into two horizontal sections so daily cells remain legible. It does not discard the older half of the year.

## Elevation & Depth

The design is flat. Calendar cells are two-dimensional squares. There are no extruded columns, depth effects or shadows.

## Shapes

Preserve the original personal logo and fine dotted canvas. The large logo remains static, without surrounding rings, orbiting points or construction traces.

## Components

### Opening

Source: `scripts/render_hero.py`<br>
Outputs: `assets/hero.svg`, `assets/hero-mobile.svg`

The composition keeps “Design. Build. Innovate.”, the original logo and the established type. It contains no animation.

To regenerate with the existing brand font:

```sh
pip install fonttools brotli
python scripts/render_hero.py --font /path/to/neue-montreal.woff2
```

The source font is the existing [Arche font asset](https://t0ttora.github.io/me492-caster-digital-twin/assets/neue-montreal-regular.woff2). The source mark is the existing [personal logo](https://t0ttora.github.io/me492-caster-digital-twin/assets/olus-emre-logo.svg).

### Contribution calendar

Source: `scripts/render_activity.py`<br>
Outputs: `assets/contributions.svg`, `assets/contributions-mobile.svg`

The chart reads GitHub’s aggregate calendar after **Private contributions** is enabled in the profile’s contribution settings.

| Included | Never included |
| --- | --- |
| Contribution date | Private repository names or IDs |
| Daily contribution count | Commit messages or file paths |
| Total and active-day counts | Issue, pull request or organization details |

The query requests only the calendar and whether anonymous private contributions are available. The renderer explicitly whitelists dates, weekdays and counts. It never distributes private contributions artificially across dates.

The daily workflow runs at **03:20 UTC / 06:20 Istanbul** using the repository’s standard GitHub Actions token. No personal token or additional repository access is required. If private counts become unavailable, `--require-private` stops the refresh and retains the last committed calendar rather than silently publishing a public-only total.

```sh
python -m unittest discover -s tests
GH_TOKEN=... python scripts/render_activity.py --require-private
```

Set the token through your development environment; do not save it in source files.

## Do's and Don'ts

- Keep the original identity, clear hierarchy and generous spacing.
- Keep project descriptions factual and research status explicit.
- Refresh both calendar variants from the same source.
- Keep private repository details out of all generated files.
- Do not add rotation, orbiting decorations, scanning lights or 3D columns.
- Do not fabricate activity or modify GitHub’s own contribution calendar.
