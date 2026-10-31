from pathlib import Path
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

import argparse
parser = argparse.ArgumentParser(description="Regenerate the portfolio-inspired outlined hero assets.")
parser.add_argument("--font", required=True, help="Path to the original Neue Montreal font (TTF or WOFF2)")
args = parser.parse_args()
OUT=Path(__file__).resolve().parents[1]/"assets"
FONT=TTFont(args.font)
GLYPHS=FONT.getGlyphSet()
CMAP=FONT.getBestCmap()
EM=FONT["head"].unitsPerEm
PAPER="#f8f7ef"
INK="#10100e"
BLUE="#1688e8"
LOGO="M33 25 L38 25 L49 34 L54 20 L60 19 L71 23 L70 40 L86 38 L89 53 L74 60 L84 73 L74 84 L69 83 L62 75 L58 75 L52 90 L43 88 L37 84 L40 69 L22 70 L19 55 L34 49 L25 39 L25 33 Z M51 41 L44 63 L51 64 L67 59 L67 55 Z"

def lettering(value,x,y,size,fill=PAPER):
    glyphs=[]
    cursor=0
    for char in value:
        name=CMAP.get(ord(char),".notdef")
        pen=SVGPathPen(GLYPHS)
        GLYPHS[name].draw(pen)
        d=pen.getCommands()
        if d:
            glyphs.append(f'<path d="{d}" transform="translate({cursor},0)"/>')
        cursor+=FONT["hmtx"].metrics[name][0]
    s=size/EM
    return f'<g aria-hidden="true" fill="{fill}" transform="translate({x},{y}) scale({s}, {-s})">{"".join(glyphs)}</g>'

def hero(mobile=False):
    w,h=(640,590) if mobile else (1080,430)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
    '<title id="title">Oluş Emre Demir — Design. Build. Innovate.</title>',
    '<desc id="desc">From idea to engineered product. Mechanical engineering, product and code. The original personal logo on a quiet drafting canvas, inspired by olusemre.dev.</desc>',
    '<defs><pattern id="dots" x="0" y="0" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#f8f7ef" opacity=".1"/></pattern></defs>',
    f'<path fill="{INK}" d="M0 0H{w}V{h}H0Z"/>',
    f'<path fill="url(#dots)" d="M25 25H{w}V{h}H25Z"/>',
    f'<path d="M25 0V{h}M0 25H{w}" fill="none" stroke="#44443d" stroke-width=".7"/>']
    for x in range(80,w,100):
        out.append(f'<path d="M{x} 19v6" stroke="#73736a" stroke-width=".7"/>')
        out.append(lettering(str(x-80),x-5,14,9,"#a5a59a"))
    for y in range(80,h,100):
        out.append(f'<path d="M19 {y}h6" stroke="#73736a" stroke-width=".7"/>')
    out.extend([
        '<g transform="translate(47,42) scale(.5)">',
        f'<path d="{LOGO}" fill="{PAPER}" fill-rule="evenodd"/></g>',
        lettering("Oluş Emre Demir",112,77,21),
        lettering("Mechanical engineering / Product / Code",112,99,12,"#a5a59a"),
    ])
    if mobile:
        out.extend([lettering("Design. Build.",48,219,74),
                    lettering("Innovate.",48,301,74),
                    lettering("From idea to engineered product.",50,346,20,"#a5a59a")])
        cx,cy,scale=485,447,.63
    else:
        out.extend([lettering("Design. Build.",48,210,80),
                    lettering("Innovate.",48,295,80),
                    lettering("From idea to engineered product.",51,341,21,"#a5a59a")])
        cx,cy,scale=834,229,1
    out.append(f'<g transform="translate({cx},{cy}) scale({scale})">')
    out.append('<g transform="translate(-108,-108) scale(2)">')
    out.append(f'<path d="{LOGO}" fill="{PAPER}" fill-rule="evenodd"/></g>')
    out.append('</g>')
    if mobile:
        out.append(lettering("olusemre.dev",49,530,20))
        out.append(lettering("Istanbul / Türkiye",49,552,12,"#a5a59a"))
    else:
        out.append(lettering("Istanbul / Türkiye",51,403,12,"#a5a59a"))
        out.append(lettering("olusemre.dev",900,403,14))
    out.append('</svg>')
    return "\n".join(out)

OUT.mkdir(exist_ok=True)
for mobile,name in [(False,"hero.svg"),(True,"hero-mobile.svg")]:
    (OUT/name).write_text(hero(mobile),encoding="utf-8")
print("Generated outlined Neue Montreal hero assets; no external font dependency")
