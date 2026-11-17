import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = '/root/.claude/uploads/09445aaf-b27a-5d89-8aaa-1da8b6de828c/7721168f-image.jpg'
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
U='/root/.claude/uploads/09445aaf-b27a-5d89-8aaa-1da8b6de828c/'
IM = {}
def L(k, f): IM[k] = Image.open(U + f + '-image.jpg').convert('RGB')
for k, f in [(1,'97ba374c'),(3,'e651325b'),(4,'02ff629b'),(5,'4e300d09'),(6,'0d78aa74'),(7,'d44bc4ec'),(8,'d3dc2cca'),
             (9,'3fc84847'),(10,'9af1d12d'),(11,'a87e271c'),(13,'1e5716d5'),(14,'a9c344d8'),(15,'587e7cc6')]: L(k, f)
REG = {3: (60, 60, 1020, 1020), 8: (60, 60, 1020, 1020), 4: (0, 0, 690, 935), 15: (0, 0, 748, 893)}
BIG = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 68)
MID = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 54)
MONO = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 34)
HUGE = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 120)

OX = (155, 29, 42); THREAD = (246, 243, 234); INK = (27, 25, 34)

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def box(k, cx, cy, h):
    W0, H0 = IM[k].size
    rx0, ry0, rx1, ry1 = REG.get(k, (0, 0, W0, H0))
    RW, RH = rx1 - rx0, ry1 - ry0
    h = min(h, RH); w = h * 9 / 16
    if w > RW: w = RW; h = w * 16 / 9
    x = min(max(cx - w / 2, rx0), rx1 - w); y = min(max(cy - h / 2, ry0), ry1 - h)
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
    (9, 3.0, box(9, 780, 1040, 2080), box(9, 760, 900, 1500), 'This shirt takes up to|2 months to make', 260),
    (1, 2.0, box(1, 900, 1100, 1500), box(1, 950, 1150, 1000), 'Every inch is|embroidered by hand', 260),
    (7, 2.0, box(7, 800, 1000, 1600), box(7, 820, 1050, 1100), 'Knots. Loops. Crosses.|All by hand.', 260),
    (10, 2.0, box(10, 900, 1000, 1700), box(10, 980, 920, 900), 'The design grows|as it is stitched', 260),
    (5, 2.0, box(5, 560, 700, 1448), box(5, 600, 560, 1000), 'No two pieces|are identical', 260),
    (6, 2.0, box(6, 540, 560, 1000), box(6, 540, 724, 1448), 'Even the back|is a canvas', 260),
    (14, 2.0, box(14, 560, 724, 1448), box(14, 500, 520, 900), 'Once made, that design|is never repeated', 260),
    (4, 2.0, box(4, 340, 470, 935), box(4, 340, 420, 760), 'Every piece is|its own composition', 1450),
    (15, 2.0, box(15, 370, 446, 893), box(15, 370, 400, 700), 'Linen. Hand embroidered.|Made in India.', 1450),
    (8, 2.0, box(8, 540, 540, 960), box(8, 520, 520, 820), 'Wear it on the street', 1500),
    (11, 2.0, box(11, 512, 760, 1535), box(11, 530, 620, 1200), 'to the party', 1500),
    (3, 2.0, box(3, 540, 540, 960), box(3, 520, 480, 800), 'or on a slow Sunday', 1500),
    (13, 2.0, box(13, 512, 768, 1536), box(13, 512, 640, 1150), 'Made individually|to order', 1450),
]
END = 4.0

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
    '-r', str(FPS), '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', OUT],
    stdin=subprocess.PIPE)

i = 0
for k, dur, b0, b1, text, ty in S:
    src = IM[k]
    n = int(dur * FPS)
    for k in range(n):
        t = k / (n - 1)
        bx = lerp_box(b0, b1, ease(t))
        fr = src.resize((W, H), Image.LANCZOS, box=bx).convert('RGBA')
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
    for j, ln in enumerate(['Art, cut', 'to be worn.']):
        ld.text(((W - ld.textlength(ln, font=HUGE)) / 2, 790 + j * 140 + int((1 - a2) * 30)), ln, font=HUGE, fill=THREAD + (int(255 * a2),))
    fr.alpha_composite(lay)
    caption(fr, '@kurustudio.clothing.in', 1180, a3, font=MID)
    caption(fr, 'DM to order', 1290, ease((s - 2.0) / 0.5), font=MID, light=False)
    ff.stdin.write(finish(fr, i)); i += 1

ff.stdin.close(); ff.wait()
print('frames', i, 'seconds', i / FPS)
