"""Builds the animated SVGs of the profile README. `python3 scripts/build.py`

Fonts: Noto Serif CJK JP Black and Noto Sans CJK JP Bold (SIL OFL), subset to the characters each SVG uses and
embedded as WOFF, so every viewer sees the same type without loading anything.
"""

import base64
import io
import math
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTCollection, TTFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SERIF = ("/usr/share/fonts/noto-cjk/NotoSerifCJK-Black.ttc", 0)
SANS = ("/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc", 0)

BG, ORANGE, RED, PURPLE, GREEN, WHITE, AMBER, DIM = (
    "#0a0a0a", "#ff7a00", "#e8301c", "#7b4bc4", "#8fe33c", "#f2f2f2", "#ffb000", "#5a5a5a")

_FONTS, _BYTES = {}, {}


def _font(spec):
    if spec not in _FONTS:
        _FONTS[spec] = TTCollection(spec[0]).fonts[spec[1]]
    return _FONTS[spec]


def _bytes(spec):
    if spec not in _BYTES:
        buf = io.BytesIO()
        _font(spec).save(buf)
        _BYTES[spec] = buf.getvalue()
    return _BYTES[spec]


def face(family, spec, text):
    """A @font-face rule with the font cut down to `text`."""
    font = TTFont(io.BytesIO(_bytes(spec)))
    options = subset.Options()
    options.flavor = "woff"
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    sub = subset.Subsetter(options)
    sub.populate(text=text + " ")
    sub.subset(font)
    out = io.BytesIO()
    font.flavor = "woff"
    font.save(out)
    data = base64.b64encode(out.getvalue()).decode()
    return f"@font-face{{font-family:{family};src:url(data:font/woff;base64,{data}) format('woff')}}"


def width(spec, text, size, spacing=0):
    font = _font(spec)
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    total = sum(hmtx[cmap[ord(ch)]][0] for ch in text if ord(ch) in cmap)
    return total * size / upm + spacing * len(text)


def svg(w, h, title, style, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f"<title>{title}</title><defs>{defs}<style>{style}</style></defs>"
            f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>\n')


def hexagon(cx, cy, r):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def tape(pid, height, colour=ORANGE, speed="1.4s"):
    return (f'<pattern id="{pid}" width="40" height="{height}" patternUnits="userSpaceOnUse">'
            f'<rect width="40" height="{height}" fill="{colour}"/>'
            f'<path d="M0 {height} L{height} 0 L{height + 18} 0 L18 {height} Z" fill="{BG}"/>'
            f'<path d="M-40 {height} L{height - 40} 0 L{height - 22} 0 L-22 {height} Z" fill="{BG}"/>'
            f'<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="40 0" dur="{speed}" '
            f'repeatCount="indefinite"/></pattern>')


FLICKER = """
@keyframes flick{0%{opacity:0}8%{opacity:1}11%{opacity:.15}14%{opacity:1}17%{opacity:.4}20%,100%{opacity:1}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.15}}
@keyframes pulse{0%,100%{opacity:.08}50%{opacity:.9}}
.f{animation:flick 1.6s ease-out backwards}
"""


def header():
    texts = {
        "serif": "EPISODE:01開発者、襲来INSALATADIRISOTHEDEVELOPERARRIVES",
        "sans": "SUBJECTinsalatadirisoCLASSFULL-STACKDEVELOPERAFFILIATIONSATURDAYCOMPANYSTATUSACTIVESYNCRATIO0123456789.%:/·-",
    }
    hexes = []
    cells = [(17.3 * c + (8.66 if r % 2 else 0) + 620, 15 * r + 40) for r in range(26) for c in range(22)]
    grid = "".join(f'<path d="{hexagon(x, y, 9.5)}"/>' for x, y in cells)
    lit = [(5, 3), (6, 4), (9, 7), (12, 2), (14, 11), (3, 15), (17, 9), (8, 19), (19, 17), (11, 22), (15, 21), (2, 8)]
    for i, (c, r) in enumerate(lit):
        x, y = 17.3 * c + (8.66 if r % 2 else 0) + 620, 15 * r + 40
        hexes.append(f'<path d="{hexagon(x, y, 9.5)}" fill="{ORANGE if i % 3 else RED}" '
                     f'style="animation:pulse {2.2 + (i % 4) * 0.7:.1f}s {i * 0.37:.2f}s infinite"/>')
    style = (face("EvaSerif", SERIF, texts["serif"]) + face("EvaSans", SANS, texts["sans"]) + FLICKER + f"""
.s{{font-family:EvaSerif;fill:{WHITE}}}
.h{{font-family:EvaSans;fill:{AMBER};letter-spacing:2px}}
.grid path{{fill:none;stroke:{ORANGE};stroke-opacity:.13;stroke-width:1}}
.lit path{{opacity:.08}}
.bar{{transform-box:fill-box;transform-origin:left;animation:sync 5s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes sync{{0%{{transform:scaleX(0)}}35%{{transform:scaleX(.41)}}60%{{transform:scaleX(.88)}}75%,100%{{transform:scaleX(1)}}}}
.n1,.n2{{opacity:0}}.n1{{animation:n1 5s infinite}}.n2{{animation:n2 5s infinite}}.n3{{animation:n3 5s infinite}}
@keyframes n1{{0%,34%{{opacity:1}}35%,100%{{opacity:0}}}}
@keyframes n2{{0%,34%{{opacity:0}}35%,74%{{opacity:1}}75%,100%{{opacity:0}}}}
@keyframes n3{{0%,74%{{opacity:0}}75%,100%{{opacity:1}}}}
.dot{{animation:blink 1s steps(1) infinite}}
""")
    defs = (tape("tape", 22) + f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".35" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="m"><rect x="600" width="400" height="440" fill="url(#fade)"/></mask>')
    hud_x = 664
    body = f"""
<g mask="url(#m)"><g class="grid">{grid}</g><g class="lit">{''.join(hexes)}</g></g>
<rect width="1000" height="22" fill="url(#tape)"/><rect y="418" width="1000" height="22" fill="url(#tape)"/>
<text class="s f" x="52" y="74" font-size="22" letter-spacing="3" style="animation-delay:.1s">EPISODE:01</text>
<text class="s f" x="50" y="146" font-size="60" style="animation-delay:.45s">開発者、襲来</text>
<text class="s f" x="46" y="258" font-size="122" textLength="540" lengthAdjust="spacingAndGlyphs" style="animation-delay:.9s">INSALATA</text>
<text class="s f" x="46" y="364" font-size="122" textLength="400" lengthAdjust="spacingAndGlyphs" style="animation-delay:1.3s">DI RISO</text>
<text class="s f" x="460" y="364" font-size="18" letter-spacing="5" fill="{ORANGE}" style="animation-delay:1.8s;fill:{ORANGE}">THE DEVELOPER</text>
<text class="s f" x="460" y="390" font-size="18" letter-spacing="5" style="animation-delay:2s;fill:{ORANGE}">ARRIVES</text>
<g class="f" style="animation-delay:2.3s">
  <path d="M{hud_x} 60 H950 V300 L930 320 H{hud_x} Z" fill="{BG}" fill-opacity=".82" stroke="{ORANGE}" stroke-width="2"/>
  <path d="M{hud_x} 60 H800 L788 76 H{hud_x} Z" fill="{ORANGE}"/>
  <text class="h" x="{hud_x + 10}" y="73" font-size="11" style="fill:{BG}">SUBJECT</text>
  <text class="h" x="{hud_x + 14}" y="110" font-size="24" style="fill:{WHITE};letter-spacing:1px">insalatadiriso</text>
  <text class="h" x="{hud_x + 14}" y="142" font-size="11">CLASS</text>
  <text class="h" x="{hud_x + 114}" y="142" font-size="11" style="fill:{WHITE}">FULL-STACK DEVELOPER</text>
  <text class="h" x="{hud_x + 14}" y="164" font-size="11">AFFILIATION</text>
  <text class="h" x="{hud_x + 114}" y="164" font-size="11" style="fill:{WHITE}">SATURDAY COMPANY</text>
  <text class="h" x="{hud_x + 14}" y="186" font-size="11">STATUS</text>
  <circle class="dot" cx="{hud_x + 119}" cy="182" r="4.5" fill="{GREEN}"/>
  <text class="h" x="{hud_x + 131}" y="186" font-size="11" style="fill:{GREEN}">ACTIVE</text>
  <text class="h" x="{hud_x + 14}" y="226" font-size="11">SYNC RATIO</text>
  <rect x="{hud_x + 14}" y="236" width="252" height="18" fill="none" stroke="{ORANGE}" stroke-opacity=".6"/>
  <rect class="bar" x="{hud_x + 17}" y="239" width="246" height="12" fill="{PURPLE}"/>
  <rect class="bar" x="{hud_x + 17}" y="249" width="246" height="2" fill="{GREEN}"/>
  <text class="h n1" x="{hud_x + 266}" y="282" font-size="22" text-anchor="end" style="fill:{WHITE}">41.3%</text>
  <text class="h n2" x="{hud_x + 266}" y="282" font-size="22" text-anchor="end" style="fill:{WHITE}">87.9%</text>
  <text class="h n3" x="{hud_x + 266}" y="282" font-size="22" text-anchor="end" style="fill:{RED}">400%</text>
</g>
<rect y="0" width="1000" height="2" fill="{WHITE}" opacity=".07"><animateTransform attributeName="transform" type="translate" from="0 0" to="0 440" dur="4s" repeatCount="indefinite"/></rect>
"""
    return svg(1000, 440, "insalatadiriso, full-stack developer", style, body, defs)


def magi():
    blocks = [
        ("BUILDER·1", "Next.js · React Native · Supabase · Swift", 380, 46),
        ("DESIGNER·2", "interfaces · motion · type · brand", 190, 182),
        ("FOUNDER·3", "Saturday Company · products · agents", 570, 182),
    ]
    text_s = "承認提訴決議全会一致PROPOSALSHIPITRESULTUNANIMOUSAPPROVED" + "".join(b[0] for b in blocks)
    text_h = "".join(b[1] for b in blocks) + "PROPOSAL:SHIPITRESULT:UNANIMOUSCODE-APPROVEDMAGI-STYLEVOTE"
    style = (face("EvaSerif", SERIF, text_s) + face("EvaSans", SANS, text_h) + FLICKER + f"""
.s{{font-family:EvaSerif;fill:{WHITE}}}
.h{{font-family:EvaSans;fill:{AMBER};letter-spacing:1.5px}}
.blk{{fill:#0f2a16;stroke:{GREEN};stroke-width:2}}
.on{{animation:on 6s infinite}}
@keyframes on{{0%,8%{{fill:#0f2a16}}12%,80%{{fill:#2f8f3a}}84%,100%{{fill:#0f2a16}}}}
.ok{{animation:ok 6s infinite}}
@keyframes ok{{0%,10%{{opacity:0}}12%,80%{{opacity:1}}84%,100%{{opacity:0}}}}
.result{{animation:res 6s infinite}}
@keyframes res{{0%,40%{{opacity:0}}44%,80%{{opacity:1}}84%,100%{{opacity:0}}}}
""")
    body = [f'<path d="M500 150 L340 182 M560 150 L720 182 M490 234 L570 234" stroke="{GREEN}" stroke-opacity=".35" stroke-width="2"/>']
    for i, (name, sub, x, y) in enumerate(blocks):
        w, h, cut = 300, 104, 22
        poly = f"M{x + cut} {y} H{x + w} V{y + h - cut} L{x + w - cut} {y + h} H{x} V{y + cut} Z"
        delay = f"animation-delay:{i * 0.9:.1f}s"
        body.append(f'<path class="blk on" d="{poly}" style="{delay}"/>')
        body.append(f'<text class="s" x="{x + 18}" y="{y + 36}" font-size="20" letter-spacing="2">{name}</text>')
        body.append(f'<text class="h" x="{x + 18}" y="{y + 58}" font-size="10.5" style="fill:{WHITE};opacity:.85">{sub}</text>')
        body.append(f'<text class="s ok" x="{x + w - 18}" y="{y + 92}" font-size="30" text-anchor="end" style="{delay}">承認</text>')
    body.append(f"""
<text class="s" x="40" y="70" font-size="40">提訴</text>
<text class="h" x="40" y="96" font-size="12">PROPOSAL: SHIP IT</text>
<text class="s" x="40" y="214" font-size="40">決議</text>
<text class="h" x="40" y="240" font-size="12">RESULT:</text>
<g class="result"><text class="s" x="40" y="286" font-size="34" style="fill:{GREEN}">全会一致</text>
<text class="h" x="40" y="306" font-size="12" style="fill:{GREEN}">UNANIMOUS</text></g>
<text class="h" x="960" y="312" font-size="10" text-anchor="end" style="fill:{DIM}">MAGI-STYLE VOTE · CODE-APPROVED</text>
""")
    return svg(1000, 330, "Builder, designer, founder: approved", style, "".join(body))


def operations():
    ops = [
        ("OPERATION 01", "MONSTERS", "local agentic hub · an orchestrator", "and a squad of little monsters", ORANGE),
        ("OPERATION 02", "SUSPICIOUSDOG", "sniffs your agent transcripts", "for what actually works", PURPLE),
        ("OPERATION 03", "SATURDAY", "AI for companies and public bodies", "WitDesk · Anteiku · custom tools", GREEN),
    ]
    text_s = "".join(o[1] for o in ops)
    text_h = "".join(o[0] + o[2] + o[3] for o in ops) + "ACTIVE"
    style = (face("EvaSerif", SERIF, text_s) + face("EvaSans", SANS, text_h) + FLICKER + f"""
.s{{font-family:EvaSerif;fill:{WHITE}}}
.h{{font-family:EvaSans;letter-spacing:1.5px}}
.tick{{animation:pulse 1.8s infinite}}
.dot{{animation:blink 1.2s steps(1) infinite}}
""")
    body = []
    for i, (code, name, l1, l2, colour) in enumerate(ops):
        x = 20 + i * 328
        body.append(f"""<g class="f" style="animation-delay:{0.2 + i * 0.35:.2f}s">
<path d="M{x} 20 H{x + 312} V214 L{x + 292} 234 H{x} Z" fill="none" stroke="{colour}" stroke-width="2"/>
<path d="M{x} 20 H{x + 170} L{x + 156} 40 H{x} Z" fill="{colour}"/>
<text class="h" x="{x + 10}" y="35" font-size="11" fill="{BG}">{code}</text>
<text class="s" x="{x + 18}" y="104" font-size="40" textLength="{min(276, len(name) * 25)}" lengthAdjust="spacingAndGlyphs">{name}</text>
<text class="h" x="{x + 18}" y="140" font-size="11" fill="{WHITE}" opacity=".85">{l1}</text>
<text class="h" x="{x + 18}" y="158" font-size="11" fill="{WHITE}" opacity=".85">{l2}</text>
<circle class="dot" cx="{x + 24}" cy="196" r="5" fill="{GREEN}" style="animation-delay:{i * 0.4:.1f}s"/>
<text class="h" x="{x + 36}" y="200" font-size="11" fill="{GREEN}">ACTIVE</text>
{''.join(f'<rect class="tick" x="{x + 150 + k * 14}" y="190" width="9" height="12" fill="{colour}" style="animation-delay:{k * 0.15:.2f}s"/>' for k in range(9))}
</g>""")
    return svg(1000, 250, "Current operations: Monsters, SuspiciousDog, Saturday Company", style, "".join(body))


def footer():
    phrase = "EMERGENCY ・ BUILD IN PROGRESS ・ 作業中 ・ DO NOT DISTURB ・ 起動 ・ "
    size, spacing = 22, 3
    w = width(SERIF, phrase, size, spacing)
    style = face("EvaSerif", SERIF, phrase) + f".s{{font-family:EvaSerif;fill:{BG};letter-spacing:{spacing}px}}"
    repeat = phrase * 6
    body = f"""<rect y="0" width="1000" height="64" fill="{ORANGE}"/>
<rect y="0" width="1000" height="10" fill="url(#t2)"/><rect y="54" width="1000" height="10" fill="url(#t2)"/>
<g><text class="s" x="0" y="42" font-size="{size}">{repeat}</text>
<animateTransform attributeName="transform" type="translate" from="0 0" to="{-w:.1f} 0" dur="9s" repeatCount="indefinite"/></g>"""
    return svg(1000, 64, "Emergency: build in progress", style, body, tape("t2", 10, ORANGE, "1s"))


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, build in (("header", header), ("magi", magi), ("operations", operations), ("footer", footer)):
        out = ASSETS / f"{name}.svg"
        out.write_text(build())
        print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
