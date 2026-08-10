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


def main():
    live = "--live" in sys.argv
    data = json.loads(PKG_JSON.read_text())
    pkgs = data["packages"]
    hdr = data["header"]

    if live:
        for p in pkgs:
            v = fetch_version(p["name"])
            if v and v != p["version"]:
                print(f"  {p['name']}: {p['version']} -> {v}")
                p["version"] = v

    def anim(attr, values, dur, begin, keytimes=None, mode="linear"):
        kt = f' keyTimes="{keytimes}" calcMode="discrete"' if keytimes else f' calcMode="{mode}"'
        return f'<animate attributeName="{attr}" values="{values}"{kt} dur="{dur}s" begin="{begin}s" fill="freeze"/>'

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

    css = f"""
      @font-face {{ font-family:'Space Grotesk'; src:url(data:font/ttf;base64,{FONT_B64}) format('truetype'); font-weight:300 700; }}
      .sg   {{ font-family:{SG}; }}
      .mono {{ font-family:{MONO}; }}
      .title{{ fill:url(#headGrad); font-size:28px; font-weight:700; letter-spacing:1px; }}
      .sub  {{ fill:#8b949e; font-size:14px; }}
      .name {{ fill:#e6edf3; font-size:15px; font-weight:600; }}
      .ver  {{ fill:#020617; font-size:11px; font-weight:700; }}
      .code {{ fill:#79c0ff; font-size:12.5px; }}
      .tag  {{ fill:#8b949e; font-size:12px; }}
      .ok   {{ fill:#27c93f; font-size:12.5px; font-weight:600; }}
    """

    grads = []
    for i, p in enumerate(pkgs):
        grads.append(f'<linearGradient id="g{i+1}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0" stop-color="{p["color"]}"/><stop offset="1" stop-color="{p["color2"]}"/></linearGradient>')
    grad_ids = "".join(grads)

    # header
    out = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="780" height="560" viewBox="0 0 780 560">',
        "  <defs>", f"    <style>{css}</style>",
        f'    <linearGradient id="headGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#7ee787"/><stop offset="1" stop-color="#f778ba"/></linearGradient>',
        grad_ids, "  </defs>",
        f'<text class="sg title" x="20" y="44">{hdr["title"]}</text>',
        f'<text class="sg sub" x="22" y="70">{hdr["sub"]}</text>',
        f'<line x1="20" y1="84" x2="760" y2="84" stroke="#21262d"/>',
        f'<line x1="20" y1="84" x2="20" y2="84" stroke="url(#headGrad)" stroke-width="2">'
        f'{anim("x2", "20;760", 1.4, 0.4)}</line>',
    ]

    positions = [(20, 104), (396, 104), (20, 328), (396, 328)]
    begins = [0.9, 1.1, 1.3, 1.5]
    cid = 0
    for i, (p, (cx, cy), bg) in enumerate(zip(pkgs, positions, begins)):
        out.append(f'  {entrance(f"card{i}", bg)}')
        out.append(f'  <g transform="translate({cx},{cy})">')
        out.append(f'    <rect width="364" height="204" rx="14" fill="#161b22" stroke="#30363d"/>')
        out.append(f'    <rect width="364" height="5" rx="3" fill="url(#g{i+1})"/>')
        out.append(f'    <rect x="14" y="26" width="40" height="40" rx="10" fill="{p["color2"]}" opacity="0.18">'
                   f'<animate attributeName="opacity" values="0.18;0.4;0.18" dur="3s" begin="{bg + 0.5}s" repeatCount="indefinite"/></rect>')
        out.append(f'    <text x="34" y="53" font-size="18" fill="{p["iconColor"]}" text-anchor="middle">{p["icon"]}</text>')
        out.append(f'    <text class="sg name" x="66" y="48">{p["name"]}</text>')
        out.append(f'    <rect x="272" y="30" width="74" height="22" rx="11" fill="url(#g{i+1})"/>')
        out.append(f'    <text class="sg ver" x="309" y="45" text-anchor="middle">v{p["version"]}</text>')
        out.append(f'    <line x1="14" y1="72" x2="350" y2="72" stroke="#21262d"/>')
        for j, line in enumerate(p["code"][:2]):
            out.append(f'    <text class="mono code" x="14" y="{96 + j * 20}">{line}</text>')
        out.append(f'    <text class="mono ok" x="14" y="152">pana {p["score"]}</text>')
        out.append(f'    <rect x="14" y="162" width="0" height="5" rx="3" fill="url(#g{i+1})">'
                   f'{anim("width", "0;336", 1, bg + 0.5)}</rect>')
        out.append(f'    <text class="mono tag" x="14" y="190">{p["tag"]}</text>')
        out.append(f'  </g>')
        out.append(f'  </g>')
        out.append(f'  </g>')  # close entrance wrapper

    out.append("</svg>")
    OUT.write_text("\n".join(out))
    print(f"library-demo.svg written ({len(OUT.read_bytes()) // 1024} KB)")


if __name__ == "__main__":
    main()
