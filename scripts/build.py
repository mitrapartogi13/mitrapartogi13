#!/usr/bin/env python3
"""Builds the pixel-art SVGs for the profile README.

Needs only the standard library. Set GITHUB_TOKEN (any token that can read
public data). Writes everything into ./assets.
"""
import base64
import datetime as dt
import hashlib
import json
import os
import urllib.request
from xml.sax.saxutils import escape

LOGIN = "mitrapartogi13"
CITY = ("SURABAYA", -7.2575, 112.7521)
TAGLINE = "informatics @ ITS · surabaya, indonesia"
BIO = "Informatics student at ITS. I build web apps with Next.js + TypeScript, solve competitive programming problems in C++, and teach AI / RAG in workshops."
PROJECTS = [
    ("web-portofolio", "My personal portfolio site. Next.js 16, React 19, Tailwind v4."),
    ("wanigo-web", "WANIGO web app, with a Flutter app for customers (WANIGO_NASABAH)."),
    ("fp-kka", "DFS, BFS, UCS and A* search for a Pac-Man style game."),
    ("competitive-programming", "My solutions to competitive programming problems."),
]
WIB = dt.timezone(dt.timedelta(hours=7))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ---------- colours ----------
BG, CARD, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED, GREEN = "#e6edf3", "#8b949e", "#39d353"
LEVELS = {"NONE": "#1c2128", "FIRST_QUARTILE": "#0e4429", "SECOND_QUARTILE": "#006d32",
          "THIRD_QUARTILE": "#26a641", "FOURTH_QUARTILE": "#39d353"}
MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,monospace"

# ---------- 5x7 pixel font ----------
F = {
 "A": [".###.","#...#","#...#","#####","#...#","#...#","#...#"],
 "B": ["####.","#...#","#...#","####.","#...#","#...#","####."],
 "C": [".###.","#...#","#....","#....","#....","#...#",".###."],
 "D": ["####.","#...#","#...#","#...#","#...#","#...#","####."],
 "E": ["#####","#....","#....","####.","#....","#....","#####"],
 "F": ["#####","#....","#....","####.","#....","#....","#...."],
 "G": [".###.","#...#","#....","#.###","#...#","#...#",".####"],
 "H": ["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
 "I": ["#####","..#..","..#..","..#..","..#..","..#..","#####"],
 "J": ["..###","...#.","...#.","...#.","...#.","#..#.",".##.."],
 "K": ["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],
 "L": ["#....","#....","#....","#....","#....","#....","#####"],
 "M": ["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],
 "N": ["#...#","##..#","#.#.#","#..##","#...#","#...#","#...#"],
 "O": [".###.","#...#","#...#","#...#","#...#","#...#",".###."],
 "P": ["####.","#...#","#...#","####.","#....","#....","#...."],
 "Q": [".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"],
 "R": ["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
 "S": [".####","#....","#....",".###.","....#","....#","####."],
 "T": ["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
 "U": ["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
 "V": ["#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."],
 "W": ["#...#","#...#","#...#","#.#.#","#.#.#","#.#.#",".#.#."],
 "X": ["#...#","#...#",".#.#.","..#..",".#.#.","#...#","#...#"],
 "Y": ["#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."],
 "Z": ["#####","....#","...#.","..#..",".#...","#....","#####"],
 "0": [".###.","#...#","#..##","#.#.#","##..#","#...#",".###."],
 "1": ["..#..",".##..","..#..","..#..","..#..","..#..",".###."],
 "2": [".###.","#...#","....#","...#.","..#..",".#...","#####"],
 "3": ["#####","...#.","..#..","...#.","....#","#...#",".###."],
 "4": ["...#.","..##.",".#.#.","#..#.","#####","...#.","...#."],
 "5": ["#####","#....","####.","....#","....#","#...#",".###."],
 "6": ["..##.",".#...","#....","####.","#...#","#...#",".###."],
 "7": ["#####","....#","...#.","..#..",".#...",".#...",".#..."],
 "8": [".###.","#...#","#...#",".###.","#...#","#...#",".###."],
 "9": [".###.","#...#","#...#",".####","....#","...#.",".##.."],
 ".": [".....",".....",".....",".....",".....",".##..",".##.."],
 "-": [".....",".....",".....","#####",".....",".....","....."],
 ":": [".....",".##..",".##..",".....",".##..",".##..","....."],
 "/": ["....#","....#","...#.","..#..",".#...","#....","#...."],
 "!": ["..#..","..#..","..#..","..#..","..#..",".....","..#.."],
 ">": [".#...","..#..","...#.","....#","...#.","..#..",".#..."],
 "_": [".....",".....",".....",".....",".....",".....","#####"],
 "+": [".....","..#..","..#..","#####","..#..","..#..","....."],
 "°": [".##..","#..#.","#..#.",".##..",".....",".....","....."],
}


def ptext_width(s, cell):
    return len(s) * 6 * cell - cell


def ptext(s, x, y, cell, fill, extra=""):
    """Text in the pixel font, drawn as one path of horizontal runs."""
    d = []
    for i, ch in enumerate(s.upper()):
        rows = F.get(ch)
        if not rows:
            continue
        ox = x + i * 6 * cell
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    d.append(f"M{ox + start * cell} {y + r * cell}h{(c - start) * cell}v{cell}h-{(c - start) * cell}z")
                else:
                    c += 1
    return f'<path d="{"".join(d)}" fill="{fill}" {extra}/>'


def sprite(rows, x, y, cell, pal, extra=""):
    """Multi-colour bitmap: each char in rows maps to a colour in pal ('.' is empty)."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            out.append(f'<rect x="{x + start * cell}" y="{y + r * cell}" width="{(c - start) * cell}" height="{cell}" fill="{pal[ch]}"/>')
    return f'<g {extra}>{"".join(out)}</g>'


def pbox(x, y, w, h, fill, border, b=4):
    """Box with a pixel border and notched corners."""
    return (f'<rect x="{x + b}" y="{y + b}" width="{w - 2 * b}" height="{h - 2 * b}" fill="{fill}"/>'
            f'<rect x="{x + b}" y="{y}" width="{w - 2 * b}" height="{b}" fill="{border}"/>'
            f'<rect x="{x + b}" y="{y + h - b}" width="{w - 2 * b}" height="{b}" fill="{border}"/>'
            f'<rect x="{x}" y="{y + b}" width="{b}" height="{h - 2 * b}" fill="{border}"/>'
            f'<rect x="{x + w - b}" y="{y + b}" width="{b}" height="{h - 2 * b}" fill="{border}"/>')


def svg(w, h, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges"><style>text{{font-family:{MONO}}}{style}</style>{body}</svg>')


def mtext(s, x, y, size, fill, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" shape-rendering="auto">{escape(s)}</text>')


def wrap(s, n):
    lines, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        lines.append(cur)
    return lines


def compact(n):
    if n >= 1000:
        v = f"{n / 1000:.1f}".rstrip("0").rstrip(".")
        return f"{v}K"
    return str(n)


# ---------- data ----------
QUERY = """
query($login: String!) {
  user(login: $login) {
    name login bio location avatarUrl(size: 24)
    followers { totalCount }
    pullRequests { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name description stargazerCount isFork url
        primaryLanguage { name color }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
        defaultBranchRef { target { ... on Commit { history(first: 6) { nodes {
          messageHeadline committedDate author { user { login } } } } } } }
      }
    }
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { contributionCount date contributionLevel } } }
    }
  }
}"""


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_user(token):
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    res = http_json("https://api.github.com/graphql", body,
                    {"Authorization": f"bearer {token}", "Content-Type": "application/json",
                     "User-Agent": "profile-readme-builder"})
    if "errors" in res:
        raise SystemExit(res["errors"])
    return res["data"]["user"]


def fetch_weather():
    _, lat, lon = CITY
    try:
        w = http_json(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                      "&current=temperature_2m,weather_code,is_day&timezone=Asia%2FJakarta")["current"]
        return round(w["temperature_2m"]), int(w["weather_code"]), bool(w["is_day"])
    except Exception as e:  # weather is decoration; never fail the build for it
        print("weather unavailable:", e)
        hour = dt.datetime.now(WIB).hour
        return None, 0, 6 <= hour < 18


def weather_kind(code):
    if code in (0,):
        return "CLEAR"
    if code in (1, 2):
        return "CLOUDY"
    if code in (3, 45, 48):
        return "GREY"
    if code >= 95:
        return "STORM"
    if code >= 51:
        return "RAIN"
    return "CLOUDY"


def streaks(days):
    best = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        best = max(best, cur)
    # current streak: count back from today (today may still be empty)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0:
            continue
        else:
            break
    return current, best


# ---------- header: the pixel room ----------
SUN = ["..y.y..", ".yyyyy.", "yyyyyyy", "yyyyyyy", "yyyyyyy", ".yyyyy.", "..y.y.."]
MOON = ["..mmm..", ".mm....", "mm.....", "mm.....", "mm.....", ".mm....", "..mmm.."]
CLOUD = ["...wwww.....", ".wwwwwwww...", "wwwwwwwwwwww", ".gggggggggg."]
CAT = [
    ".o...o........",
    ".oo.oo........",
    ".ooooo.......o",
    "ooeoeoo......o",
    "oooooooooooooo",
    "ooooooooooooo.",
    ".wwoooooooooo.",
]
PLANT = ["..l.l...", ".lll.l..", "..llll..", ".l.ll.l.", "...ll...", ".pppppp.", ".pppppp.", "..pppp.."]
MUG = ["rrrr..", "rrrrr.", "rrrr.r", "rrrrr.", "rrrr.."]


def header(user, weather, langs, commits, now):
    W, H = 840, 300
    temp, code, is_day = weather
    kind = weather_kind(code)
    wall = "#1f1d3a" if is_day else "#141228"
    stripe = "#24224a" if is_day else "#181633"
    b = [f'<rect width="{W}" height="{H}" fill="{wall}"/>']
    b += [f'<rect x="{x}" y="0" width="20" height="228" fill="{stripe}"/>' for x in range(0, W, 40)]
    b.append('<rect x="0" y="228" width="840" height="8" fill="#2b2648"/>')
    # floor
    b.append('<rect x="0" y="236" width="840" height="64" fill="#3a281e"/>')
    for i, y in enumerate((252, 268, 284)):
        b.append(f'<rect x="0" y="{y}" width="840" height="4" fill="#2e2018"/>')
        b += [f'<rect x="{x + (i % 2) * 60}" y="{y - 12}" width="4" height="12" fill="#2e2018"/>' for x in range(40, W, 120)]

    # title
    name = (user["name"] or user["login"]).strip().upper()
    tw = ptext_width(name, 4)
    tx = (W - tw) // 2
    b.append(ptext(name, tx + 4, 20, 4, "#000", 'opacity=".35"'))
    b.append(ptext(name, tx, 16, 4, TEXT))
    b.append(mtext(TAGLINE, W // 2, 66, 12, MUTED, "middle"))

    # window + sky
    sky = {True: {"CLEAR": "#6ec3ff", "CLOUDY": "#8ec5ee", "GREY": "#93a4b5", "RAIN": "#71859a", "STORM": "#4b5868"},
           False: {"CLEAR": "#0b1030", "CLOUDY": "#111737", "GREY": "#161b33", "RAIN": "#121729", "STORM": "#0c0f1d"}}[is_day][kind]
    b.append('<clipPath id="sky"><rect x="48" y="92" width="160" height="104"/></clipPath>')
    b.append('<rect x="40" y="84" width="176" height="120" fill="#5c4033"/>')
    s = [f'<rect x="48" y="92" width="160" height="104" fill="{sky}"/>']
    if not is_day:
        for i, (sx, sy) in enumerate([(60, 100), (92, 120), (150, 104), (196, 132), (72, 160), (120, 100), (180, 176)]):
            s.append(f'<rect class="tw" style="animation-delay:{i * .4}s" x="{sx}" y="{sy}" width="4" height="4" fill="#fff"/>')
    if kind in ("CLEAR", "CLOUDY"):
        s.append(sprite(SUN if is_day else MOON, 164, 100, 4,
                        {"y": "#ffd34d", "m": "#f0f0d0"}))
    cloud_col = {"w": "#ffffff" if is_day else "#3a4160", "g": "#d5e3f0" if is_day else "#2c3250"}
    if kind in ("GREY", "RAIN", "STORM"):
        cloud_col = {"w": "#c3ccd6" if is_day else "#2f3550", "g": "#a3adb9" if is_day else "#252a40"}
    if kind != "CLEAR":
        s.append(f'<g class="cl">{sprite(CLOUD, 0, 104, 4, cloud_col)}</g>')
        s.append(f'<g class="cl" style="animation-delay:-11s">{sprite(CLOUD, 0, 136, 4, cloud_col)}</g>')
    if kind in ("RAIN", "STORM"):
        for i in range(14):
            rx = 52 + (i * 37) % 156
            s.append(f'<rect class="rn" style="animation-delay:{(i * 0.17) % 1:.2f}s" x="{rx}" y="88" width="2" height="8" fill="#b8d4ff"/>')
    if kind == "STORM":
        s.append('<rect class="fl" x="48" y="92" width="160" height="104" fill="#fff"/>')
    b.append(f'<g clip-path="url(#sky)">{"".join(s)}</g>')
    b.append('<rect x="126" y="92" width="4" height="104" fill="#5c4033"/>')
    b.append('<rect x="48" y="142" width="160" height="4" fill="#5c4033"/>')
    b.append('<rect x="32" y="204" width="192" height="8" fill="#6e4c3a"/>')
    label = f"{CITY[0]} {temp}° {kind}" if temp is not None else CITY[0]
    b.append(ptext(label, 40, 216, 2, MUTED))

    # lamp + light cone
    b.append('<polygon class="lamp" points="300,146 322,146 352,196 270,196" fill="#ffe9a8" opacity=".10" shape-rendering="auto"/>')
    b.append('<rect x="298" y="134" width="28" height="12" fill="#e0a43a"/>')
    b.append('<rect x="306" y="146" width="12" height="4" fill="#ffe9a8"/>')
    b.append('<rect x="290" y="146" width="4" height="46" fill="#9aa3b2"/><rect x="290" y="134" width="12" height="4" fill="#9aa3b2"/>')
    b.append('<rect x="282" y="190" width="20" height="6" fill="#6b7380"/>')

    # desk
    b.append('<rect x="270" y="196" width="320" height="10" fill="#7a5236"/>')
    b.append('<rect x="270" y="206" width="320" height="4" fill="#5e3f29"/>')
    b.append('<rect x="282" y="210" width="10" height="34" fill="#5e3f29"/><rect x="568" y="210" width="10" height="34" fill="#5e3f29"/>')

    # monitor with scrolling commits
    b.append('<rect x="340" y="84" width="184" height="106" fill="#2b2f3a"/>')
    b.append('<rect x="348" y="92" width="168" height="88" fill="#07110a"/>')
    b.append('<rect x="420" y="190" width="24" height="2" fill="#2b2f3a"/><rect x="404" y="192" width="56" height="4" fill="#3a3f4b"/>')
    b.append('<rect class="led" x="510" y="184" width="6" height="2" fill="#39d353"/>')
    b.append(mtext("~/latest-commits", 354, 104, 9, "#3fb950"))
    b.append('<rect x="352" y="108" width="160" height="1" fill="#1f3b25"/>')
    b.append('<clipPath id="scr"><rect x="348" y="111" width="168" height="67"/></clipPath>')
    lh = 13
    rows = [f"› {c['repo']}: {c['msg']}" for c in commits] or ["› no public commits yet"]
    rows = [r if len(r) <= 31 else r[:30] + "…" for r in rows]
    lines = "".join(mtext(r, 354, 122 + i * lh, 8.5, "#7ee787") for i, r in enumerate(rows + rows))
    dur = max(len(rows) * 2.2, 6)
    b.append(f'<g clip-path="url(#scr)"><g class="scr" style="animation:scroll {dur:.1f}s linear infinite">{lines}</g></g>')
    scroll_h = len(rows) * lh

    # mug + steam
    b.append(sprite(MUG, 540, 176, 4, {"r": "#d9534f"}))
    for i, sx in enumerate((542, 550)):
        b.append(f'<rect class="st" style="animation-delay:{i * .9}s" x="{sx}" y="168" width="2" height="6" fill="#c9d1d9"/>')

    # shelves with one book per language
    b.append('<rect x="612" y="128" width="200" height="6" fill="#6e4c3a"/><rect x="612" y="196" width="200" height="6" fill="#6e4c3a"/>')
    b += [f'<rect x="{x}" y="134" width="4" height="8" fill="#4e3526"/><rect x="{x}" y="202" width="4" height="8" fill="#4e3526"/>' for x in (624, 796)]
    x = 620
    for i, (lname, color, _) in enumerate(langs[:7]):
        bw = 18 + (i * 7) % 6
        bh = 40 + (i * 13) % 14
        b.append(f'<rect x="{x}" y="{128 - bh}" width="{bw}" height="{bh}" fill="{color}"/>')
        b.append(f'<rect x="{x + 3}" y="{128 - bh + 6}" width="{bw - 6}" height="2" fill="#000" opacity=".25"/>')
        b.append(f'<rect x="{x + 3}" y="{128 - 10}" width="{bw - 6}" height="2" fill="#000" opacity=".25"/>')
        x += bw + 3
    b.append(sprite(PLANT, 760, 164, 4, {"l": "#3fb950", "p": "#b5651d"}))
    b.append(sprite(["gggg", "gyyg", ".gg.", "gggg"], 626, 180, 4, {"g": "#d29922", "y": "#ffd34d"}))
    for i, (lname, color, _) in enumerate(langs[:6]):
        lx, ly = 614 + (i % 3) * 68, 212 + (i // 3) * 12
        b.append(f'<rect x="{lx}" y="{ly - 6}" width="6" height="6" fill="{color}"/>')
        b.append(mtext(lname[:10], lx + 9, ly, 8, MUTED))

    # sleeping cat + z
    b.append(sprite(CAT, 650, 254, 4, {"o": "#e8a15a", "e": "#3a2a20", "w": "#fff3e0"}))
    for i in range(3):
        b.append(f'<g class="z" style="animation-delay:{i}s">{ptext("Z", 700 + i * 2, 244, 2, "#c9d1d9")}</g>')

    b.append(mtext(f"updated {now:%d %b %Y %H:%M} WIB", 832, 294, 9, "#8b6f5c", "end"))

    style = (
        f"@keyframes scroll{{to{{transform:translateY(-{scroll_h}px)}}}}"
        ".cl{animation:drift 22s linear infinite}@keyframes drift{from{transform:translateX(-60px)}to{transform:translateX(220px)}}"
        ".rn{animation:rain 1s linear infinite}@keyframes rain{to{transform:translateY(112px)}}"
        ".fl{opacity:0;animation:flash 7s infinite}@keyframes flash{0%,93%,97%,100%{opacity:0}95%{opacity:.6}}"
        ".tw{animation:tw 2.4s steps(2) infinite}@keyframes tw{50%{opacity:.2}}"
        ".led{animation:tw 1.6s steps(2) infinite}"
        ".lamp{animation:lamp 4s steps(4) infinite}@keyframes lamp{50%{opacity:.16}}"
        ".st{opacity:0;animation:steam 1.8s linear infinite}@keyframes steam{0%{opacity:0;transform:translateY(0)}30%{opacity:.7}100%{opacity:0;transform:translateY(-14px)}}"
        ".z{opacity:0;animation:zz 3s linear infinite}@keyframes zz{0%{opacity:0;transform:translate(0,0)}20%{opacity:1}100%{opacity:0;transform:translate(14px,-26px)}}"
    )
    return svg(W, H, "".join(b), style)


# ---------- other cards ----------
def about(user, avatar_b64):
    W, H = 840, 150
    b = [pbox(0, 0, W, H, CARD, BORDER)]
    b.append(pbox(24, 24, 104, 104, "#0d1117", GREEN))
    if avatar_b64:
        b.append(f'<image x="28" y="28" width="96" height="96" style="image-rendering:pixelated" '
                 f'href="data:image/png;base64,{avatar_b64}"/>')
    b.append(ptext("> ABOUT", 152, 26, 2, GREEN))
    b.append(ptext((user["name"] or user["login"]).strip(), 152, 44, 3, TEXT))
    for i, line in enumerate(wrap(BIO, 86)):
        b.append(mtext(line, 152, 90 + i * 16, 12, "#c9d1d9"))
    meta = f"{user['location'] or ''} · @{user['login']} · {user['followers']['totalCount']} followers · {user['repositories']['totalCount']} public repos"
    b.append(mtext(meta, 152, 128, 11, MUTED))
    return svg(W, H, "".join(b))


def stats(items):
    W, H = 840, 92
    b = [pbox(0, 0, W, H, CARD, BORDER)]
    cw = W // len(items)
    for i, (value, label) in enumerate(items):
        cx = i * cw
        if i:
            b.append(f'<rect x="{cx}" y="16" width="4" height="{H - 32}" fill="{BORDER}"/>')
        b.append(ptext(value, cx + 28, 22, 4, TEXT))
        b.append(ptext(label, cx + 28, 60, 2, MUTED))
    return svg(W, H, "".join(b))


def section(title):
    return svg(840, 30, ptext("> " + title, 0, 8, 2, GREEN) +
               f'<rect class="cur" x="{ptext_width("> " + title, 2) + 8}" y="8" width="10" height="14" fill="{GREEN}"/>',
               ".cur{animation:b 1s steps(2) infinite}@keyframes b{50%{opacity:0}}")


def identicon(name, x, y, cell, color):
    h = hashlib.md5(name.encode()).digest()
    rows = []
    for r in range(5):
        half = ["c" if (h[r] >> c) & 1 else "." for c in range(3)]
        rows.append("".join(half + half[1::-1]))
    return sprite(rows, x, y, cell, {"c": color})


def project_card(repo, desc):
    W, H = 410, 120
    lang = repo["primaryLanguage"] or {"name": "—", "color": MUTED}
    color = lang["color"] or MUTED
    b = [pbox(0, 0, W, H, CARD, BORDER)]
    b.append(pbox(18, 18, 68, 68, "#0d1117", BORDER))
    b.append(identicon(repo["name"], 27, 27, 10, color))
    b.append(mtext(repo["name"], 102, 38, 15, "#58a6ff", weight="bold"))
    for i, line in enumerate(wrap(desc or repo["description"] or "", 40)[:3]):
        b.append(mtext(line, 102, 58 + i * 15, 11, "#c9d1d9"))
    b.append(sprite(["..y..", ".yyy.", "yyyyy", ".yyy.", ".y.y."], 18, 98, 2, {"y": "#e3b341"}))
    b.append(ptext(str(repo["stargazerCount"]), 32, 98, 2, "#e3b341"))
    b.append(f'<rect x="102" y="98" width="10" height="10" fill="{color}"/>')
    b.append(mtext(lang["name"], 118, 107, 11, MUTED))
    return svg(W, H, "".join(b))


def activity(days, total, current, best):
    W, H = 840, 168
    b = [pbox(0, 0, W, H, CARD, BORDER)]
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    cell, gap, ox, oy = 10, 2, 22, 24
    for wi, week in enumerate(weeks):
        for d in week:
            wd = (dt.date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday first
            fill = LEVELS.get(d["contributionLevel"], LEVELS["NONE"])
            b.append(f'<rect class="hc" style="animation-delay:{wi * 0.025:.3f}s" x="{ox + wi * (cell + gap)}" '
                     f'y="{oy + wd * (cell + gap)}" width="{cell}" height="{cell}" fill="{fill}"/>')
    gx = ox + len(weeks) * (cell + gap) + 18
    for i, (val, lab) in enumerate(((f"{current}D", "CURRENT STREAK"), (f"{best}D", "BEST STREAK"), (compact(total), "LAST YEAR"))):
        y = 22 + i * 44
        b.append(ptext(val, gx, y, 3, TEXT))
        b.append(mtext(lab.lower(), gx, y + 36, 10, MUTED))
    # legend
    lx = ox
    b.append(mtext("less", lx, 132, 10, MUTED))
    for i, c in enumerate(LEVELS.values()):
        b.append(f'<rect x="{lx + 30 + i * 14}" y="123" width="10" height="10" fill="{c}"/>')
    b.append(mtext("more", lx + 30 + 5 * 14 + 4, 132, 10, MUTED))
    b.append(mtext(f"{total} contributions in the last year", ox, 152, 10, MUTED))
    style = ".hc{animation:pop .4s steps(3) both}@keyframes pop{from{opacity:.15}to{opacity:1}}"
    return svg(W, H, "".join(b), style)


# ---------- main ----------
def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")
    os.makedirs(OUT, exist_ok=True)
    user = fetch_user(token)
    repos = user["repositories"]["nodes"]
    now = dt.datetime.now(WIB)

    langs = {}
    for r in repos:
        if r["isFork"]:
            continue
        for e in r["languages"]["edges"]:
            n = e["node"]
            name, color = n["name"], n["color"] or "#8b949e"
            size = langs.get(name, (color, 0))[1] + e["size"]
            langs[name] = (color, size)
    langs = sorted(((k, v[0], v[1]) for k, v in langs.items()), key=lambda t: -t[2])

    commits = []
    for r in repos:
        ref = r["defaultBranchRef"]
        if not ref or r["isFork"] or r["name"].lower() == LOGIN.lower():
            continue
        for c in ref["target"]["history"]["nodes"]:
            who = (c["author"] or {}).get("user") or {}
            if who.get("login", "").lower() == LOGIN.lower() and not c["messageHeadline"].startswith("Merge"):
                commits.append({"repo": r["name"], "msg": c["messageHeadline"], "date": c["committedDate"]})
    commits = sorted(commits, key=lambda c: c["date"], reverse=True)[:8]

    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    current, best = streaks(days)
    stars = sum(r["stargazerCount"] for r in repos if not r["isFork"])

    avatar = None
    try:
        with urllib.request.urlopen(user["avatarUrl"], timeout=30) as r:
            avatar = base64.b64encode(r.read()).decode()
    except Exception as e:
        print("avatar unavailable:", e)

    files = {
        "header.svg": header(user, fetch_weather(), langs, commits, now),
        "about.svg": about(user, avatar),
        "stats.svg": stats([(compact(cal["totalContributions"]), "CONTRIBUTIONS"),
                            (compact(user["pullRequests"]["totalCount"]), "PULL REQS"),
                            (compact(stars), "STARS"), (f"{best}D", "BEST STREAK")]),
        "activity.svg": activity(days, cal["totalContributions"], current, best),
        "section-projects.svg": section("PROJECTS"),
        "section-activity.svg": section("ACTIVITY"),
        "section-stack.svg": section("TECH STACK"),
    }
    by_name = {r["name"]: r for r in repos}
    for name, desc in PROJECTS:
        if name in by_name:
            files[f"project-{name}.svg"] = project_card(by_name[name], desc)
    for fname, content in files.items():
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(content)
    print("wrote", ", ".join(files))


if __name__ == "__main__":
    main()
