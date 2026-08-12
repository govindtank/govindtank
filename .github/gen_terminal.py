#!/usr/bin/env python3
"""Generate assets/terminal-intro.svg — CLI-install profile hero.
- Commands type character-by-character (discrete clip steps).
- Single pass: plays once, holds final state with blinking cursor (no flashing loop).
- --live: fetch GitHub stats (repos/followers/stars) from the API.
Font: .github/fonts/SpaceGrotesk.ttf embedded as data URI.
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

W, H = 820, 760
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
            + clip_def(cid, y - 16, 22, n, cw, dur, begin))

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
        st = {"repos": 511, "followers": 13, "stars": 5}

    repos = st["repos"] or 511
    followers = st["followers"] or 13
    stars = st["stars"] or 5
    n_pkgs = len(pkgs)

    d = []
    ap = d.append

    # 1. install command (types)
    ap(type_line(28, 82, prof["installer"], 0.4, 1.3, "c1"))

    # installing banner
    ap(fade(28, 112, "dim", "▸ installing govindtank-profile {v} — {n} libraries, {r} repos, {f} followers".format(
        v=prof["version"], n=n_pkgs, r=repos, f=followers), 2.0))
    # progress bar
    ap(f'<rect x="28" y="122" width="460" height="10" rx="5" fill="#21262d" opacity="0">'
       f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" begin="2.2s" fill="freeze"/></rect>')
    ap(f'<rect x="28" y="122" width="0" height="10" rx="5" fill="url(#progGrad)" opacity="0">'
       f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" begin="2.2s" fill="freeze"/>'
       f'{anim("width", "0;460", 1.6, 2.3)}</rect>')
    ap(fade(500, 128, "cy", "100%", 2.3))
    ap(fade(28, 122, "ok", "✔ dependencies resolved", 4.1))

    # extract lines
    ap(fade(28, 152, "ok", "✔ extracting skills — flutter · android · kotlin", 4.4))
    ap(fade(28, 176, "ok", "✔ linking — python · on-device AI · data dashboards", 4.7))
    ap(fade(28, 200, "ok", "✔ building — {r} repos · {n} pub.dev packages · {a} Play Store apps · {s} stars".format(
        r=repos, n=sum(1 for p in pkgs if p["url"].startswith("https://pub.dev/")), a=prof["apps"], s=stars), 5.0))
    ap(fade(28, 224, "ok", "✔ building — {n} JitPack libs · Kotlin Multiplatform · Compose".format(
        n=sum(1 for p in pkgs if not p["url"].startswith("https://pub.dev/"))), 5.2))

    # 2. profile command
    ap(type_line(28, 260, "govindtank --profile", 5.8, 0.8, "c2"))
    ap(f'<text class="hdrbig" x="28" y="292" opacity="0" filter="url(#glow)">'
       f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="6.9s" fill="freeze"/>{prof["name"]}</text>')
    ap(fade(30, 318, "role", prof["role"], 7.3))
    ap(fade(30, 340, "dim", prof["stack"], 7.5))

    # 3. libs command - show ALL libraries with better grouping
    ap(type_line(28, 380, "govindtank libs", 8.1, 0.6, "c3"))
    
    # pub.dev section header
    pub_pkgs = [p for p in pkgs if p["url"].startswith("https://pub.dev/")]
    jit_pkgs = [p for p in pkgs if not p["url"].startswith("https://pub.dev/")]
    
    ap(fade(48, 406, "pp", "── pub.dev ─────────────────────────────────────────", 8.5))
    
    for i, p in enumerate(pub_pkgs):
        b = 8.9 + i * 0.28
        ap(fade_parts(48, 426 + i * 22, b, [
            ("cmd", p["name"], 0),
            ("ok", "v" + p["version"], 380),
        ]))
        # Short description on next line
        ap(fade(70, 440 + i * 22, "dim", p["tag"], 8.9 + i * 0.28 + 0.15))
    
    # JitPack section header
    jit_start = 426 + len(pub_pkgs) * 22 + 10
    ap(fade(48, jit_start, "pp", "── JitPack ─────────────────────────────────────────", 9.3))
    
    for i, p in enumerate(jit_pkgs):
        b = 9.5 + i * 0.28
        ap(fade_parts(48, jit_start + 20 + i * 22, b, [
            ("cmd", p["name"], 0),
            ("ok", "v" + p["version"], 380),
        ]))
        # Short description on next line
        ap(fade(70, jit_start + 34 + i * 22, "dim", p["tag"], 9.5 + i * 0.28 + 0.15))

    # 4. whoami
    whoami_y = jit_start + 20 + len(jit_pkgs) * 22 + 30
    ap(type_line(28, whoami_y, "govindtank whoami", 10.8, 0.7, "c4"))
    ap(fade(28, whoami_y + 26, "pk", prof["motto"], 11.8))
    ap(fade(28, whoami_y + 50, "ok", "✔ install complete — govindtank-profile {v} is live".format(v=prof["version"]), 12.2))

    # final prompt + blinking cursor
    final_y = whoami_y + 80
    ap(f'<text class="prompt" x="28" y="{final_y}" opacity="0"><animate attributeName="opacity" from="0" to="1" '
       f'dur="0.05s" begin="12.6s" fill="freeze"/>$</text>')
    ap(f'<rect x="48" y="{final_y - 16}" width="11" height="22" rx="2" fill="#39d353" opacity="0">'
       f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="12.8s" repeatCount="indefinite"/></rect>')

    defs = f"""
  <defs>
    <style>
      @font-face {{ font-family:'Space Grotesk'; src:url(data:font/ttf;base64,{FONT_B64}) format('truetype'); font-weight:300 700; }}
      .bg   {{ fill:#0d1117; }}
      .dotr {{ fill:#ff5f56; }} .doty {{ fill:#ffbd2e; }} .dotg {{ fill:#27c93f; }}
      .mono {{ font-family:{MONO}; }}
      .sg   {{ font-family:{SG}; }}
      .prompt {{ fill:#39d353; font-size:15px; font-weight:600; font-family:{MONO}; }}
      .cmd   {{ fill:#e6edf3; font-size:15px; font-weight:600; font-family:{MONO}; }}
      .dim   {{ fill:#8b949e; font-size:14px; font-family:{MONO}; }}
      .cy    {{ fill:#22d3ee; font-size:14px; font-family:{MONO}; }}
      .ok    {{ fill:#27c93f; font-size:14px; font-weight:600; font-family:{MONO}; }}
      .pp    {{ fill:#d2a8ff; font-size:14px; font-family:{MONO}; }}
      .pk    {{ fill:#f778ba; font-size:14px; font-family:{MONO}; }}
      .role  {{ fill:#7ee787; font-size:17px; font-weight:500; font-family:{SG}; }}
      .hdrbig{{ fill:url(#nameGrad); font-size:28px; font-weight:700; letter-spacing:1px; font-family:{SG}; }}
    </style>
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#7ee787"/><stop offset="1" stop-color="#f778ba"/>
    </linearGradient>
    <linearGradient id="winGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#161b22"/><stop offset="1" stop-color="#0d1117"/>
    </linearGradient>
    <linearGradient id="progGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#39d353"/><stop offset="1" stop-color="#22d3ee"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="bodyClip"><rect x="0" y="48" width="{W}" height="{H - 48}"/></clipPath>
  </defs>
"""

    frame = f"""
  <rect class="bg" width="{W}" height="{H}" rx="16"/>
  <rect x="0" y="0" width="{W}" height="48" rx="16" fill="url(#winGrad)"/>
  <rect x="0" y="44" width="{W}" height="4" fill="#161b22"/>
  <circle class="dotr" cx="22" cy="24" r="7"/><circle class="doty" cx="46" cy="24" r="7"/><circle class="dotg" cx="70" cy="24" r="7"/>
  <text class="mono" x="410" y="31" text-anchor="middle" fill="#8b949e" font-size="12px">govindtank@github — installer</text>
  <g clip-path="url(#bodyClip)">
"""

    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + defs + frame + "\n".join(d) + "\n  </g>\n</svg>\n")

    OUT.write_text(svg)
    print(f"terminal-intro.svg written ({len(svg.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
