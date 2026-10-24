#!/usr/bin/env python3
"""Builds the seven A3 @docbeyondthebarbell wall posters as self-contained SVGs.

Run:  python3 build.py        (writes NN-name.svg next to this file)
Images are linked from images/NN-name.jpg, so swapping in a high-res photo
with the same file name updates the poster without rebuilding.
"""
import base64
import html
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).parent
FONTS = HERE / "fonts"

W, H = 2970, 4200          # viewBox units: 10 units = 1 mm (A3 = 297 x 420 mm)
M = 160                    # 16 mm safe margin
FOOT_Y = 3930              # footer rule
HANDLE = "@docbeyondthebarbell"

THEMES = {
    "dark":  dict(bg="#0e0d0c", ink="#ece6da", accent="#c8963e", muted="#8a8378", vignette=0.55, ph="#1b1917"),
    "light": dict(bg="#ebe4d6", ink="#141210", accent="#a8402b", muted="#6f675c", vignette=0.18, ph="#d9d0bf"),
}

FONT_FILES = {
    "Anton": "anton-latin-400-normal.woff2",
    "Inter500": "inter-latin-500-normal.woff2",
    "Inter700": "inter-latin-700-normal.woff2",
    "PlayfairItalic": "playfair-display-latin-400-italic.woff2",
}
FACES = {  # css family, weight, style
    "Anton": ("Anton", 400, "normal"),
    "Inter500": ("Inter", 500, "normal"),
    "Inter700": ("Inter", 700, "normal"),
    "PlayfairItalic": ("Playfair Display", 400, "italic"),
}
_pil = {k: ImageFont.truetype(str(FONTS / f), 1000) for k, f in FONT_FILES.items()}


def cap_ratio(face):
    f = _pil[face]
    return (f.getmetrics()[0] - f.getbbox("H")[1]) / 1000


def text_w(face, text, size, ls=0):
    return _pil[face].getlength(text) * size / 1000 + ls * max(len(text) - 1, 0)


def fit(face, lines, width, max_size, ls=0):
    widest = max(text_w(face, l, 1000, 0) for l in lines) / 1000
    return min(max_size, (width - ls * max(len(l) for l in lines)) / widest)


def wrap(face, text, size, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and text_w(face, trial, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def t(face, x, y, s, size, fill, ls=0, anchor="start", opacity=1):
    fam, wt, st = FACES[face]
    extra = f' letter-spacing="{ls}"' if ls else ""
    extra += f' text-anchor="{anchor}"' if anchor != "start" else ""
    extra += f' opacity="{opacity}"' if opacity != 1 else ""
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{fam}, sans-serif" font-weight="{wt}" '
            f'font-style="{st}" font-size="{size:.1f}" fill="{fill}"{extra}>{html.escape(s)}</text>')


def font_css():
    rules = []
    for key, file in FONT_FILES.items():
        fam, wt, st = FACES[key]
        data = base64.b64encode((FONTS / file).read_bytes()).decode()
        rules.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};"
                     f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "\n".join(rules)


FONT_CSS = font_css()


# ---------- shared pieces ----------

def fade_mask(mid, x, y, w, h, fades):
    """Alpha mask for an image slot. fades: dict edge -> fade length in units."""
    grads, rects = [], []
    for i, (edge, length) in enumerate(fades.items()):
        gid = f"{mid}g{i}"
        if edge in ("left", "right"):
            x1, x2 = (x, x + length) if edge == "left" else (x + w, x + w - length)
            coords = f'x1="{x1}" y1="0" x2="{x2}" y2="0"'
        else:
            y1, y2 = (y, y + length) if edge == "top" else (y + h, y + h - length)
            coords = f'x1="0" y1="{y1}" x2="0" y2="{y2}"'
        grads.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" {coords}>'
                     f'<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>')
        rects.append(gid)
    # nest one mask per edge so the fades multiply
    masks, prev = [], None
    for i, gid in enumerate(rects):
        inner = f' mask="url(#{prev})"' if prev else ""
        masks.append(f'<mask id="{gid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                     f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})"{inner}/></mask>')
        prev = f"{gid}m"
    return "".join(grads) + "".join(masks), prev


def image_slot(c, mid, href, x, y, w, h, fades, align="xMidYMid"):
    defs, mask = fade_mask(mid, x, y, w, h, fades)
    ph = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c["ph"]}"/>'
          + t("Inter700", x + w / 2, y + h / 2, f"PLACE IMAGE  ·  {href}", 44, c["muted"], ls=8, anchor="middle"))
    img = (f'<image href="{href}" xlink:href="{href}" x="{x}" y="{y}" width="{w}" height="{h}" '
           f'preserveAspectRatio="{align} slice"/>')
    return defs, f'<g id="photo" mask="url(#{mask})">{ph}{img}</g>'


def logo(x_right, y_mid, color, scale=0.8):
    # ECG trace that flattens into a barbell
    w = 640 * scale
    p = "M0 0H120L150 -22L175 0H200L228 64L262 -96L292 32L312 0H640"
    plates = "".join(f'<rect x="{px}" y="{-ph / 2}" width="{pw}" height="{ph}" rx="4"/>'
                     for px, pw, ph in [(380, 26, 130), (412, 18, 90), (552, 18, 90), (576, 26, 130)])
    return (f'<g id="logo" transform="translate({x_right - w:.0f} {y_mid}) scale({scale})" fill="{color}">'
            f'<path d="{p}" fill="none" stroke="{color}" stroke-width="10" stroke-linejoin="round"/>{plates}</g>')


def chrome(c, num):
    head = (t("Inter700", M, 230, "DOC BEYOND THE BARBELL", 44, c["accent"], ls=16)
            + t("Inter500", W - M, 230, f"Rx  Nº {num:02d} / 07", 44, c["ink"], ls=10, anchor="end", opacity=0.75))
    foot = (f'<line x1="{M}" y1="{FOOT_Y}" x2="{W - M}" y2="{FOOT_Y}" stroke="{c["accent"]}" stroke-width="3" opacity="0.6"/>'
            + t("Inter700", M, 4060, HANDLE, 62, c["ink"], ls=6)
            + t("Inter500", W / 2 + 120, 4052, "MEDICINE · MUSCLE · MIND", 40, c["muted"], ls=14, anchor="middle")
            + logo(W - M, 4035, c["accent"]))
    return f'<g id="header">{head}</g><g id="footer">{foot}</g>'


def svg(theme, num, defs, body):
    c = THEMES[theme]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="297mm" height="420mm" viewBox="0 0 {W} {H}">
<defs>
<style>{FONT_CSS}</style>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 0.09"/></feComponentTransfer></filter>
<radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{c['vignette']}"/></radialGradient>
{defs}
</defs>
<rect id="background" width="{W}" height="{H}" fill="{c['bg']}"/>
{body}
<rect id="vignette" width="{W}" height="{H}" fill="url(#vig)" pointer-events="none"/>
<rect id="grain-layer" width="{W}" height="{H}" filter="url(#grain)" pointer-events="none"/>
{chrome(c, num)}
</svg>
"""


# ---------- text blocks ----------

def stack_block(c, x, width, lines, accent_idx, eyebrow, quote, author, top, bottom, max_size=520):
    """Goggins-style stacked headline + optional italic quote, vertically centred in [top, bottom]."""
    size = fit("Anton", lines, width, max_size)
    cap, lh = cap_ratio("Anton") * size, size * 0.98
    q_size, q_lh = 76, 76 * 1.38
    q_lines = wrap("PlayfairItalic", f"“{quote}”", q_size, width) if quote else []
    a_size = 46 if text_w("Inter700", f"— {author}", 46, 12) <= width else 38
    height = 70 + cap + lh * (len(lines) - 1) + (90 + q_lh * len(q_lines) if q_lines else 0) + 120
    y = top + (bottom - top - height) / 2
    out = [t("Inter700", x, y, eyebrow, 44, c["accent"], ls=16)]
    y += 70 + cap
    for i, line in enumerate(lines):
        out.append(t("Anton", x, y, line, size, c["accent"] if i in accent_idx else c["ink"]))
        y += lh
    y -= lh
    if q_lines:
        y += 90 + q_size
        for ql in q_lines:
            out.append(t("PlayfairItalic", x, y, ql, q_size, c["ink"], opacity=0.88))
            y += q_lh
        y -= q_lh
    out.append(t("Inter700", x, y + 120, f"— {author}", a_size, c["accent"], ls=12))
    return "".join(out)


# ---------- the seven posters ----------

def split_poster(num, theme, image, side, lines, accent_idx, eyebrow, quote, author, img_top=320):
    """Image on one side, stacked type on the other (layout B)."""
    c = THEMES[theme]
    img_w, col_w = 1760, 1110
    if side == "left":
        ix, fades, tx = 0, {"right": 560, "bottom": 420}, W - M - col_w
    else:
        ix, fades, tx = W - img_w, {"left": 560, "bottom": 420}, M
    if img_top:
        fades["top"] = 200
    defs, photo = image_slot(c, "m", image, ix, img_top, img_w, FOOT_Y - 50 - img_top, fades)
    text = stack_block(c, tx, col_w, lines, accent_idx, eyebrow, quote, author, 420, 3780)
    return svg(theme, num, defs, photo + f'<g id="type">{text}</g>')


def p01():
    return split_poster(1, "dark", "images/01-goggins.jpg", "left",
                        ["THEY", "DON’T", "KNOW", "ME,", "SON."], {4}, "ON SELF-BELIEF",
                        None, "DAVID GOGGINS", img_top=0)


def p02():
    return split_poster(2, "light", "images/02-tyson.jpg", "right",
                        ["DO IT", "LIKE YOU", "LOVE IT."], {2}, "ON DISCIPLINE",
                        "Discipline is doing what you hate to do, but doing it like you love it.", "MIKE TYSON")




def p03():
    """No photo: ECG trace that turns into a barbell, plus three evidence lines."""
    c = THEMES["dark"]
    a = c["accent"]
    cy = 1180
    ecg = (f"M0 {cy}H560L620 {cy - 70}L680 {cy}H760L830 {cy + 200}L930 {cy - 560}"
           f"L1020 {cy + 120}L1080 {cy}H1180")
    art = [f'<path d="{ecg}" fill="none" stroke="{a}" stroke-width="22" stroke-linejoin="round" stroke-linecap="round"/>',
           f'<line x1="1180" y1="{cy}" x2="2780" y2="{cy}" stroke="{a}" stroke-width="30" stroke-linecap="round"/>']
    for x, w, h in [(1300, 46, 220), (1360, 90, 640), (1466, 64, 460), (1546, 28, 170),
                    (2386, 28, 170), (2430, 64, 460), (2510, 90, 640), (2616, 46, 220)]:
        art.append(f'<rect x="{x}" y="{cy - h / 2}" width="{w}" height="{h}" rx="10" fill="{a}"/>')
    out = [t("Inter700", M, 520, "ON LONGEVITY", 44, a, ls=16)]
    lines = ["STRENGTH IS", "MEDICINE."]
    hs = fit("Anton", lines, W - 2 * M, 560)
    hy = 1720 + cap_ratio("Anton") * hs
    out.append(t("Anton", M - 8, hy, lines[0], hs, c["ink"]))
    out.append(t("Anton", M - 8, hy + hs * 0.98, lines[1], hs, a))
    facts = [
        ("Grip strength predicts death from any cause better than systolic blood pressure.",
         "Leong et al., The Lancet, 2015 — PURE study, 140,000 adults, 17 countries"),
        ("Skeletal muscle is the body’s largest glucose sink — it clears most of the sugar insulin pushes out of your blood.",
         "DeFronzo et al., Diabetes, 1981"),
        ("Resistance training lowers resting blood pressure.",
         "Edwards et al., British Journal of Sports Medicine, 2023 — meta-analysis of 270 trials"),
    ]
    fy = hy + hs * 0.98 + 260
    for i, (fact, src) in enumerate(facts, 1):
        out.append(f'<line x1="{M}" y1="{fy - 110}" x2="{W - M}" y2="{fy - 110}" stroke="{c["ink"]}" stroke-width="2" opacity="0.18"/>')
        out.append(t("Anton", M, fy + 10, f"{i:02d}", 110, a))
        yy = fy - 10
        for line in wrap("Inter500", fact, 56, W - 2 * M - 220):
            out.append(t("Inter500", M + 220, yy, line, 56, c["ink"]))
            yy += 76
        out.append(t("Inter500", M + 220, yy + 6, src, 36, c["muted"], ls=2))
        fy = yy + 200
    return svg("dark", 3, "", f'<g id="artwork">{"".join(art)}</g><g id="type">{"".join(out)}</g>')






def p04():
    """Record time on top, the 1955 Sports Illustrated cover shown whole, medical-student line below."""
    c = THEMES["light"]
    out = [t("Inter700", M, 420, "6 MAY 1954  ·  IFFLEY ROAD, OXFORD", 46, c["accent"], ls=16)]
    big = fit("Anton", ["3:59.4"], W - 2 * M, 1000)
    y = 420 + 80 + cap_ratio("Anton") * big
    out.append(t("Anton", M - 10, y, "3:59.4", big, c["ink"]))
    out.append(t("Inter700", M, y + 130, "THE FIRST MILE EVER RUN UNDER FOUR MINUTES.", 54, c["ink"], ls=10))
    # magazine cover, uncropped, tilted like a print pinned to the wall
    band_top, band_bot = y + 300, 3080
    ch = band_bot - band_top
    cw = ch * 1135 / 1580
    cx = W - M - cw - 40
    href = "images/04-bannister-si-cover.jpg"
    defs = ('<filter id="shadow" x="-10%" y="-10%" width="125%" height="125%">'
            '<feDropShadow dx="18" dy="26" stdDeviation="26" flood-color="#000" flood-opacity="0.35"/></filter>')
    cover = (f'<g id="photo" transform="rotate(3 {cx + cw / 2:.0f} {band_top + ch / 2:.0f})" filter="url(#shadow)">'
             f'<rect x="{cx:.0f}" y="{band_top:.0f}" width="{cw:.0f}" height="{ch:.0f}" fill="{c["ph"]}"/>'
             f'<image href="{href}" xlink:href="{href}" x="{cx:.0f}" y="{band_top:.0f}" width="{cw:.0f}" height="{ch:.0f}" '
             f'preserveAspectRatio="xMidYMid slice"/></g>')
    # left column beside the cover
    colw = cx - 140 - M
    lines = ["THE FIRST", "SPORTSMAN", "OF THE YEAR."]
    hs = fit("Anton", lines, colw, 300)
    q = "“The man who can drive himself further once the effort gets painful is the man who will win.”"
    q_lines = wrap("PlayfairItalic", q, 66, colw)
    block = 70 + cap_ratio("Anton") * hs + hs * 0.98 * 2 + 110 + 92 * len(q_lines) + 110
    ly = band_top + (ch - block) / 2
    out.append(t("Inter700", M, ly, "SPORTS ILLUSTRATED  ·  JAN 1955", 40, c["accent"], ls=14))
    ly += 70 + cap_ratio("Anton") * hs
    for i, line in enumerate(lines):
        out.append(t("Anton", M - 6, ly, line, hs, c["accent"] if i == 2 else c["ink"]))
        ly += hs * 0.98
    ly += 110 - hs * 0.98 + 66
    for line in q_lines:
        out.append(t("PlayfairItalic", M, ly, line, 66, c["ink"], opacity=0.88))
        ly += 92
    out.append(t("Inter700", M, ly + 20, "— ROGER BANNISTER", 44, c["accent"], ls=12))
    hs2 = fit("Anton", ["HE WAS A MEDICAL STUDENT."], W - 2 * M, 300)
    hy = 3260 + cap_ratio("Anton") * hs2
    out.append(t("Anton", M, hy, "HE WAS A MEDICAL STUDENT.", hs2, c["accent"]))
    body = ("Roger Bannister trained in his lunch hour while studying medicine "
            "— and went on to become one of Britain’s leading neurologists.")
    by = hy + 120
    for line in wrap("Inter500", body, 58, W - 2 * M):
        out.append(t("Inter500", M, by, line, 58, c["ink"], opacity=0.85))
        by += 84
    return svg("light", 4, defs, cover + f'<g id="type">{"".join(out)}</g>')


def p05():
    c = THEMES["dark"]
    defs, photo = image_slot(c, "m", "images/05-arnold.jpg", 0, 300, 2050, 3000,
                             {"right": 520, "bottom": 420, "top": 200})
    cx, cw = 1960, W - M - 1960
    out = [t("Inter700", cx, 560, "FIG. 05 — ANATOMY", 40, c["accent"], ls=14)]
    muscles = [("DELTOID", "shoulder abduction"), ("BICEPS BRACHII", "elbow flexion"),
               ("LATISSIMUS DORSI", "shoulder extension"), ("EXTERNAL OBLIQUE", "trunk rotation"),
               ("GLUTEUS MAXIMUS", "hip extension"), ("QUADRICEPS FEMORIS", "knee extension"),
               ("GASTROCNEMIUS", "plantar flexion")]
    y = 720
    for i, (name, action) in enumerate(muscles, 1):
        out.append(f'<line x1="{cx}" y1="{y - 100}" x2="{cx + cw}" y2="{y - 100}" stroke="{c["ink"]}" stroke-width="2" opacity="0.18"/>')
        out.append(t("Anton", cx, y + 30, f"{i:02d}", 96, c["accent"]))
        out.append(t("Inter700", cx + 150, y - 8, name, 48, c["ink"], ls=4))
        out.append(t("PlayfairItalic", cx + 150, y + 62, action, 50, c["muted"]))
        y += 330
    head = "FORM OVER COMFORT."
    hs = fit("Anton", [head], W - 2 * M, 420)
    hy = 3330 + cap_ratio("Anton") * hs
    out.append(t("Anton", M - 6, hy, "FORM OVER", hs, c["ink"]))
    out.append(t("Anton", M - 6 + text_w("Anton", "FORM OVER ", hs), hy, "COMFORT.", hs, c["accent"]))
    out.append(t("Inter500", M, hy + 130, "Train the body like a doctor would: precisely, patiently, for life.", 54, c["ink"], opacity=0.8))
    return svg("dark", 5, defs, photo + f'<g id="type">{"".join(out)}</g>')






def p06():
    return split_poster(6, "light", "images/06-bruce-lee.jpg", "left",
                        ["BE", "WATER,", "MY", "FRIEND."], {1}, "ON ADAPTING",
                        "Empty your mind. Be formless, shapeless — like water.", "BRUCE LEE")


def p07():
    """No photo: a prescription pad, signed."""
    c = THEMES["dark"]
    a, ink, muted = c["accent"], c["ink"], c["muted"]
    out = [t("Inter700", M, 420, "PRESCRIPTION  ·  VALID FOR LIFE", 44, a, ls=16)]
    lines = ["DOCTOR’S", "ORDERS."]
    hs = fit("Anton", lines, 1900, 560)
    hy = 520 + cap_ratio("Anton") * hs
    out.append(t("Anton", M - 8, hy, lines[0], hs, ink))
    out.append(t("Anton", M - 8, hy + hs * 0.98, lines[1], hs, a))
    out.append(t("PlayfairItalic", W - M, hy + hs * 0.98, "Rx", 720, a, anchor="end"))
    fy = hy + hs * 0.98 + 230
    for label, value, x0, x1 in [("PATIENT", "You", M, 1420), ("DATE", "Every single day", 1560, W - M)]:
        out.append(t("Inter700", x0, fy, label, 38, muted, ls=12))
        out.append(t("PlayfairItalic", x0 + text_w("Inter700", label, 38, 12) + 50, fy, value, 72, ink))
        out.append(f'<line x1="{x0}" y1="{fy + 40}" x2="{x1}" y2="{fy + 40}" stroke="{ink}" stroke-width="3" opacity="0.5"/>')
    orders = [("LIFT HEAVY", "3× a week, progressive overload"), ("WALK", "8,000+ steps, daily"),
              ("PROTEIN", "1.6 g per kg body weight, daily"), ("SLEEP", "7–9 hours, nightly"),
              ("MOBILITY", "10 minutes, daily"), ("REPEAT", "for life · refills unlimited")]
    oy = fy + 330
    for i, (name, dose) in enumerate(orders, 1):
        out.append(t("Anton", M, oy, f"{i:02d}", 110, a))
        out.append(t("Anton", M + 200, oy, name, 130, ink))
        nx = M + 200 + text_w("Anton", name, 130) + 40
        dx = W - M - text_w("PlayfairItalic", dose, 66) - 40
        out.append(f'<line x1="{nx:.0f}" y1="{oy - 8}" x2="{dx:.0f}" y2="{oy - 8}" stroke="{ink}" stroke-width="5" stroke-dasharray="2 22" stroke-linecap="round" opacity="0.45"/>')
        out.append(t("PlayfairItalic", W - M, oy, dose, 66, ink, anchor="end", opacity=0.85))
        oy += 245
    sy = 3700
    out.append(t("PlayfairItalic", M, sy - 40, "Dr. Mohan Babu", 120, ink))
    out.append(f'<line x1="{M}" y1="{sy}" x2="{M + 1050}" y2="{sy}" stroke="{ink}" stroke-width="3" opacity="0.6"/>')
    out.append(t("Inter700", M, sy + 70, "SIGNATURE  ·  MBBS", 36, muted, ls=12))
    # rubber stamp
    sx, scy, r = W - M - 230, 3560, 210
    stamp = (f'<g id="stamp" transform="rotate(-12 {sx} {scy})" opacity="0.85">'
             f'<path id="stamp-arc" d="M{sx - r + 50} {scy}a{r - 50} {r - 50} 0 1 1 {2 * (r - 50)} 0a{r - 50} {r - 50} 0 1 1 {-2 * (r - 50)} 0" fill="none"/>'
             f'<circle cx="{sx}" cy="{scy}" r="{r}" fill="none" stroke="{a}" stroke-width="8"/>'
             f'<circle cx="{sx}" cy="{scy}" r="{r - 100}" fill="none" stroke="{a}" stroke-width="4"/>'
             f'<text font-family="Inter, sans-serif" font-weight="700" font-size="34" letter-spacing="7" fill="{a}">'
             f'<textPath href="#stamp-arc" xlink:href="#stamp-arc">DOC BEYOND THE BARBELL • APPROVED •</textPath></text>'
             + t("Anton", sx, scy + 40, "Rx", 110, a, anchor="middle") + '</g>')
    return svg("dark", 7, "", f'<g id="type">{"".join(out)}</g>{stamp}')






POSTERS = {
    "01-goggins": p01, "02-tyson": p02, "03-strength-is-medicine": p03, "04-bannister": p04,
    "05-form-over-comfort": p05, "06-bruce-lee": p06, "07-doctors-orders": p07,
}

if __name__ == "__main__":
    for name, fn in POSTERS.items():
        (HERE / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", f"{name}.svg")
