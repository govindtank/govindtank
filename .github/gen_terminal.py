#!/usr/bin/env python3
"""Generate assets/terminal-intro.svg — animated CLI-install profile hero.
Typewriter = discrete clip-width steps, one per character. Font embedded as data URI."""
import base64

FONT_B64 = open('/tmp/sg.b64').read().strip()
W, H = 820, 600
MONO = "'JetBrains Mono','Fira Code','SF Mono',Menlo,monospace"
SG = "'Space Grotesk',system-ui,sans-serif"

def anim(attr, values, dur, begin, keytimes=None):
    kt = f' keyTimes="{keytimes}" calcMode="discrete"' if keytimes else ''
    return (f'<animate attributeName="{attr}" values="{values}"{kt} '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite" fill="freeze"/>')

def clip_def(cid, y, h, n, cw, dur, begin):
    widths = ';'.join(str(round(i * cw, 1)) for i in range(n + 1))
    kts = ';'.join(str(round(i / n, 4)) for i in range(n + 1))
    return (f'<clipPath id="{cid}"><rect x="0" y="{y}" width="0" height="{h}">'
            f'{anim("width", widths, dur, begin, kts)}</rect></clipPath>')

def type_line(x, y, cmd, begin, dur, cid, cw=9.2):
    n = len(cmd)
    return (f'<text class="prompt" x="{x}" y="{y}">$</text>'
            f'<text class="cmd" x="{x + 20}" y="{y}" clip-path="url(#{cid})">{cmd}</text>'
            + clip_def(cid, y - 16, 22, n, cw, dur, begin))

def fade(x, y, cls, text, begin, anchor=None, dy=0):
    a = f' text-anchor="{anchor}"' if anchor else ''
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" '
            f'dur="0.22s" begin="{begin}s" repeatCount="indefinite" fill="freeze"/>'
            f'<text class="{cls}" x="{x}" y="{y}"{a}>{text}</text></g>')

def fade_multi(x, y, begin, parts, dy=0):
    # parts: list of (cls, text, offset_x)
    inner = ''.join(f'<text class="{c}" x="{x + dx}" y="{y}">{t}</text>' for c, t, dx in parts)
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" '
            f'dur="0.22s" begin="{begin}s" repeatCount="indefinite" fill="freeze"/>'
            f'{inner}</g>')

body = []
d = body.append

# --- command 1: install
d(type_line(28, 84, 'curl -fsSL govindtank.dev/install | sh', 0.3, 1.2, 'ct1'))

# --- installing banner
d(fade(28, 114, 'dim', '&#9656; installing govindtank-profile v2.1.0', 1.7))
d('<rect x="28" y="126" width="440" height="9" rx="4.5" fill="#21262d"/>')
d(f'<rect x="28" y="126" width="0" height="9" rx="4.5" fill="url(#progGrad)">'
  f'{anim("width", "0;110;220;330;440", 1.6, 1.8)}</rect>')

# --- extract lines
d(fade(28, 154, 'dim', '<tspan class="ok">&#10003; </tspan>extracting skills — flutter · android · kotlin', 3.6))
d(fade(28, 176, 'dim', '<tspan class="ok">&#10003; </tspan>linking — python · on-device AI · data dashboards', 3.9))
d(fade(28, 198, 'dim', '<tspan class="ok">&#10003; </tspan>building — 50+ repos · 4 pub.dev packages · 2 apps', 4.2))

# --- command 2: profile
d(type_line(28, 234, 'govindtank --profile', 4.8, 0.8, 'ct2'))
d('<text class="hdrbig" x="28" y="266" clip-path="url(#ct3)" filter="url(#glow)">GOVIND TANK</text>')
d(clip_def('ct3', 236, 38, 11, 22, 0.7, 5.9))
d(fade(30, 300, 'role', 'Mobile Architect · Developer · Technical Consultant', 6.2))
d(fade(30, 324, 'dim', 'flutter · android · kotlin · python · on-device AI · automations', 6.5))

# --- command 3: libs
d(type_line(28, 360, 'govindtank libs', 7.2, 0.6, 'ct4'))
libs = [
    ('country_mobile_validator', 'v0.2.0', '160/160'),
    ('flutter_whisper',          'v0.1.0', '160/160'),
    ('waveform_pro',             'v1.0.0', '160/160'),
    ('quote_painter',            'v0.1.0', '160/160'),
]
for i, (nm, ver, score) in enumerate(libs):
    y = 386 + i * 24
    d(fade_multi(44, y, 8.0 + i * 0.28, [
        ('cmd', nm, 0), ('dim', ver, 330), ('ok', score, 400),
    ]))

# --- command 4: whoami
d(type_line(28, 488, 'govindtank whoami', 9.6, 0.7, 'ct5'))
d(fade(30, 514, 'dim', '&#8220;automate the boring, ship the real, measure everything&#8221;', 10.5))

# --- done
d(fade(28, 558, 'ok', '&#10003; install complete — govindtank-profile v2.1.0 is live', 11.3))

defs = f'''
  <defs>
    <style>
      @font-face {{ font-family:'Space Grotesk'; src:url(data:font/ttf;base64,{FONT_B64}) format('truetype'); font-weight:300 700; }}
      .bg {{ fill:#0d1117; }}
      .dotr {{ fill:#ff5f56; }} .doty {{ fill:#ffbd2e; }} .dotg {{ fill:#27c93f; }}
      .mono {{ font-family:{MONO}; }}
      .sg {{ font-family:{SG}; }}
      .prompt {{ fill:#39d353; font-size:15px; font-weight:600; font-family:{MONO}; }}
      .cmd {{ fill:#e6edf3; font-size:15px; font-weight:600; font-family:{MONO}; }}
      .dim {{ fill:#8b949e; font-size:14px; font-family:{MONO}; }}
      .ok {{ fill:#27c93f; font-size:14px; font-weight:600; font-family:{MONO}; }}
      .role {{ fill:#7ee787; font-size:17px; font-weight:500; font-family:{SG}; }}
      .hdrbig {{ fill:url(#nameGrad); font-size:32px; font-weight:700; letter-spacing:1.5px; font-family:{SG}; }}
    </style>
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#22d3ee"/><stop offset="0.55" stop-color="#7ee787"/><stop offset="1" stop-color="#f778ba"/>
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
'''

frame = f'''
  <rect class="bg" width="{W}" height="{H}" rx="16"/>
  <rect x="0" y="0" width="{W}" height="48" rx="16" fill="url(#winGrad)"/>
  <rect x="0" y="44" width="{W}" height="4" fill="#161b22"/>
  <circle class="dotr" cx="22" cy="24" r="7"/><circle class="doty" cx="46" cy="24" r="7"/><circle class="dotg" cx="70" cy="24" r="7"/>
  <text class="mono" x="410" y="31" text-anchor="middle" fill="#8b949e" font-size="12px">govindtank@github — installer</text>
  <g clip-path="url(#bodyClip)">
    <rect width="{W}" height="{H}" fill="url(#scanGrad)">
      <animate attributeName="y" from="-{H}" to="{H}" dur="7s" repeatCount="indefinite"/>
    </rect>
  </g>
'''

scan = f'''<linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#22d3ee" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#22d3ee" stop-opacity="0.07"/>
      <stop offset="1" stop-color="#22d3ee" stop-opacity="0"/>
    </linearGradient>'''

cursor = f'''<rect x="470" y="548" width="11" height="22" rx="2" fill="#39d353">
    <animate attributeName="opacity" values="1;0;1" dur="1s" begin="11.6s" repeatCount="indefinite"/>
  </rect>'''

svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
       f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       + defs.replace('</defs>', scan + '\n  </defs>')
       + frame + '\n'.join(body) + cursor + '\n</svg>\n')

with open('/Users/govind/workspace/govindtank-profile/assets/terminal-intro.svg', 'w') as f:
    f.write(svg)
print('written', len(svg) // 1024, 'KB')
