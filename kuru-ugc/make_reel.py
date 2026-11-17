import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = '/root/.claude/uploads/09445aaf-b27a-5d89-8aaa-1da8b6de828c/7721168f-image.jpg'
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
img = Image.open(SRC).convert('RGB')
IW, IH = img.size

BIG = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 68)
MID = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 54)
MONO = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 34)
HUGE = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 120)

OX = (155, 29, 42); THREAD = (246, 243, 234); INK = (27, 25, 34)

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def box(cx, cy, h):
    h = min(h, IH); w = h * 9 / 16
    if w > IW: w = IW; h = w * 16 / 9
    x = min(max(cx - w / 2, 0), IW - w); y = min(max(cy - h / 2, 0), IH - h)
    return (x, y, x + w, y + h)

def lerp_box(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))

def wrap(text, font, maxw, d):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines

def caption(frame, text, y, alpha, font=BIG, light=True):
    """Instagram 'classic with background' style: one rounded box per line."""
    if alpha <= 0: return
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    lines = [l for part in text.split('|') for l in wrap(part.strip(), font, W - 220, d)]
    lh = font.size + 30; dy = int((1 - alpha) * 24)
    bg = THREAD if light else INK; fg = INK if light else THREAD
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=font); x = (W - tw) / 2; yy = y + i * lh + dy
        d.rounded_rectangle((x - 26, yy - 12, x + tw + 26, yy + font.size + 18), 18, fill=bg + (int(235 * alpha),))
        d.text((x, yy), ln, font=font, fill=fg + (int(255 * alpha),))
    frame.alpha_composite(layer)

rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 9, (H, W, 1)).astype(np.int16) for _ in range(4)]

def finish(frame, i):
    a = np.asarray(frame.convert('RGB')).astype(np.int16) + GRAIN[i % 4]
    return np.clip(a, 0, 255).astype(np.uint8).tobytes()

# scenes: (duration, start_box, end_box, caption, caption_y)
S = [
    (3.2, box(830, 640, IH), box(840, 560, 1050), 'Third person today to ask|where this shirt is from', 240),
    (3.0, box(780, 790, 760), box(760, 800, 520), '“Is it printed?”', 300),
    (3.0, box(760, 800, 520), box(780, 820, 430), 'No. Every dot is|a hand stitch.', 300),
    (3.2, box(1010, 800, 470), box(1030, 790, 390), 'A different embroidery|on every panel', 300),
    (3.0, box(830, 910, 420), box(830, 905, 300), 'Hours of handwork.|One pair of hands.', 300),
    (3.2, box(800, 720, 700), box(830, 640, IH), 'Made in small batches.|No two the same.', 1440),
]
END = 4.0

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
    '-r', str(FPS), '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', OUT],
    stdin=subprocess.PIPE)

i = 0
for dur, b0, b1, text, ty in S:
    n = int(dur * FPS)
    for k in range(n):
        t = k / (n - 1)
        bx = lerp_box(b0, b1, ease(t))
        fr = img.resize((W, H), Image.LANCZOS, box=bx).convert('RGBA')
        # soft top/bottom vignette for text legibility
        caption(fr, text, ty, ease((k / FPS) / 0.35))
        ff.stdin.write(finish(fr, i)); i += 1

# end card with stitch border drawing itself
n = int(END * FPS)
for k in range(n):
    s = k / FPS
    fr = Image.new('RGBA', (W, H), OX + (255,)); d = ImageDraw.Draw(fr)
    m = 60; per = 2 * ((W - 2 * m) + (H - 2 * m)); drawn = per * ease(s / 1.4)
    pts = [(m, m), (W - m, m), (W - m, H - m), (m, H - m), (m, m)]
    pos = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = abs(x1 - x0) + abs(y1 - y0)
        for p in range(0, int(L), 26):
            if pos + p > drawn: break
            f0, f1 = p / L, min(p + 15, L) / L
            d.line((x0 + (x1 - x0) * f0, y0 + (y1 - y0) * f0, x0 + (x1 - x0) * f1, y0 + (y1 - y0) * f1), fill=THREAD, width=4)
        pos += L
    a1 = ease((s - 0.3) / 0.5); a2 = ease((s - 0.9) / 0.5); a3 = ease((s - 1.5) / 0.5)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    t1 = 'KURU STUDIO'; ld.text(((W - ld.textlength(t1, font=MONO)) / 2, 700), t1, font=MONO, fill=THREAD + (int(255 * a1),))
    for j, ln in enumerate(['Wearable', 'art, by hand.']):
        ld.text(((W - ld.textlength(ln, font=HUGE)) / 2, 790 + j * 140 + int((1 - a2) * 30)), ln, font=HUGE, fill=THREAD + (int(255 * a2),))
    fr.alpha_composite(lay)
    caption(fr, '@kurustudio.clothing.in', 1180, a3, font=MID)
    caption(fr, 'DM “KURU” for the lookbook', 1290, ease((s - 2.0) / 0.5), font=MID, light=False)
    ff.stdin.write(finish(fr, i)); i += 1

ff.stdin.close(); ff.wait()
print('frames', i, 'seconds', i / FPS)
