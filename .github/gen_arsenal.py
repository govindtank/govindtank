#!/usr/bin/env python3
"""Generate assets/library-demo.svg from .github/packages.json.
Cleaner card design: 2x4 grid, simplified cards, better spacing.
--live: fetch current versions from pub.dev API (fallback to JSON on failure).
Font: .github/fonts/SpaceGrotesk.ttf embedded as data URI.
"""
import base64
import json
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

    # Layout: 2 rows x 4 columns, cleaner proportions
    COLS = 4
    ROWS = 2
    CARD_W = 300
    CARD_H = 140
    GAP_X = 24
    GAP_Y = 24
    START_X = 30
    START_Y = 90
    TOTAL_W = START_X * 2 + COLS * CARD_W + (COLS - 1) * GAP_X
    TOTAL_H = START_Y + ROWS * CARD_H + (ROWS - 1) * GAP_Y + 30

    css = f"""
      @font-face {{ font-family:'Space Grotesk'; src:url(data:font/ttf;base64,{FONT_B64}) format('truetype'); font-weight:300 700; }}
      .sg   {{ font-family:{SG}; }}
      .mono {{ font-family:{MONO}; }}
      .title{{ fill:url(#headGrad); font-size:28px; font-weight:700; letter-spacing:1.5px; }}
      .sub  {{ fill:#8b949e; font-size:13px; }}
      .name {{ fill:#e6edf3; font-size:15px; font-weight:600; }}
      .ver  {{ fill:#0d1117; font-size:11px; font-weight:700; }}
      .tag  {{ fill:#8b949e; font-size:11px; }}
      .publink {{ fill:#58a6ff; font-size:10px; }}
      .section {{ fill:#f778ba; font-size:11px; font-weight:700; letter-spacing:0.8px; }}
    """

    grads = []
    for i, p in enumerate(pkgs):
        grads.append(f'<linearGradient id="g{i+1}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0" stop-color="{p["color"]}"/><stop offset="1" stop-color="{p["color2"]}"/></linearGradient>')
    grad_ids = "".join(grads)

    out = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}" height="{TOTAL_H}" viewBox="0 0 {TOTAL_W} {TOTAL_H}">',
        "  <defs>", f"    <style>{css}</style>",
        f'    <linearGradient id="headGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#7ee787"/><stop offset="1" stop-color="#f778ba"/></linearGradient>',
        grad_ids, "  </defs>",
        f'<text class="sg title" x="30" y="48">{hdr["title"]}</text>',
        f'<text class="sg sub" x="32" y="70">{hdr["sub"]}</text>',
        f'<line x1="30" y1="80" x2="{TOTAL_W - 30}" y2="80" stroke="#21262d"/>',
        f'<line x1="30" y1="80" x2="30" y2="80" stroke="url(#headGrad)" stroke-width="2">'
        f'<animate attributeName="x2" values="30;{TOTAL_W - 30}" dur="0.8s" begin="0.1s" fill="freeze"/></line>',
    ]

    # Section dividers
    pub_indices = [i for i, p in enumerate(pkgs) if p["url"].startswith("https://pub.dev/")]
    jit_indices = [i for i, p in enumerate(pkgs) if not p["url"].startswith("https://pub.dev/")]

    def draw_section_badge(y, label, color):
        return [
            f'<rect x="30" y="{y}" width="90" height="18" rx="9" fill="#161b22" stroke="#30363d"/>',
            f'<rect x="30" y="{y}" width="3" height="18" rx="2" fill="{color}"/>',
            f'<text class="sg section" x="68" y="{y + 13}" text-anchor="middle">{label}</text>',
        ]

    if pub_indices:
        first_pub_y = START_Y + (pub_indices[0] // COLS) * (CARD_H + GAP_Y)
        out.extend(draw_section_badge(first_pub_y - 24, "PUB.DEV", "#22d3ee"))

    if jit_indices:
        first_jit_y = START_Y + (jit_indices[0] // COLS) * (CARD_H + GAP_Y)
        out.extend(draw_section_badge(first_jit_y - 24, "JITPACK", "#fb923c"))

    for i, p in enumerate(pkgs):
        col = i % COLS
        row = i // COLS
        cx = START_X + col * (CARD_W + GAP_X)
        cy = START_Y + row * (CARD_H + GAP_Y)
        registry = "pub.dev" if p["url"].startswith("https://pub.dev/") else "JitPack"

        out.append(f'  <g opacity="0">')
        out.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{0.3 + i * 0.06}s" fill="freeze"/>')
        out.append(f'    <g transform="translate({cx},{cy})">')
        # card background
        out.append(f'      <rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="#161b22" stroke="#30363d"/>')
        # top gradient bar
        out.append(f'      <rect width="{CARD_W}" height="4" rx="2" fill="url(#g{i+1})"/>')
        # icon
        out.append(f'      <rect x="14" y="20" width="36" height="36" rx="8" fill="{p["color2"]}" opacity="0.15"/>')
        out.append(f'      <text x="32" y="42" font-size="16" fill="{p["iconColor"]}" text-anchor="middle">{p["icon"]}</text>')
        # name + version badge
        out.append(f'      <text class="sg name" x="58" y="38">{p["name"]}</text>')
        out.append(f'      <rect x="58" y="44" width="56" height="18" rx="9" fill="url(#g{i+1})"/>')
        out.append(f'      <text class="sg ver" x="86" y="57" text-anchor="middle">{p["version"]}</text>')
        # registry badge
        out.append(f'      <rect x="{CARD_W - 72}" y="20" width="56" height="18" rx="9" fill="#21262d" stroke="#30363d"/>')
        out.append(f'      <text class="sg publink" x="{CARD_W - 44}" y="33" text-anchor="middle">{registry}</text>')
        # divider
        out.append(f'      <line x1="14" y1="68" x2="{CARD_W - 14}" y2="68" stroke="#21262d"/>')
        # description
        out.append(f'      <text class="sg sub" x="14" y="88" width="{CARD_W - 28}">{p["desc"]}</text>')
        # tag
        out.append(f'      <line x1="14" y1="112" x2="{CARD_W - 14}" y2="112" stroke="#21262d"/>')
        out.append(f'      <text class="mono tag" x="14" y="130">{p["tag"]}</text>')
        if p["score"] == "160/160":
            out.append(f'      <text class="mono tag" x="{CARD_W - 70}" y="130" text-anchor="end" fill="#27c93f" font-weight="600">pana {p["score"]}</text>')
        out.append(f'    </g>')
        out.append(f'  </g>')

    out.append("</svg>")
    OUT.write_text("\n".join(out))
    print(f"library-demo.svg written ({len(OUT.read_bytes()) // 1024} KB)")


if __name__ == "__main__":
    main()
