"""Sports-day themed 9:16 reel for St. Peter's College, Agra - 180th Annual Sports Meet.
All visuals are drawn in code (track, lanes, badges, emoji stickers) - no photos are used.
Text content (guests, date, theme, programme highlights) comes from the invitation card.
usage: python3 make_reel.py out_video_noaudio.mp4 [still_dir]
"""
import subprocess, sys, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
W, H, FPS = 1080, 1920, 30

FB = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
FK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
if not os.path.exists(FK): FK = FB
F_CAP = ImageFont.truetype(FB, 64); F_SM = ImageFont.truetype(FB, 44); F_XS = ImageFont.truetype(FB, 36)
F_MEGA = ImageFont.truetype(FK, 200); F_HUGE = ImageFont.truetype(FK, 140); F_BIG = ImageFont.truetype(FK, 96)
F_MID = ImageFont.truetype(FK, 72); F_DAY = ImageFont.truetype(FK, 300)
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)

NAVY = (22, 32, 70); MAROON = (150, 34, 40); SAFFRON = (240, 140, 36); CREAM = (252, 245, 228)
TRACK = (196, 74, 52); GRASS = (46, 140, 78); SKY = (48, 120, 200); INK = (18, 20, 32); WHITE = (255, 255, 255)
ELEM = [('EARTH', (120, 84, 50), '⛰️'), ('WATER', (40, 120, 200), '💧'), ('FIRE', (230, 90, 30), '🔥'),
        ('AIR', (110, 180, 200), '🌬️'), ('SPACE', (70, 50, 140), '✨')]

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))
def pop(t):
    t = max(0, min(1, t)); return 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2 if t < 1 else 1
def ctext(d, y, s, f, fill):
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)

def wrap(text, font, maxw, d):
    out = []
    for part in text.split('|'):
        cur = ''
        for wd in part.split():
            t = (cur + ' ' + wd).strip()
            if d.textlength(t, font=font) <= maxw: cur = t
            else: out.append(cur); cur = wd
        out.append(cur)
    return out

def caption(fr, text, y, a, font=F_CAP, bg=WHITE, fg=INK):
    """Instagram 'text with background' pills, popping in."""
    if a <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lines = wrap(text, font, W - 200, d); lh = font.size + 30
    s = pop(a); dy = int((1 - min(1, a * 1.3)) * 30); al = min(1, a * 2)
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=font); x = (W - tw) / 2; yy = y + i * lh + dy
        d.rounded_rectangle((x - 28, yy - 12, x + tw + 28, yy + font.size + 20), 20, fill=bg + (int(245 * al),))
        d.text((x, yy), ln, font=font, fill=fg + (int(255 * al),))
    if abs(s - 1) > 0.01:
        lay = lay.resize((int(W * s), int(H * s)), Image.BILINEAR)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tmp.paste(lay, ((W - lay.width) // 2, int((y + lh) * (1 - s)))); lay = tmp
    fr.alpha_composite(lay)

_emo = {}
def sticker(fr, ch, x, y, a, size=150, rot=0):
    if a <= 0: return
    if ch not in _emo:
        im = Image.new('RGBA', (180, 180), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=EMO, embedded_color=True)
        _emo[ch] = im.crop(im.getbbox())
    e = _emo[ch]; s = max(0.01, pop(a)) * size / max(e.size)
    im = e.resize((max(1, int(e.width * s)), max(1, int(e.height * s))), Image.LANCZOS)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    fr.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

def wobble(t, amp=7):  # handheld feel
    return (amp * math.sin(t * 2.1) + amp * .5 * math.sin(t * 5.3 + 1),
            amp * math.cos(t * 1.7) + amp * .5 * math.sin(t * 4.1 + 2))

# ---------------------------------------------------------------- backgrounds
def bg_track(t, speed=1.0, sky=SKY):
    """Perspective running track rushing toward camera."""
    fr = Image.new('RGBA', (W, H), sky + (255,)); d = ImageDraw.Draw(fr)
    hz = 620; vx = W / 2
    for i in range(10):  # sky gradient bands
        c = tuple(int(sky[k] + (255 - sky[k]) * i / 14) for k in range(3))
        d.rectangle((0, hz - 62 * (10 - i), W, hz - 62 * (9 - i)), fill=c)
    for k in range(18):  # tree line / stands
        x = k * 64; d.rectangle((x, hz - 40 - 18 * (1 + math.sin(k * 1.7)), x + 44, hz), fill=(30, 90, 55))
    d.polygon([(0, hz), (W, hz), (W, H), (0, H)], fill=GRASS)
    L, R = vx - 120, vx + 120
    d.polygon([(L, hz), (R, hz), (W + 900, H), (-900, H)], fill=TRACK)
    n = 6
    for i in range(n + 1):  # lane lines
        f = i / n; d.line((L + (R - L) * f, hz, -900 + (W + 1800) * f, H), fill=WHITE, width=6)
    for k in range(14):  # moving distance markers
        z = ((k / 14) + t * 0.55 * speed) % 1; y = hz + (H - hz) * z ** 2.2
        if y < hz + 4: continue
        f = (y - hz) / (H - hz)
        d.line((L + (-900 - L) * f, y, R + (W + 900 - R) * f, y), fill=(255, 255, 255, 70), width=max(1, int(2 + 10 * f)))
    return fr

def bg_burst(c1, c2, t, rays=16):
    """Rotating sunburst rays - sports poster energy."""
    fr = Image.new('RGBA', (W, H), c1 + (255,)); d = ImageDraw.Draw(fr)
    cx, cy, R = W / 2, H * 0.45, 2400; a0 = t * 0.35
    for i in range(rays):
        a = a0 + i * 2 * math.pi / rays; b = a + math.pi / rays
        d.polygon([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a)), (cx + R * math.cos(b), cy + R * math.sin(b))], fill=c2)
    return fr

def lanes_strip(fr, y, t, h=260):
    """Horizontal track strip with runners dashing across."""
    d = ImageDraw.Draw(fr); d.rectangle((0, y, W, y + h), fill=TRACK)
    for i in range(4): d.line((0, y + i * h / 3, W, y + i * h / 3), fill=WHITE, width=5)
    for i in range(3):
        x = W + 150 - ((t * (520 + i * 90) + i * 300) % (W + 300))
        sticker(fr, '🏃', x, y + h / 6 + i * h / 3, 1, size=int(h / 3.2))

CONF = np.random.default_rng(5).uniform(0, 1, (70, 5))
def confetti(fr, t, a=1.0):
    if a <= 0: return
    d = ImageDraw.Draw(fr); cols = [SAFFRON, WHITE, (60, 170, 90), (60, 130, 220), MAROON]
    for x, y0, sp, ph, c in CONF:
        y = (y0 * H + t * (300 + sp * 500)) % (H + 60) - 30
        xx = x * W + 30 * math.sin(t * 3 + ph * 6); r = 10 + 8 * abs(math.sin(t * 4 + ph * 9))
        d.rectangle((xx - r, y - 6, xx + r, y + 6), fill=cols[int(c * 5) % 5] + (int(230 * a),))

def progress(fr, t, total):
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((40, 40, W - 40, 50), 5, fill=(255, 255, 255, 90))
    d.rounded_rectangle((40, 40, 40 + (W - 80) * min(1, t / total), 50), 5, fill=(255, 255, 255, 235))

rng = np.random.default_rng(11)
GRAIN = [rng.normal(0, 4, (H, W, 1)).astype(np.int16) for _ in range(4)]

# ---------------------------------------------------------------- scenes
def sc_hook(s, T):
    fr = bg_track(T, 1.6)
    caption(fr, "POV: it's Sports Day|at St. Peter's", 200, s / 0.25, bg=WHITE)
    for j, ln in enumerate(['180th', 'ANNUAL', 'SPORTS MEET']):
        f = [F_MEGA, F_HUGE, F_BIG][j]; aa = ease((s - 0.15 - j * 0.15) / 0.3)
        if aa <= 0: continue
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        y = [700, 920, 1080][j] + (1 - aa) * 80
        ctext(ld, y + 8, ln, f, INK + (int(150 * aa),)); ctext(ld, y, ln, f, (CREAM if j else SAFFRON) + (int(255 * aa),))
        fr.alpha_composite(lay)
    sticker(fr, '🏆', 880, 640, (s - 0.6) / 0.35, size=170, rot=-12)
    sticker(fr, '🏃', W / 2 + 260 * math.sin(s * 2), 1560, (s - 0.3) / 0.3, size=240)
    return fr

def sc_theme(s, T):
    fr = bg_burst(NAVY, (32, 46, 96), T); d = ImageDraw.Draw(fr)
    caption(fr, "This year's theme", 200, s / 0.25, font=F_SM, bg=SAFFRON)
    a = ease((s - 0.1) / 0.3)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ctext(ld, 400 + (1 - a) * 60, 'INDIANA', F_HUGE, SAFFRON + (int(255 * a),))
    ctext(ld, 570 + (1 - a) * 60, 'The Symphony of Panchtatva', F_SM, CREAM + (int(255 * a),))
    fr.alpha_composite(lay)
    for i, (name, col, em) in enumerate(ELEM):  # five element badges orbit in
        aa = ease((s - 0.3 - i * 0.12) / 0.3)
        if aa <= 0: continue
        ang = -math.pi / 2 + i * 2 * math.pi / 5 + s * 0.4
        cx, cy, r = W / 2 + 310 * math.cos(ang), 1180 + 310 * math.sin(ang), 115 * pop(aa)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=CREAM, width=6)
        sticker(fr, em, cx, cy - 12, 1, size=int(105 * pop(aa)))
        tw = d.textlength(name, font=F_XS); d.text((cx - tw / 2, cy + r + 6), name, font=F_XS, fill=CREAM)
    caption(fr, 'Earth · Water · Fire · Air · Space', 1700, (s - 0.9) / 0.3, font=F_XS, bg=WHITE)
    return fr

def sc_date(s, T):
    fr = bg_track(T, 0.6, sky=(240, 150, 60)); d = ImageDraw.Draw(fr)
    caption(fr, 'Save the date', 200, s / 0.25, bg=INK, fg=WHITE)
    a = pop((s - 0.1) / 0.35); dx, dy = wobble(T)
    if a > 0.05:
        cw, ch = 640 * a, 700 * a; x0, y0 = W / 2 - cw / 2 + dx, 760 - ch / 2 + dy
        d.rounded_rectangle((x0 + 14, y0 + 18, x0 + cw + 14, y0 + ch + 18), 40, fill=(0, 0, 0, 90))
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 40, fill=CREAM)
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + 170 * a), 40, fill=MAROON)
        d.rectangle((x0, y0 + 120 * a, x0 + cw, y0 + 170 * a), fill=MAROON)
        if a > 0.9:
            ctext(d, y0 + 40, 'SATURDAY', F_MID, WHITE)
            ctext(d, y0 + 190, '21', F_DAY, INK)
            ctext(d, y0 + 560, 'NOVEMBER 2026', F_SM, MAROON)
    caption(fr, '12:30 PM  ·  College Ground', 1230, (s - 0.5) / 0.3, bg=SAFFRON)
    sticker(fr, '⏱️', 880, 420, (s - 0.4) / 0.3, size=150, rot=12)
    return fr

def guest_card(fr, s, T, role, name, sub, em, col, em2):
    d = ImageDraw.Draw(fr); a = ease((s - 0.05) / 0.3); dx, dy = wobble(T, 5)
    cw, ch = 820, 900; x0, y0 = (W - cw) / 2 + dx + (1 - a) * 1000, 500 + dy
    d.rounded_rectangle((x0 + 16, y0 + 20, x0 + cw + 16, y0 + ch + 20), 48, fill=(0, 0, 0, 100))
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 48, fill=CREAM, outline=SAFFRON, width=10)
    d.rounded_rectangle((x0 + 40, y0 + 40, x0 + cw - 40, y0 + 520), 34, fill=col)
    for k in range(6):  # lane stripes inside the top panel
        yy = y0 + 110 + k * 70; d.line((x0 + 40, yy, x0 + cw - 40, yy), fill=tuple(min(255, c + 30) for c in col), width=5)
    sticker(fr, em, x0 + cw / 2, y0 + 280, (s - 0.25) / 0.3, size=260)
    pw = d.textlength(role, font=F_SM) + 60
    d.rounded_rectangle((x0 + (cw - pw) / 2, y0 + 560, x0 + (cw + pw) / 2, y0 + 640), 40, fill=INK)
    d.text((x0 + (cw - pw) / 2 + 30, y0 + 572), role, font=F_SM, fill=SAFFRON)
    lines = wrap(name, F_MID, cw - 80, d)
    for i, ln in enumerate(lines):
        d.text((x0 + (cw - d.textlength(ln, font=F_MID)) / 2, y0 + 670 + i * 86), ln, font=F_MID, fill=INK)
    for i, ln in enumerate(wrap(sub, F_XS, cw - 100, d)):
        d.text((x0 + (cw - d.textlength(ln, font=F_XS)) / 2, y0 + 700 + len(lines) * 86 + i * 46), ln, font=F_XS, fill=MAROON)
    if em2: sticker(fr, em2, x0 + cw - 30, y0 + 20, (s - 0.5) / 0.3, size=150, rot=14)

def sc_guest(p):
    def f(s, T):
        fr = bg_burst(p['bg'], tuple(min(255, c + 22) for c in p['bg']), T)
        caption(fr, p['cap'], 200, s / 0.25, bg=p['cb'], fg=p['cf'])
        guest_card(fr, s, T, p['role'], p['name'], p['sub'], p['em'], p['col'], p.get('em2'))
        return fr
    return f

def sc_expect(s, T):
    fr = Image.new('RGBA', (W, H), NAVY + (255,)); d = ImageDraw.Draw(fr)
    for i, (_, c, _e) in enumerate(ELEM):
        w = W * ease((s - i * 0.05) / 0.35); d.rectangle((0, 1250 + i * 34, w, 1250 + i * 34 + 22), fill=c)
    a = ease(s / 0.25)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for j, ln in enumerate(('WHAT TO', 'EXPECT')): ctext(ld, 700 + j * 170 + (1 - a) * 60, ln, F_HUGE, CREAM + (int(255 * a),))
    fr.alpha_composite(lay)
    sticker(fr, '👇', W / 2, 1120 + 14 * math.sin(s * 10), (s - 0.2) / 0.3, size=170)
    return fr

# highlight motifs - each draws a small animated sports scene
def m_torch(fr, s, T):
    d = ImageDraw.Draw(fr); cx, cy = W / 2, 1150
    for k in range(5):
        r = 260 - k * 40 + 18 * math.sin(T * 9 + k)
        d.ellipse((cx - r, cy - r * 1.3, cx + r, cy + r * 0.7),
                  fill=[(255, 120, 20, 60), (255, 150, 30, 80), (255, 180, 40, 110), (255, 210, 80, 150), (255, 240, 170, 200)][k])
    sticker(fr, '🔥', cx, cy - 40 + 10 * math.sin(T * 7), 1, size=300)
    sticker(fr, '🏃', W / 2 - 360 + 720 * ease(s / 1.5), 1620, 1, size=200)
def m_march(fr, s, T):
    for row, ch in enumerate(['🚩', '🎺', '🥁']):
        for k in range(5):
            x = 140 + k * 200 + ((T * 160) % 200) - 100; y = 1000 + row * 230 + 14 * abs(math.sin(T * 8 + k))
            sticker(fr, ch, x, y, 1, size=150)
def m_balloons(fr, s, T):
    for k in range(12):
        x = 80 + (k * 97) % (W - 160); y = 1850 - ((T * 260 + k * 140) % 1350)
        sticker(fr, '🎈', x + 20 * math.sin(T * 2 + k), y, 1, size=130 + (k % 3) * 30)
    sticker(fr, '🎷', W / 2, 1650, 1, size=200)
def m_hurdles(fr, s, T):
    lanes_strip(fr, 1000, T, 450); d = ImageDraw.Draw(fr)
    for k in range(3):
        x = (k * 380 - T * 600) % (W + 200) - 100
        d.rectangle((x, 1110, x + 14, 1330), fill=WHITE); d.rectangle((x - 70, 1110, x + 84, 1145), fill=SAFFRON)
    for j, t in enumerate(['110m H', '100m', '200m', '400m']):
        a = ease((s - 0.2 - j * 0.1) / 0.25)
        if a <= 0: continue
        x = 70 + j * 240; d.rounded_rectangle((x, 1600, x + 220, 1690), 45, fill=(WHITE if j % 2 else SAFFRON) + (int(255 * a),))
        d.text((x + 110 - d.textlength(t, font=F_XS) / 2, 1624), t, font=F_XS, fill=INK + (int(255 * a),))
def m_elements(fr, s, T):
    d = ImageDraw.Draw(fr)
    for i, (name, col, em) in enumerate(ELEM):
        a = pop((s - i * 0.1) / 0.3)
        if a <= 0: continue
        cx = 150 + i * 195; cy = 1200 + 60 * math.sin(T * 3 + i); r = 88 * a
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=CREAM, width=5)
        sticker(fr, em, cx, cy, 1, size=int(100 * a))
    sticker(fr, '💃', W / 2, 1580, 1, size=220)
def m_relay(fr, s, T):
    lanes_strip(fr, 1000, T * 1.2, 420)
    sticker(fr, '🏅', W / 2, 1640, (s - 0.2) / 0.3, size=200, rot=-10)
def m_tug(fr, s, T):
    d = ImageDraw.Draw(fr); sh = 60 * math.sin(T * 3)
    d.line((60, 1180, W - 60, 1180 + 10 * math.sin(T * 5)), fill=(150, 110, 60), width=22)
    d.rectangle((W / 2 + sh - 10, 1140, W / 2 + sh + 10, 1220), fill=WHITE)
    for k in range(3):
        sticker(fr, '💪', 150 + k * 110 + sh, 1090, 1, size=120); sticker(fr, '💪', W - 150 - k * 110 + sh, 1090, 1, size=120)
    sticker(fr, '🚴', (T * 500) % (W + 300) - 150, 1530, 1, size=230)
def m_finale(fr, s, T):
    confetti(fr, T)
    for k, ch in enumerate(['💃', '🕺', '💃']):
        sticker(fr, ch, 250 + k * 290, 1300 + 40 * math.sin(T * 8 + k * 2), 1, size=240)
    sticker(fr, '🦁', W / 2, 1640, (s - 0.3) / 0.3, size=170)

HL = [  # (caption, emoji, bg, motif) - highlights from the programme
    ('The Torch & lighting the Meet Flame', '🔥', (120, 30, 20), m_torch),
    ('March Past & Parade', '🥁', NAVY, m_march),
    ('Balloons up with the Band', '🎈', (30, 120, 200), m_balloons),
    ('Hurdles & sprints on the track', '🏃', (40, 120, 70), m_hurdles),
    ('Tattvam: The Five Elements', '🌊', (70, 50, 140), m_elements),
    ("4x100 Relay & the Old Boys' Race", '🏅', (200, 110, 20), m_relay),
    ('Tug-of-War & Cycle Race', '🚴', MAROON, m_tug),
    ('Grand Finale: Mission Courage', '💃', (20, 24, 50), m_finale),
]
def sc_hl(i):
    cap, em, bgc, motif = HL[i]
    def f(s, T):
        fr = bg_burst(bgc, tuple(min(255, c + 25) for c in bgc), T)
        motif(fr, s, T)
        d = ImageDraw.Draw(fr); tag = f'{i + 1}/8'
        d.rounded_rectangle((70, 150, 70 + d.textlength(tag, font=F_SM) + 48, 224), 37, fill=SAFFRON)
        d.text((94, 160), tag, font=F_SM, fill=INK)
        caption(fr, cap, 330, s / 0.25, font=F_CAP, bg=WHITE)
        sticker(fr, em, W - 150, 190 + 8 * math.sin(s * 8), (s - 0.1) / 0.3, size=140, rot=10)
        return fr
    return f

def sc_end(s, T):
    fr = bg_track(T, 0.4, sky=NAVY); d = ImageDraw.Draw(fr)
    a = ease(s / 0.4); y = 330  # finish-line ribbon snapping across
    for k in range(int(W / 40) + 1):
        if k * 40 > W * a: break
        for r in range(2): d.rectangle((k * 40, y + r * 40, k * 40 + 40, y + r * 40 + 40), fill=WHITE if (k + r) % 2 else INK)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((70, 450, W - 70, 1200), 50, fill=NAVY + (int(225 * ease((s - 0.1) / 0.3)),))
    for j, (ln, f, c, t0) in enumerate([("ST. PETER'S", F_BIG, CREAM, 0.2), ('COLLEGE, AGRA', F_BIG, CREAM, 0.3),
                                         ('180th Annual Sports Meet', F_SM, SAFFRON, 0.5)]):
        aa = ease((s - t0) / 0.35)
        if aa <= 0: continue
        yy = [480, 590, 715][j] + (1 - aa) * 40
        ctext(ld, yy + 6, ln, f, INK + (int(160 * aa),)); ctext(ld, yy, ln, f, c + (int(255 * aa),))
    fr.alpha_composite(lay)
    caption(fr, 'See you on the ground!', 880, (s - 0.8) / 0.3, bg=SAFFRON)
    caption(fr, 'Sat, 21 Nov · 12:30 PM', 1000, (s - 1.1) / 0.3, font=F_SM, bg=WHITE)
    caption(fr, 'Bring your invite card for entry', 1110, (s - 1.4) / 0.3, font=F_SM, bg=INK, fg=WHITE)
    sticker(fr, '🏁', W / 2, 1450 + 10 * math.sin(s * 5), (s - 1.7) / 0.35, size=200)
    confetti(fr, T, ease((s - 0.8) / 0.5))
    return fr

SCENES = [
    (3.0, sc_hook), (2.0, sc_theme), (2.5, sc_date),
    (2.0, sc_guest(dict(cap='Presided by', role='PRESIDENT', name='The Most Rev. Dr. Raphy Manjaly',
                        sub='Archbishop of Agra & Patron of the College', em='🙏', col=NAVY, bg=(30, 60, 120), cb=WHITE, cf=INK))),
    (3.0, sc_guest(dict(cap='WAIT... the Chief Guest is a cricketer?!', role='CHIEF GUEST', name='Mr. Praveen Kumar',
                        sub='Former Indian Cricketer', em='🏏', col=(40, 120, 70), bg=MAROON, cb=SAFFRON, cf=INK, em2='🔥'))),
    (2.0, sc_guest(dict(cap='Guest of Honour', role='GUEST OF HONOUR', name="The Most Rev. Dr. Albert D'Souza",
                        sub='Archbishop Emeritus of Agra', em='✨', col=(70, 50, 140), bg=(20, 90, 110), cb=WHITE, cf=INK))),
    (1.0, sc_expect),
] + [(1.5, sc_hl(i)) for i in range(8)] + [(3.5, sc_end)]
TOTAL = sum(d for d, _ in SCENES)

if STILLS: os.makedirs(STILLS, exist_ok=True)
ff = None if STILLS else subprocess.Popen(
    ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
     '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)

i = 0
for dur, fn in SCENES:
    n = int(round(dur * FPS))
    for k in range(n):
        if STILLS and k != int(n * 0.8): i += 1; continue
        s = k / FPS; fr = fn(s, i / FPS)
        if k < 3 and i > 0: fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(120 * (1 - k / 3)))))
        progress(fr, i / FPS, TOTAL)
        if STILLS: fr.convert('RGB').resize((540, 960)).save(f'{STILLS}/{i:04d}.jpg')
        else:
            a = np.asarray(fr.convert('RGB')).astype(np.int16) + GRAIN[i % 4]
            ff.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
        i += 1
if ff: ff.stdin.close(); ff.wait()
print('frames', i, 'seconds', i / FPS)
