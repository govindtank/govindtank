#!/usr/bin/env python3
"""Generate assets/terminal-intro.svg — CLI-install profile hero.
- Commands type character-by-character (discrete clip steps).
- Single pass: plays once, holds final state with blinking cursor (no flashing loop).
- --live: fetch GitHub stats (repos/followers/stars) from the API.
Font: .github/fonts/SpaceGrotesk.ttf embedded as data URI.

Design upgrades:
- Clean aligned layout with consistent spacing
- Better visual hierarchy
- Professional terminal aesthetic
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / ".github" / "fonts" / "SpaceGrotesk.ttf"
PKG_JSON = ROOT / ".github" / "packages.json"
OUT = ROOT / "assets" / "terminal-intro.svg"

W, H = 820, 940
MONO = "'JetBrains Mono','Fira Code','SF Mono',Menlo,monospace"
SG = "'Space Grotesk',system-ui,sans-serif"
FONT_B64 = base64.b64encode(FONT.read_bytes()).decode()

def anim(attr, values, dur, begin, keytimes=None, mode="linear", repeat=None):
    kt = f' keyTimes="{keytimes}" calcMode="discrete"' if keytimes else f' calcMode="{mode}"'
    rep = f' repeatCount="{repeat}"' if repeat else ''
    return f'<animate attributeName="{attr}" values="{values}"{kt} dur="{dur}s" begin="{begin}s"{rep} fill="freeze"/>'

def clip_def(cid, y, h, n, cw, dur, begin):
    widths = ";".join(str(round(i * cw, 1)) for i in range(n + 1))
    kts = ";".join(str(round(i / n, 4)) for i in range(n + 1))
    return (f'<clipPath id="{cid}"><rect x="0" y="{y}" width="0" height="{h}">'
            f'{anim("width", widths, dur, begin, kts)}</rect></clipPath>')

def type_line(x, y, cmd, begin, dur, cid, cw=9.2):
    n = len(cmd)
    return (f'<text class="prompt" x="{x}" y="{y}" opacity="0"><animate attributeName="opacity" '
            f'from="0" to="1" dur="0.05s" begin="{begin}s" fill="freeze"/>$</text>'
            f'<text class="cmd" x="{x + 20}" y="{y}" clip-path="url(#{cid})">{cmd}</text>'
            + clip_def(cid, y - 16, 24, n, cw, dur, begin))

def fade(x, y, cls, text, begin, anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ''
    return (f'<text class="{cls}" x="{x}" y="{y}"{a} opacity="0"><animate attributeName="opacity" '
            f'from="0" to="1" dur="0.2s" begin="{begin}s" fill="freeze"/>{text}</text>')

def fade_parts(x, y, begin, parts):
    inner = "".join(f'<text class="{c}" x="{x + dx}" y="{y}">{t}</text>' for c, t, dx in parts)
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.2s" '
            f'begin="{begin}s" fill="freeze"/>{inner}</g>')

def fetch_stats():
    import os
    stats = {"repos": None, "followers": None, "stars": None}
    hdrs = {"User-Agent": "govindtank-readme/1.0"}
    tok = os.environ.get("GITHUB_TOKEN", "")
    if tok:
        hdrs["Authorization"] = f"token {tok}"
    try:
        req = urllib.request.Request("https://api.github.com/users/govindtank", headers=hdrs)
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
            stats["repos"] = d.get("public_repos")
            stats["followers"] = d.get("followers")
    except Exception:
        pass
    try:
        stars = 0
        for page in range(1, 7):
            req = urllib.request.Request(
                f"https://api.github.com/users/govindtank/repos?per_page=100&page={page}",
                headers={"User-Agent": "govindtank-readme/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                rs = json.load(r)
            stars += sum(r.get("stargazers_count", 0) for r in rs)
            if len(rs) < 100:
                break
        stats["stars"] = stars
    except Exception:
        pass
    return stats


def main():
    import os
    live = "--live" in sys.argv
    data = json.loads(PKG_JSON.read_text())
    prof = data["profile"]
    pkgs = data["packages"]

    if live:
        st = fetch_stats()
        if st["repos"]:
            print(f"  live: {st['repos']} repos, {st['followers']} followers, {st['stars']} stars")
        else:
            print("  live stats unavailable, using defaults")
    else:
        st = {"repos": 512, "followers": 13, "stars": 10}

    repos = st["repos"] or 512
    followers = st["followers"] or 13
    stars = st["stars"] or 10
    n_pkgs = len(pkgs)

    d = []
    ap = d.append

    # Section 1: Install command
    ap(type_line(28, 92, prof["installer"], 0.4, 1.5, "c1"))
    
    # Installing banner
    ap(fade(28, 124, "dim", f"▸ installing govindtank-profile {prof['version']} — {n_pkgs} libraries, {repos} repos, {followers} followers", 2.0))
    
    # Progress bar
    ap(f'<rect x="28" y="142" width="460" height="10" rx="5" fill="#21262d" opacity="0">'
       f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" begin="2.0s" fill="freeze"/></rect>')
    ap(f'<rect x="28" y="142" width="0" height="10" rx="5" fill="url(#progGrad)" opacity="0">'
       f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" begin="2.0s" fill="freeze"/>'
       f'{anim("width", "0;460", 1.8, 2.1)}</rect>')
    ap(fade(500, 136, "cy", "100%", 2.1))
    ap(fade(28, 158, "ok", "✔ dependencies resolved — all checks passed", 3.8))

    # Section 2: Skills
    ap(type_line(28, 200, "govindtank --skills", 4.0, 0.7, "c2"))
    
    skills = [
        "✔ Flutter • Android Studio • Kotlin",
        "✔ Python • TensorFlow Lite • ONNX Runtime",
        "✔ Data Dashboards • Plotly • Flask",
        "✔ On-Device AI • Whisper.cpp • MediaPipe",
    ]
    for i, skill in enumerate(skills):
        ap(fade(48, 234 + i * 26, "skill", skill, 4.0 + i * 0.12))

    # Section 3: Build summary
    ap(type_line(28, 340, "govindtank --build", 6.0, 0.7, "c3"))
    
    ap(fade(28, 374, "ok", f"├── {repos} repositories built across Flutter • Kotlin • Python", 6.0 + 0.15))
    pub_count = sum(1 for p in pkgs if p["url"].startswith("https://pub.dev/"))
    jit_count = len(pkgs) - pub_count
    ap(fade(28, 402, "ok", f"├── {n_pkgs} packages: {pub_count} × pub.dev • {jit_count} × JitPack", 6.15))
    ap(fade(28, 430, "ok", f"└── {prof['apps']} Play Store apps • {prof.get('dashboards', 3)} live dashboards shipped in production", 6.3))

    # Section 4: Profile
    ap(type_line(28, 490, "govindtank --profile", 7.0, 0.6, "c4"))
    
    ap(f'<text class="hdrbig" x="28" y="530" opacity="0" filter="url(#nameGlow)">'
       f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="7.9s" fill="freeze"/>{prof["name"]}</text>')
    ap(fade(30, 572, "role", prof["role"], 8.4))
    ap(fade(30, 596, "dim", prof["stack"], 8.7))

    # Section 5: Libraries
    ap(type_line(28, 650, "govindtank libs", 9.0, 0.5, "c3"))
    
    pub_pkgs = [p for p in pkgs if p["url"].startswith("https://pub.dev/")]
    jit_pkgs = [p for p in pkgs if not p["url"].startswith("https://pub.dev/")]
    
    # pub.dev section
    ap(fade(48, 680, "pp", "── pub.dev ─────────────────────────────────────────────────", 9.3))
    
    for i, p in enumerate(pub_pkgs):
        y = 716 + i * 28
        ap(fade_parts(48, y, 9.5 + i * 0.12, [
            ("cmd", f"[{p['name']}] {p['version']}", 0),
            (p["color"], p["url"], 340),
        ]))

    # JitPack section
    y_jit = 716 + len(pub_pkgs) * 28 + 16
    ap(fade(48, y_jit, "pp", "── JitPack ─────────────────────────────────────────────────", 9.5))
    
    for i, p in enumerate(jit_pkgs):
        y = y_jit + 20 + i * 28
        ap(fade_parts(48, y, 9.7 + i * 0.12, [
            ("cmd", f"[{p['name']}] {p['version']}", 0),
            (p["color"], p["url"], 340),
        ]))

    # Section 6: Whoami
    whoami_y = y_jit + 20 + len(jit_pkgs) * 28 + 30
    ap(type_line(28, whoami_y, "govindtank whoami", 11.5, 0.5, "c4"))
    ap(fade(28, whoami_y + 30, "pk", prof["motto"], 12.5))
    ap(fade(28, whoami_y + 60, "dim", "✔ setup complete — ready to ship", 13.0))

    # Final prompt with blinking cursor
    final_y = whoami_y + 100
    ap(f'<text class="prompt" x="28" y="{final_y}" opacity="0"><animate attributeName="opacity" from="0" to="1" '
       f'dur="0.05s" begin="13.3s" fill="freeze"/>$</text>')
    ap(f'<rect x="48" y="{final_y - 16}" width="11" height="22" rx="2" fill="#39d353" opacity="0">'
       f'<animate attributeName="opacity" values="1;0;1" dur="0.8s" begin="13.5s" repeatCount="indefinite"/></rect>')

    # SVG Defs
    defs = f"""
  <defs>
    <style>
      @font-face {{ font-family:'Space Grotesk'; src:url(data:font/ttf;base64,{FONT_B64}) format('truetype'); font-weight:300 700; }}
      .bg   {{ fill:#0d1117; }}
      .dotr {{ fill:#ff5f56; }} .doty {{ fill:#ffbd2e; }} .dotg {{ fill:#27c93f; }}
      .mono {{ font-family:{MONO}; }}
      .sg   {{ font-family:{SG}; }}
      .prompt {{ fill:#39d353; font-size:16px; font-weight:600; letter-spacing:1px; font-family:{MONO}; text-shadow:0 0 8px rgba(57,211,83,0.4); }}
      .cmd   {{ fill:#e6edf3; font-size:15px; font-weight:500; font-family:{MONO}; opacity:0.92; }}
      .dim   {{ fill:#8b949e; font-size:14px; font-family:{MONO}; }}
      .cy    {{ fill:#22d3ee; font-size:14px; font-weight:500; font-family:{MONO}; opacity:0.9; text-shadow:0 0 6px rgba(34,211,238,0.3); }}
      .ok    {{ fill:#27c93f; font-size:14px; font-weight:500; font-family:{MONO}; opacity:0.95; text-shadow:0 0 6px rgba(39,201,63,0.3); }}
      .pp    {{ fill:#d2a8ff; font-size:14px; font-family:{MONO}; opacity:0.88; }}
      .skill {{ fill:#8b949e; font-size:14px; font-family:{MONO}; opacity:0.9; }}
      .role  {{ fill:url(#nameGrad); font-size:20px; font-weight:600; letter-spacing:0.5px; font-family:{SG}; }}
      .hdrbig{{ fill:url(#nameGrad); font-size:32px; font-weight:700; letter-spacing:1px; text-anchor:middle; font-family:{SG}; }}
    </style>
    <linearGradient id="nameGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22d3ee"/><stop offset="50%" stop-color="#7ee787"/><stop offset="100%" stop-color="#f778ba"/>
    </linearGradient>
    <linearGradient id="winGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#161b22"/><stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>
    <linearGradient id="progGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#39d353"/><stop offset="100%" stop-color="#22d3ee"/>
    </linearGradient>
    <filter id="nameGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
"""

    frame = f"""
  <rect class="bg" width="{W}" height="{H}" rx="20"/>
  <rect x="0" y="0" width="{W}" height="56" rx="20" fill="url(#winGrad)"/>
  <rect x="0" y="52" width="{W}" height="4" fill="#161b22"/>
  <circle class="dotr" cx="30" cy="28" r="7"/><circle class="doty" cx="59" cy="28" r="7"/><circle class="dotg" cx="90" cy="28" r="7"/>
  <text class="mono" x="410" y="36" text-anchor="middle" fill="#8b949e" font-size="12px">govindtank@github — CLI installer v{prof["version"]}</text>
  <g clip-path="url(#bodyClip)">
"""

    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + defs + frame + "\n".join(d) + "\n  </g>\n</svg>\n")

    OUT.write_text(svg)
    print(f"terminal-intro.svg written ({len(svg.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
