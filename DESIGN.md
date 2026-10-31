---
name: Oluş Emre GitHub profile
description: Existing personal identity expressed through a drafting canvas and public activity field.
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
    typography: "{typography.activity}"
    width: "100%"
---

# Design System: Oluş Emre GitHub profile

## Overview

A compact GitHub profile built around the existing Oluş Emre identity: a dark drafting canvas, outlined brand typography, the original star mark and measured blue motion. The README keeps project descriptions and links in GitHub’s native typography; custom styling lives inside self-contained SVG assets.

This records an established brand implementation, not a new application design system. The palette follows olusemre.dev and the public Arche research project. “Drafting canvas” describes the implemented visual metaphor rather than a newly selected brand name.

**Key Characteristics:**

- Ink canvas and paper lettering with a single blue accent.
- Original logo geometry and outlined Neue Montreal hero type.
- Responsive vector compositions and real public contribution data.

## Colors

Blue is the primary accent for the constructed mark, traces and activity tops. Ink is the canvas; paper supplies primary lettering; muted supports annotations and dates. The frontmatter owns these four reusable values. Additional local SVG face shades, hairlines and opacity values remain in their source assets rather than becoming a new palette scale.

## Typography

The hero uses Neue Montreal converted to glyph paths from the user's Arche-hosted font. It has no runtime font dependency; edit the source lettering through the same outline generation process. The chart uses the Arial/Helvetica/sans-serif stack, with desktop heading (34 SVG units), mobile heading (30), and supporting labels (11–18). README prose, headings and links inherit GitHub's typography and theme.

## Layout

The desktop hero is 1080 × 430; mobile is a separately composed 640 × 590 asset. Activity is 1080 × 440 on desktop and 480 × 380 on mobile. Both README picture elements select their mobile source at a maximum viewport width of 600px and render at full available width. The desktop hero pairs lettering with a construction diagram; the narrow composition reflows rather than shrinking the entire desktop scene. An 18-unit dotted grid and fine drafting marks structure the hero. README projects remain a simple vertical list, with a native disclosure for Turkish text.

## Elevation & Depth

No drop shadows or floating surfaces. Hero depth comes from fine construction lines and overlapping circular geometry. Activity uses distinct front, side and top faces to create an isometric field; desktop weeks advance horizontally and weekdays recede.

## Shapes

Rectangular SVG canvases have square corners. The original star mark, circular construction rings, dashed traces, dots and fine rules establish the form language. Preserve the supplied logo geometry from https://t0ttora.github.io/me492-caster-digital-twin/assets/olus-emre-logo.svg rather than redrawing an approximate star.

## Components

**Hero:** `assets/hero.svg` and `assets/hero-mobile.svg` are code-generated vectors. The outer and inner construction rings orbit in 40s and 24s (inner reversed); the mark rocks over 9s and the trace animates over 9s. All stop under `prefers-reduced-motion: reduce`. Titles, descriptions and README image alt text carry the identity when decorative glyph paths are hidden from accessibility APIs.

**Public activity:** `scripts/render_activity.py` queries GitHub's contribution calendar and generates both activity SVGs. Desktop heights use `8 + 30 × log(1 + daily count)` for nonzero days. Mobile groups counts by calendar month and scales logarithmic monthly heights to its available field. These are explicitly public counts, not a complete private-work record. A decorative survey sweep runs for 9s; top-face shimmer and mobile pulse run for 7s. Reduced motion disables them and hides the sweep. Exact totals, active days, peak and date range remain textual. The additional visualization leaves GitHub's native contribution chart untouched.

**Maintenance:** `.github/workflows/activity.yml` schedules refresh at 03:20 UTC daily, with manual dispatch and renderer/workflow-change triggers. It tests before rendering and commits only generated activity assets. Fetch or validation failure occurs before replacement, retaining the last committed visual. Keep generated numbers and date ranges synchronized by running the renderer; regenerate this record and its sidecar when visual source changes. These are vector code assets, so raster/AI-image prompt provenance does not apply. No PRODUCT.md is required for this scoped profile record.

Hero source is in `scripts/render_hero.py`. To regenerate it, install `fonttools` and `brotli` in a development environment and run `python scripts/render_hero.py --font /path/to/neue-montreal.woff2`. Use the same authorized brand font as the Arche site; its published asset is `https://t0ttora.github.io/me492-caster-digital-twin/assets/neue-montreal-regular.woff2`. Font files are not required by the profile or daily activity job because hero lettering ships as outlines.

## Do's and Don'ts

- Do preserve the original star geometry and outlined hero typography.
- Do keep decorative movement separate from the meaning of contribution counts.
- Do retain mobile compositions, accessible image descriptions and reduced-motion rules.
- Do regenerate activity from GitHub data rather than editing the generated values.
- Don’t describe the survey light as live activity.
- Don’t replace GitHub’s native contribution chart or README text styling.
- Don’t introduce application controls or states into this profile design record.
