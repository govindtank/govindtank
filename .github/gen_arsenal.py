#!/usr/bin/env python3
"""Generate assets/library-demo.svg from .github/packages.json.
--live: fetch current versions from pub.dev API (fallback to JSON on failure).
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
OUT = ROOT / "assets" / "library-demo.svg"

SG = "'Space Grotesk',system-ui,sans-serif"
MONO = "'JetBrains Mono','Fira Code','SF Mono',Menlo,monospace"
FONT_B64 = base64.b64encode(FONT.read_bytes()).decode()


def fetch_version(name):
    try:
        req = urllib.request.Request(f"https://pub.dev/api/packages/{name}",
                                     headers={"User-Agent": "govindtank-readme/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
            v = d.get("latest", {}).get("version")
            if v:
                return v
    except Exception:
        pass
    return None


def anim(attr, values, dur, begin, keytimes=None, mode="linear", repeat=None):
    kt = f' keyTimes="{keytimes}" calcMode="discrete"' if keytimes else f' calcMode="{mode}"'
    rep = f' repeatCount="{repeat}"' if repeat else ''
    return f'<animate attributeName="{attr}" values="{values}"{kt} dur="{dur}s" begin="{begin}s"{rep} fill="freeze"/>'


def clip_def(cid, y, h, n, cw, dur, begin):
    widths = ";".join(str(round(i * cw, 1)) for i in range(n + 1))
    kts = ";".join(str(round(i / n, 4)) for i in range(n + 1))
    return (f'<clipPath id="{cid}"><rect x="0" y="{y}" width="0" height="{h}">'
            f'{anim("width", widths, dur, begin, kts)}</rect></clipPath>')


def entrance(gid, begin):
    """fade + slide-up entrance for a card group"""
    return (f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.45s" begin="{begin}s" fill="freeze"/>'
            f'<g id="{gid}">')


def main():
    live = "--live" in sys.argv
    data = json.loads(PKG_JSON.read_text())
    pkgs = data["packages"]
    hdr = data["header"]

    if live:
        for p in pkgs:
            if not p["url"].startswith("https://pub.dev/"):
                continue
            name = p["url"].split("/")[-1]
            v = fetch_version(name)
            if v and v != p["version"]:
                print(f"  {p['name']}: {p['version']} -> {v}")
                p["version"] = v

    # Grid: 4 columns x 2 rows
    COLS = 4
    ROWS = 2
    CARD_W = 340
    CARD_H = 210
    GAP_X = 30
    GAP_Y = 30
    START_X = 30
    START_Y = 100
    TOTAL_W = START_X * 2 + COLS * CARD_W + (COLS - 1) * GAP_X
    TOTAL_H = START_Y + ROWS * CARD_H + (ROWS - 1) * GAP_Y + 30

    css = f"""
      @font-face {{ font-family:'Space Grotesk'; src:url(data:font/ttf;base64,{FONT_B64}) format('truetype'); font-weight:300 700; }}
      .sg   {{ font-family:{SG}; }}
      .mono {{ font-family:{MONO}; }}
      .title{{ fill:url(#headGrad); font-size:32px; font-weight:700; letter-spacing:2px; }}
      .sub  {{ fill:#8b949e; font-size:15px; }}
      .name {{ fill:#e6edf3; font-size:16px; font-weight:600; }}
      .ver  {{ fill:#0d1117; font-size:12px; font-weight:700; }}
      .code {{ fill:#79c0ff; font-size:12px; }}
      .tag  {{ fill:#8b949e; font-size:11px; }}
      .ok   {{ fill:#27c93f; font-size:12px; font-weight:600; }}
      .pkgcount {{ fill:#f778ba; font-size:13px; font-weight:700; }}
      .publink {{ fill:#58a6ff; font-size:11px; }}
    """

    grads = []
    for i, p in enumerate(pkgs):
        grads.append(f'<linearGradient id="g{i+1}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0" stop-color="{p["color"]}"/><stop offset="1" stop-color="{p["color2"]}"/></linearGradient>')
    grad_ids = "".join(grads)

    # header
    out = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}" height="{TOTAL_H}" viewBox="0 0 {TOTAL_W} {TOTAL_H}">',
        "  <defs>", f"    <style>{css}</style>",
        f'    <linearGradient id="headGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#7ee787"/><stop offset="1" stop-color="#f778ba"/></linearGradient>',
        grad_ids, "  </defs>",
        f'<text class="sg title" x="30" y="55">{hdr["title"]}</text>',
        f'<text class="sg sub" x="32" y="80">{hdr["sub"]}</text>',
        f'<line x1="30" y1="92" x2="{TOTAL_W - 30}" y2="92" stroke="#21262d"/>',
        f'<line x1="30" y1="92" x2="30" y2="92" stroke="url(#headGrad)" stroke-width="2">'
        f'{anim("x2", f"30;{TOTAL_W - 30}", 1.2, 0.3)}</line>',
    ]

    # badge animations for header
    out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="1.5s" fill="freeze"/>')
    out.append(f'<rect x="30" y="104" width="140" height="24" rx="12" fill="#161b22" stroke="#30363d"/>')
    out.append(f'<text class="sg pkgcount" x="100" y="120" text-anchor="middle">4 pub.dev</text>')
    out.append(f'</g>')
    out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="1.7s" fill="freeze"/>')
    out.append(f'<rect x="180" y="104" width="140" height="24" rx="12" fill="#161b22" stroke="#30363d"/>')
    out.append(f'<text class="sg pkgcount" x="250" y="120" text-anchor="middle">4 JitPack</text>')
    out.append(f'</g>')

    for i, p in enumerate(pkgs):
        col = i % COLS
        row = i // COLS
        cx = START_X + col * (CARD_W + GAP_X)
        cy = START_Y + row * (CARD_H + GAP_Y)
        bg = 1.8 + i * 0.15
        registry = "pub.dev" if p["url"].startswith("https://pub.dev/") else "JitPack"

        out.append(f'  {entrance(f"card{i}", bg)}')
        out.append(f'  <g transform="translate({cx},{cy})">')
        # card background
        out.append(f'    <rect width="{CARD_W}" height="{CARD_H}" rx="16" fill="#161b22" stroke="#30363d"/>')
        # top gradient bar
        out.append(f'    <rect width="{CARD_W}" height="6" rx="3" fill="url(#g{i+1})">'
                   f'{anim("height", "6;8;6", 2, bg + 0.5)}</rect>')
        # icon pulse
        out.append(f'    <rect x="16" y="22" width="44" height="44" rx="12" fill="{p["color2"]}" opacity="0.15">'
                   f'<animate attributeName="opacity" values="0.15;0.35;0.15" dur="3s" begin="{bg + 0.5}s" repeatCount="indefinite"/></rect>')
        out.append(f'    <text x="38" y="50" font-size="20" fill="{p["iconColor"]}" text-anchor="middle">{p["icon"]}</text>')
        # name + version badge
        out.append(f'    <text class="sg name" x="72" y="42">{p["name"]}</text>')
        out.append(f'    <rect x="72" y="50" width="62" height="20" rx="10" fill="url(#g{i+1})"/>')
        out.append(f'    <text class="sg ver" x="103" y="64" text-anchor="middle">{p["version"]}</text>')
        # registry badge
        out.append(f'    <rect x="{CARD_W - 80}" y="22" width="64" height="20" rx="10" fill="#21262d" stroke="#30363d"/>')
        out.append(f'    <text class="sg publink" x="{CARD_W - 48}" y="36" text-anchor="middle">{registry}</text>')
        # divider
        out.append(f'    <line x1="16" y1="78" x2="{CARD_W - 16}" y2="78" stroke="#21262d"/>')
        # description
        out.append(f'    <text class="sg sub" x="16" y="100" width="{CARD_W - 32}">{p["desc"]}</text>')
        # code snippets
        for j, line in enumerate(p["code"][:2]):
            out.append(f'    <text class="mono code" x="16" y="{128 + j * 20}">{line}</text>')
        # tag + score
        out.append(f'    <line x1="16" y1="170" x2="{CARD_W - 16}" y2="170" stroke="#21262d"/>')
        out.append(f'    <text class="mono tag" x="16" y="188">{p["tag"]}</text>')
        if p["score"] == "160/160":
            out.append(f'    <text class="mono ok" x="{CARD_W - 90}" y="188" text-anchor="end">pana {p["score"]}</text>')
        # animated progress bar at bottom
        out.append(f'    <rect x="16" y="196" width="0" height="4" rx="2" fill="url(#g{i+1})">'
                   f'{anim("width", f"0;{CARD_W - 32}", 0.8, bg + 0.3)}</rect>')
        out.append(f'  </g>')
        out.append(f'  </g>')  # close entrance wrapper

    out.append("</svg>")
    OUT.write_text("\n".join(out))
    print(f"library-demo.svg written ({len(OUT.read_bytes()) // 1024} KB)")


if __name__ == "__main__":
    main()
