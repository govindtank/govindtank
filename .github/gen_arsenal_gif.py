#!/usr/bin/env python3
"""Generate an optimized animated GIF for The Arsenal.

Style: dark cyber grid, scanlines, typing reveal, neon accents.
Optimized for GitHub README display (~500 KB target).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "assets" / "library-demo.gif"

W, H = 480, 270
DURATION = 0.18  # seconds per frame
LOOP = 0
FONT_SIZE = 12
MONO_FONT_SIZE = 11

# Palette
BG = (13, 17, 23)
GRID = (22, 27, 34)
ACCENT_CYAN = (34, 211, 238)
ACCENT_GREEN = (126, 231, 135)
ACCENT_PINK = (247, 120, 186)
ACCENT_ORANGE = (251, 146, 60)
ACCENT_BLUE = (56, 189, 248)
ACCENT_LIME = (163, 230, 53)
ACCENT_PURPLE = (210, 168, 255)
ACCENT_ROSE = (244, 114, 182)
TEXT_MAIN = (230, 237, 243)
TEXT_DIM = (139, 148, 158)
TEXT_CODE = (121, 192, 255)

# Load fonts
def load_font(size, mono=False):
    paths = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFMono-Regular.otf",
        "/System/Library/Fonts/Monaco.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    if mono:
        for p in paths:
            if Path(p).exists():
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
    else:
        paths = [
            "/System/Library/Fonts/SFCompact.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ] + paths
        for p in paths:
            if Path(p).exists():
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
    return ImageFont.load_default()


FONT = load_font(FONT_SIZE)
MONO_FONT = load_font(MONO_FONT_SIZE, mono=True)
TITLE_FONT = load_font(18)
SMALL_FONT = load_font(9)

PKGS = [
    {
        "name": "country_mobile_validator",
        "ver": "0.2.0",
        "color": ACCENT_CYAN,
        "code": "validateForCountry('IN','98765')",
        "tag": "pub.dev · Dart",
    },
    {
        "name": "flutter_whisper",
        "ver": "0.1.0",
        "color": ACCENT_GREEN,
        "code": "WhisperStream.start(audioBytes)",
        "tag": "pub.dev · Dart",
    },
    {
        "name": "waveform_pro",
        "ver": "1.0.2",
        "color": ACCENT_PINK,
        "code": "WaveformView(painter: GpuPainter())",
        "tag": "pub.dev · Dart",
    },
    {
        "name": "quote_painter",
        "ver": "0.1.0",
        "color": ACCENT_PURPLE,
        "code": "QuoteCanvas.render('Code is poetry')",
        "tag": "pub.dev · Dart",
    },
    {
        "name": "capture-improvement-kotlin",
        "ver": "v1.0.0",
        "color": ACCENT_ORANGE,
        "code": "BlurDetector.analyze(frame)",
        "tag": "JitPack · Kotlin",
    },
    {
        "name": "cmp-clipboard",
        "ver": "v1.0.0",
        "color": ACCENT_BLUE,
        "code": "rememberClipboardManager()",
        "tag": "JitPack · KMP",
    },
    {
        "name": "cmp-keyboard",
        "ver": "v1.0.0",
        "color": ACCENT_LIME,
        "code": "KeyboardAwareColumn(modifier)",
        "tag": "JitPack · KMP",
    },
    {
        "name": "cmp-linked-text",
        "ver": "v1.0.0",
        "color": ACCENT_ROSE,
        "code": "LinkedText('https://...')",
        "tag": "JitPack · KMP",
    },
]

# Layout: 4 cols x 2 rows
COLS = 4
ROWS = 2
CARD_W = 105
CARD_H = 95
GAP_X = 8
GAP_Y = 8
START_X = 12
START_Y = 44

TOTAL_FRAMES = 55


def draw_grid(draw):
    for x in range(0, W, 26):
        draw.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 26):
        draw.line([(0, y), (W, y)], fill=GRID, width=1)


def draw_scanline(img, frame_idx):
    y = int((frame_idx / 45) * H) % H
    arr = img.copy()
    draw = ImageDraw.Draw(arr)
    for i in range(3):
        draw.line([(0, y - i), (W, y - i)], fill=ACCENT_CYAN, width=1)
    return arr


def draw_card(draw, cx, cy, pkg, progress):
    if progress <= 0:
        return
    x1, y1 = cx, cy
    x2, y2 = cx + CARD_W, cy + CARD_H

    # Background
    draw.rectangle([x1, y1, x2, y2], fill=(22, 27, 34))
    # Top accent bar
    bar_h = max(1, int(3 * min(1, progress)))
    draw.rectangle([x1, y1, x2, y1 + bar_h], fill=pkg["color"])
    # Border
    if progress > 0.5:
        border_alpha = int(255 * min(1, (progress - 0.5) * 2))
        draw.rectangle([x1, y1, x2 - 1, y2 - 1], outline=(48, 54, 61, border_alpha), width=1)

    # Icon circle
    if progress > 0.2:
        icon_alpha = int(255 * min(1, (progress - 0.2) * 2))
        draw.ellipse([x1 + 5, y1 + 7, x1 + 23, y1 + 25], fill=(*pkg["color"][:3], icon_alpha // 3))

    # Name
    if progress > 0.3:
        name_alpha = int(255 * min(1, (progress - 0.3) * 2))
        draw.text((x1 + 29, y1 + 10), pkg["name"], fill=(*TEXT_MAIN[:3], name_alpha), font=FONT)

    # Version badge
    if progress > 0.4:
        ver_alpha = int(255 * min(1, (progress - 0.4) * 2))
        draw.rectangle([x1 + 29, y1 + 20, x1 + 78, y1 + 31], fill=(*pkg["color"][:3], ver_alpha))
        draw.text((x1 + 35, y1 + 21), pkg["ver"], fill=(*BG[:3], ver_alpha), font=SMALL_FONT)

    # Divider
    if progress > 0.5:
        draw.line([(x1 + 5, y1 + 38), (x2 - 5, y1 + 38)], fill=(33, 38, 45, int(255 * min(1, progress))), width=1)

    # Tag
    if progress > 0.6:
        tag_alpha = int(255 * min(1, (progress - 0.6) * 2))
        draw.text((x1 + 5, y1 + 44), pkg["tag"], fill=(*TEXT_DIM[:3], tag_alpha), font=SMALL_FONT)

    # Code snippet
    if progress > 0.7:
        code_alpha = int(255 * min(1, (progress - 0.7) * 2))
        draw.text((x1 + 5, y1 + 60), pkg["code"][:24], fill=(*TEXT_CODE[:3], code_alpha), font=MONO_FONT)

    # Bottom progress bar
    if progress > 0.1:
        bar_w = int((CARD_W - 10) * min(1, progress))
        draw.rectangle([x1 + 5, y2 - 7, x1 + 5 + bar_w, y2 - 3], fill=(*pkg["color"][:3], int(255 * min(1, progress))))


def render_frame(frame_idx):
    img = Image.new('RGBA', (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_grid(draw)

    # Header
    draw.text((12, 10), "THE ARSENAL", fill=ACCENT_CYAN, font=TITLE_FONT)
    draw.text((14, 30), "8 libraries · 4 pub.dev + 4 JitPack · Flutter + Kotlin Multiplatform", fill=TEXT_DIM, font=SMALL_FONT)

    # Cards animation: staggered reveal
    for i, pkg in enumerate(PKGS):
        col = i % COLS
        row = i // COLS
        cx = START_X + col * (CARD_W + GAP_X)
        cy = START_Y + row * (CARD_H + GAP_Y)

        trigger = 6 + i * 6
        duration = 16
        progress = max(0.0, min(1.0, (frame_idx - trigger) / duration))

        if progress > 0:
            draw_card(draw, cx, cy, pkg, progress)

    # Scanline effect
    if frame_idx < 55:
        img = draw_scanline(img, frame_idx)

    # Convert to RGB for GIF
    rgb = Image.new('RGB', (W, H), BG)
    rgb.paste(img, mask=img.split()[3])
    return rgb


print("Generating frames...")
frames = []
for i in range(TOTAL_FRAMES):
    frame = render_frame(i)
    frames.append(frame)

print(f"Writing GIF ({len(frames)} frames, {W}x{H})...")
frames[0].save(
    str(OUT_PATH),
    save_all=True,
    append_images=frames[1:],
    duration=int(DURATION * 1000),
    loop=LOOP,
    optimize=True,
    disposal=2,
)
size_kb = OUT_PATH.stat().st_size / 1024
print(f"library-demo.gif written ({size_kb:.1f} KB)")
