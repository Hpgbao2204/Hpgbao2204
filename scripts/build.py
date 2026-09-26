#!/usr/bin/env python3
"""Generates the animated SVGs in assets/ and README.md from scripts/content.py.

All text is converted to outlines with fontTools so the SVGs render identically
everywhere (GitHub serves README images without web fonts or scripts), and all
3D motion is pre-computed here and played back with SMIL / CSS keyframes.

    pip install fonttools brotli
    python3 scripts/build.py
"""
import math
import os
from html import escape
from urllib.parse import quote_plus

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "scripts", "fonts")
ASSETS = os.path.join(ROOT, "assets")

W = 1200
PAL = dict(
    bg="#131211", panel="#1a1917", line="#2d2a27", dim="#4a4640", fg="#f5f2ec",
    muted="#8f8a82", red="#ff4b4b", orange="#ff8f42", yellow="#ffc730",
    lime="#c8ff3d", green="#18ff74", teal="#00e5c8", blue="#3d8bff",
    violet="#a26bff", pink="#ff4fa3",
)
RAINBOW = ["yellow", "orange", "red", "pink", "violet", "blue", "teal", "lime"]
KIND_COLOR = dict(journal="yellow", conference="blue", article="pink")


def fmt(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    ra, rb = hex2rgb(PAL.get(a, a)), hex2rgb(PAL.get(b, b))
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ra, rb))


def col(name):
    return PAL.get(name, name)


# --------------------------------------------------------------------- text --

# Glyph outlines are emitted once per SVG into <defs> and placed with <use>.
DEFS = {}


class Font:
    def __init__(self, key, file):
        self.key = key
        self.t = TTFont(os.path.join(FONTS, file))
        self.gs = self.t.getGlyphSet()
        self.cmap = self.t.getBestCmap()
        self.upm = self.t["head"].unitsPerEm
        self.hm = self.t["hmtx"].metrics

    def gname(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap[ord("?")]

    def adv(self, ch, size):
        return self.hm[self.gname(ch)][0] * size / self.upm

    def width(self, s, size, track=0):
        return sum(self.adv(c, size) for c in s) + track * max(len(s) - 1, 0)

    def ref(self, ch, size):
        """Id of this glyph at this size, registering its outline in DEFS."""
        gid = f"{self.key}{fmt(size).replace('.', '_')}-{self.gname(ch)}"
        if gid not in DEFS:
            pen = SVGPathPen(self.gs, ntos=fmt)
            k = size / self.upm
            self.gs[self.gname(ch)].draw(TransformPen(pen, (k, 0, 0, -k, 0, 0)))
            DEFS[gid] = f'<path id="{gid}" d="{pen.getCommands()}"/>'
        return gid

    def glyphs(self, s, size, x, y, anchor="start", track=0):
        """[(char, <use> tag, x, advance)] for every non-space glyph."""
        w = self.width(s, size, track)
        x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
        out = []
        for ch in s:
            a = self.adv(ch, size)
            if ch != " ":
                out.append((ch, f'href="#{self.ref(ch, size)}" x="{fmt(x)}" y="{fmt(y)}"', x, a))
            x += a + track
        return out

    def wrap(self, s, size, maxw):
        lines, cur = [], ""
        for word in s.split():
            test = (cur + " " + word).strip()
            if cur and self.width(test, size) > maxw:
                lines.append(cur)
                cur = word
            else:
                cur = test
        return lines + ([cur] if cur else [])


DISPLAY = Font("d", "unbounded-latin-800-normal.woff2")
SANS = Font("s", "space-grotesk-latin-700-normal.woff2")
SANS_M = Font("t", "space-grotesk-latin-500-normal.woff2")
MONO = Font("m", "jetbrains-mono-latin-400-normal.woff2")
MONO_B = Font("b", "jetbrains-mono-latin-700-normal.woff2")


def text(font, s, size, x, y, fill="fg", anchor="start", track=0, attrs=""):
    uses = "".join(f"<use {g[1]}/>" for g in font.glyphs(s, size, x, y, anchor, track))
    return f'<g fill="{col(fill)}" {attrs}>{uses}</g>'


def arrow(x, y, s, color, sw=2.4):
    """North-east arrow in a box of size s with its bottom-left corner at (x, y)."""
    return (f'<path d="M{fmt(x)} {fmt(y)}L{fmt(x + s)} {fmt(y - s)}M{fmt(x + s * .3)} {fmt(y - s)}'
            f'H{fmt(x + s)}V{fmt(y - s * .3)}" fill="none" stroke="{col(color)}" '
            f'stroke-width="{sw}" stroke-linecap="square"/>')


# ----------------------------------------------------------------------- 3D --

PHI = (1 + 5 ** .5) / 2


def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def _cyc(v):
    a, b, c = v
    return [(a, b, c), (b, c, a), (c, a, b)]


def _signs(v):
    out = {v}
    for i in range(3):
        out |= {tuple(-c if j == i else c for j, c in enumerate(p)) for p in out}
    return sorted(out)


def solid(name):
    if name == "tetra":
        vs = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    elif name == "cube":
        vs = _signs((1, 1, 1))
    elif name == "octa":
        vs = [p for i in range(3) for p in _signs(tuple(1 if j == i else 0 for j in range(3)))]
    elif name == "ico":
        vs = sorted({p for s in _signs((0, 1, PHI)) for p in _cyc(s)})
    elif name == "dodeca":
        vs = _signs((1, 1, 1)) + sorted({p for s in _signs((0, 1 / PHI, PHI)) for p in _cyc(s)})
    else:
        raise ValueError(name)
    vs = [_norm(v) for v in sorted(set(vs))]
    d2 = lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b))
    m = min(d2(a, b) for i, a in enumerate(vs) for b in vs[i + 1:])
    edges = [(i, j) for i in range(len(vs)) for j in range(i + 1, len(vs))
             if abs(d2(vs[i], vs[j]) - m) < 1e-6]
    adj = {i: set() for i in range(len(vs))}
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)
    faces = []
    if name in ("tetra", "octa", "ico"):
        faces = [(i, j, k) for i, j in edges for k in adj[i] & adj[j] if k > j]
    elif name == "cube":
        for axis in range(3):
            for sgn in (-1, 1):
                f = [i for i, v in enumerate(vs) if v[axis] * sgn > 0]
                c = [sum(vs[i][a] for i in f) / 4 for a in range(3)]
                u, w = [(axis + 1) % 3, (axis + 2) % 3]
                f.sort(key=lambda i: math.atan2(vs[i][w] - c[w], vs[i][u] - c[u]))
                faces.append(tuple(f))
    return vs, edges, faces


def rot(ax, ay, az):
    ca, sa, cb, sb, cc, sc = (math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay),
                              math.cos(az), math.sin(az))
    rx = ((1, 0, 0), (0, ca, -sa), (0, sa, ca))
    ry = ((cb, 0, sb), (0, 1, 0), (-sb, 0, cb))
    rz = ((cc, -sc, 0), (sc, cc, 0), (0, 0, 1))
    mm = lambda a, b: tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
                            for i in range(3))
    return mm(rz, mm(rx, ry))


def apply(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


CAM = 4.2


def project(v, cx, cy, r):
    f = CAM / (CAM - v[2])
    return cx + v[0] * r * f, cy - v[1] * r * f


def motion(t, tilt=0.45, wob=0.18, turns=1, phase=0.0):
    a = 2 * math.pi * t
    return rot(tilt + wob * math.sin(a + phase), turns * a + phase, 0.12 * math.sin(2 * a + phase))


def smil(attr, vals, dur, discrete=False, begin="0s"):
    vals = list(vals) + [vals[0]] if not discrete else list(vals)
    mode = ' calcMode="discrete"' if discrete else ""
    return (f'<animate attributeName="{attr}" dur="{dur}s" begin="{begin}" repeatCount="indefinite"'
            f'{mode} values="{";".join(vals)}"/>')


def wire(name, cx, cy, r, color, dur=12, frames=60, sw=2, opacity=1.0, reverse=False, **mo):
    vs, edges, _ = solid(name)
    ds = []
    for f in range(frames):
        t = f / frames
        m = motion(1 - t if reverse else t, **mo)
        p = [project(apply(m, v), cx, cy, r) for v in vs]
        ds.append("".join(f"M{fmt(p[i][0])} {fmt(p[i][1])}L{fmt(p[j][0])} {fmt(p[j][1])}"
                          for i, j in edges))
    return (f'<path d="{ds[0]}" fill="none" stroke="{col(color)}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round" opacity="{opacity}">'
            f'{smil("d", ds, dur)}</path>')


SUNSET = [(0, "#2a1650"), (.22, "violet"), (.42, "pink"), (.58, "red"), (.74, "orange"),
          (.88, "yellow"), (1, "#fff4c9")]


def ramp(t, stops=SUNSET):
    t = min(1.0, max(0.0, t))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if t <= b:
            return mix(ca, cb, (t - a) / (b - a))
    return col(stops[-1][1])


def gem(name, cx, cy, r, dur=16, frames=72, gap="bg", **mo):
    """Solid, toon-shaded convex polyhedron with back-face culling."""
    vs, _, faces = solid(name)
    light = _norm((-0.45, 0.65, 0.75))
    out = []
    for fi, face in enumerate(faces):
        jitter = ((fi * 7) % 5 - 2) * .035
        n0 = _norm(tuple(sum(vs[i][a] for i in face) for a in range(3)))
        ds, fills, vis = [], [], []
        for f in range(frames):
            m = motion(f / frames, **mo)
            rv = [apply(m, vs[i]) for i in face]
            n = apply(m, n0)
            c = tuple(sum(v[a] for v in rv) / len(rv) for a in range(3))
            view = _norm((-c[0], -c[1], CAM - c[2]))
            facing = sum(a * b for a, b in zip(n, view))
            lam = max(0.0, sum(a * b for a, b in zip(n, light)))
            p = [project(v, cx, cy, r) for v in rv]
            ds.append("M" + "L".join(f"{fmt(x)} {fmt(y)}" for x, y in p) + "Z")
            fills.append(ramp(.08 + lam * .92 + jitter))
            vis.append("1" if facing > 0.02 else "0")
        out.append(f'<path d="{ds[0]}" fill="{fills[0]}" stroke="{col(gap)}" stroke-width="3" '
                   f'stroke-linejoin="round">{smil("d", ds, dur)}{smil("fill", fills, dur)}'
                   f'{smil("opacity", vis, dur, discrete=True)}</path>')
    return "".join(out)


# -------------------------------------------------------------------- frame --

BASE_CSS = """
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
.o { transform-box: fill-box; transform-origin: center; }
"""


def svg(w, h, body, css="", label="", bg=True, radius=22):
    back = (f'<rect width="{w}" height="{h}" rx="{radius}" fill="{PAL["bg"]}"/>'
            f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{radius}" fill="none" '
            f'stroke="{PAL["line"]}" stroke-width="1.5"/>') if bg else ""
    defs = "".join(DEFS.values())
    DEFS.clear()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><style>{BASE_CSS}{css}</style>'
            f'<defs>{defs}</defs>{back}{body}</svg>\n')


def save(name, data):
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(data)
    print(f"  assets/{name:<22} {len(data) / 1024:7.1f} KB")


def section_header(num, title, accent, variant, right_label=""):
    """Numbered heading used at the top of each section card (100px tall)."""
    y = 74
    body = [text(DISPLAY, num, 44, 48, y, "none", attrs=f'stroke="{col(accent)}" stroke-width="1.6"')]
    nx = 48 + DISPLAY.width(num, 44) + 22
    body.append(f'<rect x="{fmt(nx)}" y="{y - 30}" width="14" height="14" fill="{col(accent)}" '
                f'class="o hs"/>')
    body.append(text(DISPLAY, title, 30, nx + 34, y - 2, "fg", track=1))
    if right_label:
        body.append(text(MONO, right_label, 15, W - 48, y - 4, "muted", anchor="end"))
    css = """
.hs { animation: hs 3.2s cubic-bezier(.7,0,.3,1) infinite; }
@keyframes hs { 0%,20% { transform: rotate(0) } 50%,70% { transform: rotate(180deg) scale(.6) } 100% { transform: rotate(360deg) } }
"""
    # right-side mini animation, anime.js stagger style
    x0 = W - 48 - (MONO.width(right_label, 15) + 40 if right_label else 0)
    n = 9
    if variant == "squares":
        for i in range(n):
            x = x0 - (n - i) * 26
            c = col(RAINBOW[i % len(RAINBOW)])
            body.append(f'<rect x="{x}" y="{y - 24}" width="16" height="16" rx="3" fill="{c}" '
                        f'class="o sq" style="animation-delay:{i * .09:.2f}s"/>')
        css += """
.sq { animation: sq 2.8s cubic-bezier(.5,0,.2,1) infinite; }
@keyframes sq { 0%,55%,100% { transform: none } 25% { transform: translateY(-14px) rotate(180deg) scale(.7) } }
"""
    elif variant == "bars":
        for i in range(n):
            x = x0 - (n - i) * 18
            body.append(f'<rect x="{x}" y="{y - 36}" width="10" height="36" rx="2" fill="{col(accent)}" '
                        f'class="bar" style="animation-delay:{i * .11:.2f}s"/>')
        css += """
.bar { transform-box: fill-box; transform-origin: 50% 100%; animation: bar 1.8s ease-in-out infinite; }
@keyframes bar { 0%,100% { transform: scaleY(.2) } 50% { transform: scaleY(1) } }
"""
    elif variant == "dots":
        for i in range(n):
            x = x0 - (n - i) * 24 + 8
            body.append(f'<circle cx="{x}" cy="{y - 16}" r="7" fill="{col(accent)}" class="o dt" '
                        f'style="animation-delay:{i * .1:.2f}s"/>')
        css += """
.dt { animation: dt 2.4s cubic-bezier(.4,0,.2,1) infinite; }
@keyframes dt { 0%,60%,100% { transform: none; opacity: .35 } 25% { transform: translateY(-16px) scale(1.25); opacity: 1 } }
"""
    elif variant == "wire":
        body.append(wire("octa", x0 - 40, y - 18, 30, accent, dur=8, frames=48, sw=2))
        body.append(wire("cube", x0 - 110, y - 18, 22, "muted", dur=10, frames=48, sw=1.5, reverse=True))
    body.append(f'<path d="M48 {y + 24}H{W - 48}" stroke="{PAL["line"]}" stroke-width="1.5"/>')
    return "".join(body), css


# ------------------------------------------------------------------- header --

def build_header():
    h = 560
    cx, cy = 948, 282
    css = []
    body = []

    # stagger ripple dot-grid, rippling out from the gem
    body.append(f'<defs><radialGradient id="fade" cx="{cx / W:.3f}" cy="{cy / h:.3f}" r=".62">'
                '<stop offset="0" stop-color="#fff" stop-opacity="1"/>'
                '<stop offset=".75" stop-color="#fff" stop-opacity=".18"/>'
                '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
                f'<mask id="m"><rect width="{W}" height="{h}" fill="url(#fade)"/></mask>'
                f'<clipPath id="card"><rect width="{W}" height="{h}" rx="22"/></clipPath></defs>')
    dots, rings = [], set()
    for gy in range(18, h, 30):
        for gx in range(18, W, 30):
            k = int(math.hypot(gx - cx, gy - cy) / 30)
            rings.add(k)
            dots.append(f'<circle cx="{gx}" cy="{gy}" r="1.8" class="o d r{k}"/>')
    body.append(f'<g mask="url(#m)" clip-path="url(#card)">{"".join(dots)}</g>')
    css.append(f"""
.d {{ fill: {PAL['dim']}; animation: rip 4.8s cubic-bezier(.4,0,.2,1) infinite; }}
@keyframes rip {{ 0%,26%,100% {{ transform: scale(1); fill: {PAL['dim']} }} 9% {{ transform: scale(2.3); fill: {PAL['yellow']} }} }}
""" + "".join(f".r{k}{{animation-delay:{k * .085:.3f}s}}" for k in sorted(rings)))

    # 3D: outer wire shell, orbit rings (split front/back), solid gem
    R = 132
    shell = wire("dodeca", cx, cy, R * 1.55, "line", dur=30, frames=60, sw=1.4, reverse=True,
                 tilt=0.2, wob=0.1)
    orbit_back, orbit_front = [], []
    for ri, (tx, tz, rr, color, n, speed) in enumerate(
            [(1.18, 0.35, 1.42, "red", 7, 1), (1.32, -0.6, 1.62, "teal", 9, -1)]):
        m = rot(tx, 0, tz)
        pts = []
        for s in range(121):
            th = 2 * math.pi * s / 120
            v = apply(m, (rr * math.cos(th), 0, rr * math.sin(th)))
            pts.append((project(v, cx, cy, R), v[2]))
        for front, bucket in ((False, orbit_back), (True, orbit_front)):
            seg, segs = [], []
            for p, z in pts:
                if (z >= 0) == front:
                    seg.append(p)
                elif seg:
                    segs.append(seg)
                    seg = []
            if seg:
                segs.append(seg)
            for sg in segs:
                if len(sg) > 1:
                    d = "M" + "L".join(f"{fmt(x)} {fmt(y)}" for x, y in sg)
                    bucket.append(f'<path d="{d}" fill="none" stroke="{col(color)}" stroke-width="1.6" '
                                  f'opacity="{.9 if front else .35}"/>')
        frames, dur = 90, 18
        for k in range(n):
            xs, ys, rs, zs = [], [], [], []
            for f in range(frames):
                th = 2 * math.pi * (k / n + speed * f / frames)
                v = apply(m, (rr * math.cos(th), 0, rr * math.sin(th)))
                x, y = project(v, cx, cy, R)
                xs.append(fmt(x))
                ys.append(fmt(y))
                rs.append(fmt((4.2 if k % 3 else 6.5) * CAM / (CAM - v[2])))
                zs.append(v[2])
            node_color = col(color) if k % 3 else PAL["fg"]
            for front, bucket in ((False, orbit_back), (True, orbit_front)):
                vis = ["1" if (z >= 0) == front else "0" for z in zs]
                bucket.append(
                    f'<circle cx="{xs[0]}" cy="{ys[0]}" r="{rs[0]}" fill="{node_color}" '
                    f'opacity="{vis[0]}">{smil("cx", xs, dur)}{smil("cy", ys, dur)}'
                    f'{smil("r", rs, dur)}{smil("opacity", vis, dur, discrete=True)}</circle>')
    solid_gem = gem("ico", cx, cy, R, dur=16, frames=72)
    body.append(f'<g class="float">{shell}{"".join(orbit_back)}{solid_gem}{"".join(orbit_front)}</g>')
    css.append("""
.float { animation: float 7s ease-in-out infinite; }
@keyframes float { 0%,100% { transform: translateY(-6px) } 50% { transform: translateY(8px) } }
""")

    # left: label, name with staggered entrance + looping wave, typing tagline
    x = 64
    body.append(f'<circle cx="{x + 6}" cy="96" r="6" fill="{PAL["green"]}" class="o blink"/>')
    body.append(text(MONO, f"0x2204 · {C.ROLE.upper()}", 16, x + 22, 102, "muted", track=.6))
    css.append("""
.blink { animation: blink 1.6s steps(1) infinite; }
@keyframes blink { 50% { opacity: .15 } }
.l { transform-box: fill-box; transform-origin: 50% 100%;
     animation: rise 1.1s cubic-bezier(.2,1.5,.4,1) both, hop 7s cubic-bezier(.5,0,.3,1) infinite; }
@keyframes rise { from { transform: translateY(70px) scaleY(.4); opacity: 0 } to { transform: none; opacity: 1 } }
@keyframes hop { 0%,82%,100% { transform: none } 88% { transform: translateY(-18px) } 94% { transform: translateY(3px) scaleY(.94) } }
""")
    i = 0
    for word, y, fill in ((C.NAME_TOP, 236, "fg"), (C.NAME_BOTTOM, 372, "yellow")):
        for ch, d, gx, a in DISPLAY.glyphs(word, 132, x - 4, y, track=-2):
            body.append(f'<use {d} fill="{col(fill)}" class="l" '
                        f'style="animation-delay:{.15 + i * .07:.2f}s,{1.4 + i * .09:.2f}s"/>')
            i += 1
    # accent square after the first word, like a full stop
    ex = x - 4 + DISPLAY.width(C.NAME_TOP, 132, -2) + 14
    body.append(f'<rect x="{fmt(ex)}" y="206" width="30" height="30" fill="{PAL["red"]}" class="o stop"/>')
    css.append("""
.stop { animation: stop 3.6s cubic-bezier(.7,0,.3,1) infinite; }
@keyframes stop { 0%,40% { transform: none } 55% { transform: rotate(90deg) scale(.55) } 70%,100% { transform: rotate(180deg) } }
""")

    # typewriter carousel
    ty, size = 438, 24
    n = len(C.TAGLINES)
    period = 3.4
    total = n * period
    prompt_w = MONO.width("> ", size)
    body.append(text(MONO_B, ">", size, x, ty, "green"))
    for k, phrase in enumerate(C.TAGLINES):
        w = MONO.width(phrase, size)
        a = k / n * 100
        b = (k + 1) / n * 100
        typ = a + 1.1 / total * 100
        era = b - .45 / total * 100
        css.append(f"""
.ph{k} {{ animation: ph{k} {total}s linear infinite; }}
@keyframes ph{k} {{ 0%,{a:.2f}% {{ opacity: 0 }} {a + .01:.2f}%,{b - .01:.2f}% {{ opacity: 1 }} {b:.2f}%,100% {{ opacity: 0 }} }}
.tw{k} {{ animation: tw{k} {total}s infinite; }}
@keyframes tw{k} {{
  0%,{a:.2f}% {{ transform: translateX(-{w + 4:.1f}px); animation-timing-function: steps({len(phrase)}) }}
  {typ:.2f}%,{era:.2f}% {{ transform: none; animation-timing-function: steps({len(phrase)}) }}
  {b:.2f}%,100% {{ transform: translateX(-{w + 4:.1f}px) }} }}
""")
        body.append(
            f'<clipPath id="c{k}"><rect x="{fmt(x + prompt_w)}" y="{ty - 30}" width="{fmt(w + 4)}" '
            f'height="40" class="tw{k}"/></clipPath>'
            f'<g class="ph{k}"><g clip-path="url(#c{k})">'
            f'{text(MONO, phrase, size, x + prompt_w, ty, "fg")}</g>'
            f'<g class="tw{k}"><rect x="{fmt(x + prompt_w + w + 4)}" y="{ty - 22}" width="13" height="26" '
            f'fill="{PAL["yellow"]}" class="blink"/></g></g>')

    # chips
    cxp = x
    for label, color in ((C.AFFILIATION, "yellow"), (C.LOCATION, "teal"),
                         (f"{len(C.PUBLICATIONS)} PAPERS", "red")):
        label = label.upper()
        w = MONO.width(label, 14, .5) + 34
        body.append(f'<rect x="{cxp}" y="474" width="{fmt(w)}" height="34" rx="17" fill="none" '
                    f'stroke="{PAL["line"]}" stroke-width="1.5"/>'
                    f'<circle cx="{cxp + 17}" cy="491" r="4" fill="{col(color)}"/>'
                    + text(MONO, label, 14, cxp + 28, 496, "fg", track=.5))
        cxp += w + 10

    # corner annotations
    body.append(text(MONO, "fig.01 - icosahedron / 20 faces / 2 relay rings", 12, W - 40, h - 30,
                     "dim", anchor="end", track=.4))
    body.append(text(MONO, "v2026.09", 12, W - 40, 42, "dim", anchor="end", track=.4))
    save("header.svg", svg(W, h, "".join(body), "".join(css),
                           f"{C.FULL_NAME} - {C.ROLE}"))


# -------------------------------------------------------------------- links --

def build_links():
    for label, url, color in C.LINKS:
        w, h, depth = 280, 76, 8
        fw = SANS.width(label, 19, .6)
        body = (f'<rect x="4" y="{8 + depth}" width="{w - 8}" height="{h - 18 - depth + 2}" rx="14" '
                f'fill="{mix(color, "bg", .55)}"/>'
                f'<g class="k"><rect x="4" y="8" width="{w - 8}" height="{h - 18 - depth + 2}" rx="14" '
                f'fill="{col(color)}"/>'
                + text(SANS, label, 19, (w - 26) / 2, 8 + (h - 16 - depth) / 2 + 7, "bg",
                       anchor="middle", track=.6)
                + arrow((w - 26) / 2 + fw / 2 + 10, 8 + (h - 16 - depth) / 2 + 7, 12, "bg")
                + '</g>')
        css = """
.k { animation: k 4s cubic-bezier(.5,0,.2,1) infinite; }
@keyframes k { 0%,70%,100% { transform: none } 78% { transform: translateY(6px) } 86% { transform: none } }
"""
        save(f"link-{label.split()[-1].lower()}.svg",
             svg(w, h, body, css, f"{label}", bg=False))


# -------------------------------------------------------------------- about --

def build_about():
    h = 668
    head, css = section_header("01", "ABOUT", "yellow", "squares", "whoami --verbose")
    body = [head]

    # pseudo-contract, lines revealed with a stagger
    x, y0, lh, size = 48, 166, 34, 19
    cw = MONO.width("m", size)
    tw = max(len(t) for t, _, _ in C.ABOUT)
    fw = max(len(f) for _, f, _ in C.ABOUT)
    lines = [[("contract ", "violet"), (C.FULL_NAME.replace(" ", ""), "yellow"), (" {", "fg")]]
    for typ, field, val in C.ABOUT:
        vcol = "green" if val.startswith('"') else ("orange" if val[0].isdigit() else "fg")
        lines.append([("    " + typ.ljust(tw) + " ", "blue"), (field.ljust(fw), "fg"),
                      (" = ", "muted"), (val, vcol), (";", "muted")])
    lines.append([("", "fg")])
    lines.append([("    function ", "violet"), ("motto", "yellow"), ("() ", "fg"), ("pure ", "violet"),
                  ("returns ", "violet"), ("(string) {", "fg")])
    lines.append([("        return ", "violet"), (f'"{C.MOTTO}"', "green"), (";", "muted")])
    lines.append([("    }", "fg")])
    lines.append([("}", "fg")])
    for i, parts in enumerate(lines):
        y = y0 + i * lh
        body.append(text(MONO, f"{i + 1:>2}", 14, x, y - 2, "dim"))
        cx = x + 40
        g = []
        for s, c in parts:
            if s.strip():
                g.append(text(MONO, s, size, cx, y, c))
            cx += cw * len(s)
        body.append(f'<g class="ln" style="animation-delay:{.2 + i * .08:.2f}s">{"".join(g)}</g>')
    css += """
.ln { animation: ln .8s cubic-bezier(.2,.9,.3,1) both; }
@keyframes ln { from { transform: translateX(-24px); opacity: 0 } to { transform: none; opacity: 1 } }
"""

    # right: floating isometric layer stack, one slab per focus area
    ox, oy = 872, 146
    sw, sd, th = 118, 118, 24
    iso = lambda u, v, z: (ox + (u - v) * .866, oy + (u + v) * .5 - z)
    colors = ["yellow", "red", "blue", "lime"]
    slabs = []
    for i, (label, c) in enumerate(zip(C.FOCUS, colors)):
        z = -i * 58
        top = [iso(0, 0, z), iso(sw, 0, z), iso(sw, sd, z), iso(0, sd, z)]
        left = [iso(0, sd, z), iso(sw, sd, z), iso(sw, sd, z - th), iso(0, sd, z - th)]
        right = [iso(sw, 0, z), iso(sw, sd, z), iso(sw, sd, z - th), iso(sw, 0, z - th)]
        P = lambda pts: "M" + "L".join(f"{fmt(a)} {fmt(b)}" for a, b in pts) + "Z"
        lx, ly = iso(sw, 0, z - th / 2)
        slabs.append(
            f'<g class="slab" style="animation-delay:{i * .22:.2f}s">'
            f'<path d="{P(left)}" fill="{mix(c, "bg", .45)}"/>'
            f'<path d="{P(right)}" fill="{mix(c, "bg", .2)}"/>'
            f'<path d="{P(top)}" fill="{col(c)}" stroke="{PAL["bg"]}" stroke-width="1.5"/>'
            f'<path d="M{fmt(lx + 8)} {fmt(ly)}H{fmt(lx + 28)}" stroke="{PAL["dim"]}" stroke-width="1.5"/>'
            + text(MONO, label.upper(), 14, lx + 36, ly + 5, "fg", track=.3)
            + text(MONO, f"L{i}", 12, *iso(sw * .5, sd * .5, z), "bg", anchor="middle")
            + '</g>')
    body.append("".join(reversed(slabs)))
    css += """
.slab { animation: slab 5s cubic-bezier(.5,0,.3,1) infinite; }
@keyframes slab { 0%,100% { transform: none } 30% { transform: translateY(-12px) } 55% { transform: translateY(2px) } }
"""

    # metrics as rolling odometers
    kinds = [p["kind"] for p in C.PUBLICATIONS]
    metrics = [(len(C.PUBLICATIONS), "PUBLICATIONS", "yellow"),
               (kinds.count("journal"), "JOURNAL ARTICLES", "red"),
               (kinds.count("conference"), "CONFERENCE PAPERS", "blue"),
               (C.CITATIONS, "CITATIONS", "lime")]
    my = 568
    body.append(f'<path d="M48 {my - 78}H{W - 48}" stroke="{PAL["line"]}" stroke-width="1.5" '
                'stroke-dasharray="2 6"/>')
    cellw = (W - 96) / 4
    dh, dsize = 72, 64
    for mi, (val, label, c) in enumerate(metrics):
        mx = 48 + mi * cellw
        digits = f"{val:02d}"
        dx = mx
        for di, dg in enumerate(digits):
            target = 10 + int(dg)
            dw = DISPLAY.width(dg, dsize)
            col_paths = "".join(text(DISPLAY, str(n % 10), dsize, dx + dw / 2, my + n * dh, c, anchor="middle")
                                for n in range(target + 1))
            body.append(f'<clipPath id="od{mi}{di}"><rect x="{fmt(dx - 4)}" y="{my - dsize - 4}" '
                        f'width="{fmt(dw + 8)}" height="{dsize + 16}"/></clipPath>'
                        f'<g clip-path="url(#od{mi}{di})"><g class="od{mi}{di}">{col_paths}</g></g>')
            css += (f".od{mi}{di} {{ animation: od{mi}{di} 2.6s cubic-bezier(.7,0,.1,1) "
                    f"{.4 + mi * .18 + di * .12:.2f}s both; }}"
                    f"@keyframes od{mi}{di} {{ from {{ transform: none }} to "
                    f"{{ transform: translateY(-{target * dh}px) }} }}")
            dx += dw + 2
        if label == "CITATIONS":
            body.append(text(DISPLAY, "+", 34, dx + 4, my - 30, c))
        body.append(f'<rect x="{fmt(mx)}" y="{my + 26}" width="10" height="10" fill="{col(c)}"/>')
        body.append(text(MONO, label, 14, mx + 20, my + 36, "muted", track=.8))
    save("about.svg", svg(W, h, "".join(body), css, f"About {C.FULL_NAME}"))


# ------------------------------------------------------------- publications --

def pub_url(p):
    return p["url"] or "https://scholar.google.com/scholar?q=" + quote_plus(f'"{p["title"]}"')


def build_publications():
    years = sorted({p["year"] for p in C.PUBLICATIONS})
    head, css = section_header("02", "PUBLICATIONS", "red", "bars",
                               f"{len(C.PUBLICATIONS)} papers · {years[0]}-{years[-1]}")
    save("sec-publications.svg", svg(W, 124, head, css, "Publications"))

    shapes = ["ico", "octa", "cube", "tetra", "dodeca"]
    for i, p in enumerate(C.PUBLICATIONS):
        accent = KIND_COLOR[p["kind"]]
        tx, maxw = 232, 790
        tsize, tlh = 29, 38
        tl = SANS.wrap(p["title"], tsize, maxw)
        y = 66
        body = []
        for li, line in enumerate(tl):
            body.append(text(SANS, line, tsize, tx, y + li * tlh, "fg"))
        y += (len(tl) - 1) * tlh + 42
        # authors, with me highlighted
        ax, asz = tx, 18
        cw = MONO.width("m", asz)
        names = [a.strip() for a in p["authors"].split(",")]
        for ni, nm in enumerate(names):
            me = nm in C.ME
            s = nm + ("," if ni < len(names) - 1 else "")
            if me:
                body.append(f'<rect x="{fmt(ax - 5)}" y="{y - 18}" width="{fmt(cw * len(nm) + 10)}" '
                            f'height="26" rx="4" fill="{mix(accent, "bg", .78)}"/>')
            body.append(text(MONO_B if me else MONO, s, asz, ax, y, accent if me else "muted"))
            ax += cw * (len(s) + 1)
        if p["venue"]:
            y += 36
            body.append(text(SANS_M, p["venue"], 19, tx, y, mix("fg", "bg", .25)))
        h = y + 44

        # left column: index, year, kind tag
        body.insert(0, f'<clipPath id="cc"><rect width="{W}" height="{h}" rx="22"/></clipPath>'
                       f'<rect width="8" height="{h}" fill="{col(accent)}" clip-path="url(#cc)"/>')
        body.append(text(MONO, f"#{i + 1:02d}", 14, 48, 44, "dim", track=.5))
        body.append(text(DISPLAY, str(p["year"]), 36, 48, 92, accent))
        tag = p["kind"].upper()
        tw = MONO.width(tag, 12, 1) + 22
        body.append(f'<rect x="48" y="110" width="{fmt(tw)}" height="26" rx="13" fill="none" '
                    f'stroke="{col(accent)}" stroke-width="1.5"/>'
                    + text(MONO, tag, 12, 48 + tw / 2, 127, accent, anchor="middle", track=1))
        # right: slowly spinning wireframe + link hint
        sx, sy = 1100, min(h / 2, 100)
        body.append(f'<circle cx="{sx}" cy="{sy}" r="58" fill="{mix(accent, "bg", .9)}"/>')
        body.append(wire(shapes[i % len(shapes)], sx, sy, 50, accent, dur=14 + i, frames=48, sw=1.8,
                         reverse=i % 2 == 1, phase=i * .7))
        hint = "DOI" if p["url"] else "SCHOLAR"
        body.append(text(MONO, hint, 13, W - 64, h - 26, "muted", anchor="end", track=1)
                    + arrow(W - 56, h - 26, 11, "muted", 2))
        css = ""
        save(f"pub-{i + 1:02d}.svg", svg(W, h, "".join(body), css, p["title"]))


# -------------------------------------------------------------------- stack --

def build_stack():
    head, css = section_header("03", "STACK", "blue", "dots", "languages · chains · tooling")
    body = [head]
    y = 150
    gi = 0
    kh, depth, gap = 54, 8, 14
    for label, color, items in C.STACK:
        body.append(f'<rect x="48" y="{y - 11}" width="10" height="10" fill="{col(color)}"/>')
        body.append(text(MONO, label, 13, 68, y, "muted", track=1))
        y += 22
        x = 48
        for it in items:
            w = SANS.width(it, 21) + 44
            if x + w > W - 48:
                x = 48
                y += kh + depth + gap
            body.append(
                f'<rect x="{fmt(x)}" y="{y + depth}" width="{fmt(w)}" height="{kh}" rx="12" '
                f'fill="{mix(color, "bg", .55)}"/>'
                f'<g class="key" style="animation-delay:{gi * .07:.2f}s">'
                f'<rect x="{fmt(x)}" y="{y}" width="{fmt(w)}" height="{kh}" rx="12" fill="{col(color)}"/>'
                + text(SANS, it, 21, x + w / 2, y + kh / 2 + 8, "bg", anchor="middle")
                + '</g>')
            x += w + gap
            gi += 1
        y += kh + depth + 40
    h = y - 4
    css += """
.key { animation: key 5s cubic-bezier(.5,0,.2,1) infinite; }
@keyframes key { 0%,12%,100% { transform: none } 4% { transform: translateY(8px) } }
"""
    save("stack.svg", svg(W, h, "".join(body), css, "Tech stack: " + ", ".join(
        it for _, _, items in C.STACK for it in items)))


def build_activity():
    head, css = section_header("04", "ACTIVITY", "lime", "wire", f"github.com/{C.GITHUB_USER}")
    save("sec-activity.svg", svg(W, 124, head, css, "GitHub activity"))


# ------------------------------------------------------------------- footer --

def build_footer():
    h = 260
    body, css = [], []
    msg = C.MOTTO.upper()
    size = 34
    glyphs = DISPLAY.glyphs(msg, size, W / 2, 104, anchor="middle", track=1)
    for i, (ch, d, gx, a) in enumerate(glyphs):
        c = RAINBOW[i % len(RAINBOW)]
        body.append(f'<use {d} fill="{PAL["fg"]}" class="w" style="animation-delay:{i * .05:.2f}s;'
                    f'--c:{col(c)}"/>')
    css.append("""
.w { transform-box: fill-box; transform-origin: 50% 100%; animation: w 4.5s cubic-bezier(.5,0,.3,1) infinite; }
@keyframes w { 0%,30%,100% { transform: none; fill: #f5f2ec } 10% { transform: translateY(-14px); fill: var(--c) } }
""")
    # a chain of blocks with a pulse travelling along it
    n, bw, gap = 16, 34, 26
    x0 = (W - (n * bw + (n - 1) * gap)) / 2
    y = 160
    body.append(f'<path d="M{fmt(x0)} {y + bw / 2}H{fmt(x0 + n * bw + (n - 1) * gap)}" '
                f'stroke="{PAL["line"]}" stroke-width="2" stroke-dasharray="4 5"/>')
    for i in range(n):
        x = x0 + i * (bw + gap)
        c = RAINBOW[i % len(RAINBOW)]
        body.append(f'<rect x="{fmt(x)}" y="{y}" width="{bw}" height="{bw}" rx="6" fill="{PAL["panel"]}" '
                    f'stroke="{PAL["dim"]}" stroke-width="1.5" class="o blk" '
                    f'style="animation-delay:{i * .12:.2f}s;--c:{col(c)}"/>')
    css.append(f"""
.blk {{ animation: blk 3.8s cubic-bezier(.5,0,.2,1) infinite; }}
@keyframes blk {{ 0%,40%,100% {{ transform: none; fill: {PAL['panel']}; stroke: {PAL['dim']} }}
  12% {{ transform: translateY(-10px) rotate(45deg) scale(.8); fill: var(--c); stroke: var(--c) }} }}
""")
    body.append(text(MONO, f"© {C.FULL_NAME.upper()} · HCMC · BLOCK #2204", 12, W / 2, h - 30,
                     "dim", anchor="middle", track=1.2))
    save("footer.svg", svg(W, h, "".join(body), "".join(css), C.MOTTO))


# ------------------------------------------------------------------- README --

def build_readme():
    u = C.GITHUB_USER
    theme = ("bg_color=131211&title_color=ffc730&text_color=f5f2ec&icon_color=ff4b4b"
             "&border_color=2d2a27&ring_color=ffc730")
    links = "\n".join(
        f'  <a href="{url}"><img src="assets/link-{label.split()[-1].lower()}.svg" width="23%" alt="{label}"/></a>'
        for label, url, _ in C.LINKS)
    pubs = "\n".join(
        f'<p><a href="{pub_url(p)}"><img src="assets/pub-{i + 1:02d}.svg" width="100%" '
        f'alt="{escape(p["title"])} ({p["year"]})"/></a></p>'
        for i, p in enumerate(C.PUBLICATIONS))
    md = f"""<!-- Generated by scripts/build.py from scripts/content.py - edit those, not this file. -->

<div align="center">

<img src="assets/header.svg" width="100%" alt="{C.FULL_NAME} - {C.ROLE}"/>

<br/>

<p>
{links}
</p>

<br/>

<img src="assets/about.svg" width="100%" alt="About: {C.ROLE} at {C.AFFILIATION}, {C.LOCATION}. Focus: {', '.join(C.FOCUS)}."/>

<br/><br/>

<p><img src="assets/sec-publications.svg" width="100%" alt="Publications"/></p>
{pubs}

<sub>Full list and citations on <a href="{C.SCHOLAR}">Google Scholar</a>.</sub>

<br/><br/>

<img src="assets/stack.svg" width="100%" alt="Tech stack"/>

<br/><br/>

<img src="assets/sec-activity.svg" width="100%" alt="GitHub activity"/>

<a href="https://github.com/{u}"><img height="170" src="https://github-readme-stats.vercel.app/api?username={u}&show_icons=true&count_private=true&include_all_commits=true&hide_border=true&border_radius=16&{theme}" alt="GitHub stats"/></a>
<a href="https://github.com/{u}"><img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username={u}&layout=compact&langs_count=8&hide_border=true&border_radius=16&{theme}" alt="Top languages"/></a>

<img height="170" src="https://streak-stats.demolab.com/?user={u}&background=131211&border=2d2a27&stroke=2d2a27&ring=ffc730&fire=ff4b4b&currStreakNum=f5f2ec&sideNums=f5f2ec&currStreakLabel=ffc730&sideLabels=8f8a82&dates=8f8a82&hide_border=true&border_radius=16" alt="GitHub streak"/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username={u}&bg_color=131211&color=f5f2ec&line=ffc730&point=ff4b4b&area=true&area_color=ffc730&hide_border=true&radius=16" alt="Contribution graph" width="100%"/>

<br/><br/>

<img src="assets/footer.svg" width="100%" alt="{C.MOTTO}"/>

<img src="https://komarev.com/ghpvc/?username={u}&style=flat-square&color=ffc730&label=VISITORS" alt="Profile views"/>

</div>
"""
    with open(os.path.join(ROOT, "README.md"), "w") as f:
        f.write(md)
    print("  README.md")


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    build_header()
    build_links()
    build_about()
    build_publications()
    build_stack()
    build_activity()
    build_footer()
    build_readme()
