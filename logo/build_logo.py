#!/usr/bin/env python3
"""Builds the @docbeyondthebarbell logo set as SVGs with all text converted to outlines.

Run:  python3 build_logo.py      (writes svg/*.svg; render.js turns them into PNGs)
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONTS = HERE.parent / "posters" / "fonts"
OUT = HERE / "svg"

GOLD, INK, BLACK, CREAM = "#c8963e", "#ece6da", "#0e0d0c", "#ebe4d6"

_fonts = {k: TTFont(str(FONTS / f)) for k, f in {
    "Anton": "anton-latin-400-normal.woff2",
    "Inter700": "inter-latin-700-normal.woff2",
    "Playfair": "playfair-display-latin-400-normal.woff2",
}.items()}


def _glyph(face, ch):
    f = _fonts[face]
    name = f.getBestCmap()[ord(ch)]
    return name, f["hmtx"][name][0]


def text_width(face, s, size, ls=0):
    upm = _fonts[face]["head"].unitsPerEm
    return sum(_glyph(face, ch)[1] for ch in s) * size / upm + ls * (len(s) - 1)


def cap_height(face, size):
    f = _fonts[face]
    return f["OS/2"].sCapHeight * size / f["head"].unitsPerEm


def glyph_path(face, ch, size, x=0.0, y=0.0):
    """SVG path data for one glyph, baseline at y, left edge at x."""
    f = _fonts[face]
    name, _ = _glyph(face, ch)
    s = size / f["head"].unitsPerEm
    pen = SVGPathPen(f.getGlyphSet())
    f.getGlyphSet()[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
    return pen.getCommands()


def text_path(face, s, size, x, y, fill, ls=0, anchor="start"):
    if anchor == "middle":
        x -= text_width(face, s, size, ls) / 2
    elif anchor == "end":
        x -= text_width(face, s, size, ls)
    upm = _fonts[face]["head"].unitsPerEm
    d = []
    for ch in s:
        if ch != " ":
            d.append(glyph_path(face, ch, size, x, y))
        x += _glyph(face, ch)[1] * size / upm + ls
    return f'<path d="{" ".join(d)}" fill="{fill}"/>'


def arc_text(face, s, size, cx, cy, r, fill, ls=0, bottom=False):
    """Text along a circle: over the top reading clockwise, or along the bottom reading left to right."""
    upm = _fonts[face]["head"].unitsPerEm
    advs = [_glyph(face, ch)[1] * size / upm for ch in s]
    total = sum(advs) + ls * (len(s) - 1)
    rr = r if not bottom else r + cap_height(face, size)
    pos = -total / 2
    out = []
    for ch, adv in zip(s, advs):
        mid = pos + adv / 2
        ang = math.degrees(mid / rr)
        if ch != " ":
            if not bottom:
                d = glyph_path(face, ch, size, cx - adv / 2, cy - r)
                out.append(f'<path d="{d}" transform="rotate({ang:.3f} {cx} {cy})"/>')
            else:
                d = glyph_path(face, ch, size, cx - adv / 2, cy + rr)
                out.append(f'<path d="{d}" transform="rotate({-ang:.3f} {cx} {cy})"/>')
        pos += adv + ls
    return f'<g fill="{fill}">{"".join(out)}</g>'


def mark(x, y, width, color):
    """The symbol: a barbell whose bar carries one heartbeat. Drawn on an 800 x 400 grid, centred at (x, y)."""
    s = width / 800
    plates = [(64, 68, 340), (146, 46, 236)]
    rects = []
    for px, pw, ph in plates:
        for rx in (px, 800 - px - pw):
            rects.append(f'<rect x="{rx}" y="{-ph / 2}" width="{pw}" height="{ph}" rx="{min(pw / 2, 12)}"/>')
    ecg = "M0 0H306L326 -32L346 0H364L382 46L408 -206L436 114L454 0H472L490 -36L508 0H800"
    return (f'<g transform="translate({x - width / 2:.1f} {y:.1f}) scale({s:.5f})" fill="{color}">'
            f'<path d="{ecg}" fill="none" stroke="{color}" stroke-width="38" stroke-linejoin="round" stroke-linecap="round"/>'
            f'{"".join(rects)}</g>')


def svg(w, h, body, bg=None):
    back = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{back}{body}</svg>\n')


# ---------- lockups ----------

def profile(bg, ring, sym):
    """Instagram profile picture: symbol inside a thin ring, safe inside the circular crop."""
    n = 1080
    return svg(n, n, f'<circle cx="540" cy="540" r="455" fill="none" stroke="{ring}" stroke-width="14"/>'
                     + mark(540, 556, 740, sym), bg)


def badge(bg, ring, sym, top_txt, bottom_txt):
    n = 1200
    c = n / 2
    body = (f'<circle cx="{c}" cy="{c}" r="560" fill="none" stroke="{ring}" stroke-width="12"/>'
            f'<circle cx="{c}" cy="{c}" r="400" fill="none" stroke="{ring}" stroke-width="5"/>'
            + arc_text("Inter700", "DOC BEYOND THE BARBELL", 58, c, c, 470, top_txt, ls=12)
            + arc_text("Inter700", "MEDICINE · MUSCLE · MIND", 44, c, c, 450, bottom_txt, ls=12, bottom=True)
            + f'<circle cx="{c - 510}" cy="{c}" r="9" fill="{ring}"/><circle cx="{c + 510}" cy="{c}" r="9" fill="{ring}"/>'
            + mark(c, c + 20, 560, sym))
    return svg(n, n, body, bg)


def horizontal(bg, line1, line2, sym):
    h = 520
    size = 190
    tx = 120 + 560 + 90
    cap = cap_height("Anton", size)
    gap = 44
    top = (h - (2 * cap + gap)) / 2
    w = int(tx + max(text_width("Anton", "DOC BEYOND", size, 6), text_width("Anton", "THE BARBELL", size, 6)) + 120)
    body = (mark(120 + 280, h / 2, 560, sym)
            + text_path("Anton", "DOC BEYOND", size, tx, top + cap, line1, ls=6)
            + text_path("Anton", "THE BARBELL", size, tx, top + 2 * cap + gap, line2, ls=6))
    return svg(w, h, body, bg)


def stacked(bg, line1, line2, sym, tag):
    size = 170
    cap = cap_height("Anton", size)
    y1 = 560 + cap
    w, h = 1400, int(y1 + 2 * cap + 150 + 110)
    body = (mark(w / 2, 330, 760, sym)
            + text_path("Anton", "DOC BEYOND", size, w / 2, y1, line1, ls=8, anchor="middle")
            + text_path("Anton", "THE BARBELL", size, w / 2, y1 + cap + 40, line2, ls=8, anchor="middle")
            + text_path("Inter700", "MEDICINE · MUSCLE · MIND", 40, w / 2, y1 + 2 * cap + 150, tag, ls=16, anchor="middle"))
    return svg(w, h, body, bg)


def instagram_handle(text_color):
    """Instagram glyph + handle in Playfair Display, for posters, slides and video end cards."""
    icon, size = 170, 128
    tx = icon + 50
    w = int(tx + text_width("Playfair", "@docbeyondthebarbell", size) + 20)
    h = 220
    iy = (h - icon) / 2
    # baseline so the lowercase x-height sits centred on the icon
    xh = _fonts["Playfair"]["OS/2"].sxHeight * size / _fonts["Playfair"]["head"].unitsPerEm
    base = h / 2 + xh / 2
    s = icon / 100  # glyph drawn on a 100 x 100 grid
    glyph = (f'<defs><radialGradient id="ig" cx="0.3" cy="1.07" r="1.5">'
             '<stop offset="0" stop-color="#fdf497"/><stop offset="0.05" stop-color="#fdf497"/>'
             '<stop offset="0.45" stop-color="#fd5949"/><stop offset="0.6" stop-color="#d6249f"/>'
             '<stop offset="0.9" stop-color="#285aeb"/></radialGradient></defs>'
             f'<g id="instagram-icon" transform="translate(0 {iy:.1f}) scale({s:.4f})">'
             '<rect width="100" height="100" rx="24" fill="url(#ig)"/>'
             '<rect x="19" y="19" width="62" height="62" rx="18" fill="none" stroke="#fff" stroke-width="7.5"/>'
             '<circle cx="50" cy="50" r="15" fill="none" stroke="#fff" stroke-width="7.5"/>'
             '<circle cx="69.5" cy="30.5" r="4.6" fill="#fff"/></g>')
    return svg(w, h, glyph + text_path("Playfair", "@docbeyondthebarbell", size, tx, base, text_color))


LOGOS = {
    "profile-picture": profile(BLACK, GOLD, GOLD),
    "badge-dark": badge(BLACK, GOLD, GOLD, INK, GOLD),
    "badge-gold-transparent": badge(None, GOLD, GOLD, GOLD, GOLD),
    "badge-white-transparent": badge(None, "#ffffff", "#ffffff", "#ffffff", "#ffffff"),
    "horizontal-dark": horizontal(BLACK, INK, GOLD, GOLD),
    "horizontal-light": horizontal(CREAM, BLACK, "#a8402b", BLACK),
    "horizontal-white-transparent": horizontal(None, "#ffffff", "#ffffff", "#ffffff"),
    "stacked-dark": stacked(BLACK, INK, GOLD, GOLD, "#8a8378"),
    "stacked-light": stacked(CREAM, BLACK, "#a8402b", BLACK, "#6f675c"),
    "mark-gold-transparent": svg(900, 500, mark(450, 250, 800, GOLD)),
    "mark-black-transparent": svg(900, 500, mark(450, 250, 800, BLACK)),
    "instagram-handle-black": instagram_handle("#000000"),
    "instagram-handle-white": instagram_handle("#ffffff"),
    "instagram-handle-gold": instagram_handle(GOLD),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, data in LOGOS.items():
        (OUT / f"{name}.svg").write_text(data, encoding="utf-8")
        print("wrote", name)
