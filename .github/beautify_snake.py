#!/usr/bin/env python3
"""Upgrade Platane/snk SVG: dark gradient bg, glowing gradient snake, animated hue cycle."""
import re
import sys

DEFS = """<defs>
<linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#0f172a"/>
  <stop offset="1" stop-color="#020617"/>
</linearGradient>
<linearGradient id="snakeGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#22d3ee"/>
  <stop offset="0.5" stop-color="#4ade80"/>
  <stop offset="1" stop-color="#22d3ee"/>
</linearGradient>
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="2.5" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>
<rect class="bg" x="-16" y="-32" width="880" height="192" rx="14" fill="url(#bgGrad)"/>"""

STYLE_OVERRIDE = """<style>
:root{--cb:#1b1f2322;--ce:#151b23;--c0:#0e4429;--c1:#006d32;--c2:#26a641;--c3:#39d353}
.g-snake{animation:snakehue 10s linear infinite}
@keyframes snakehue{0%{filter:hue-rotate(0deg)}100%{filter:hue-rotate(360deg)}}
.s{fill:url(#snakeGrad)}
</style>"""


def main(path):
    with open(path) as f:
        svg = f.read()
    if "snakeGrad" in svg:
        print("already beautified")
        return
    svg = re.sub(r"(<desc>.*?</desc>)", r"\1\n" + DEFS, svg, count=1, flags=re.S)
    svg = svg.replace(
        '<rect class="s s0"', '<g class="g-snake" filter="url(#glow)">\n<rect class="s s0"', 1
    )
    svg = svg.replace("</svg>", STYLE_OVERRIDE + "</g>\n</svg>")
    with open(path, "w") as f:
        f.write(svg)
    print("beautified:", path)


if __name__ == "__main__":
    main(sys.argv[1])
