"""Original 31s stadium-style track for the St. Peter's Sports Meet reel. 120 BPM, D major. Drop at 3s, riser into highlights (14.5s), end card at 27.5s."""
import sys, numpy as np, wave
SR = 44100; BPM = 120; B = 60 / BPM; DUR = 31.0
N = int(SR * DUR); rng = np.random.default_rng(3)
mix = np.zeros((N, 2))

def put(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[:j - i] * gain
    mix[i:j, 0] += s * (1 - max(0, pan)); mix[i:j, 1] += s * (1 + min(0, pan))

def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def hz(m): return 440 * 2 ** ((m - 69) / 12)

def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 1.0

def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    nz = rng.normal(0, 1, n)
    nz = np.convolve(nz, [1, -0.6], 'same')
    e = np.exp(-t * 22) + 0.6 * np.exp(-((t - 0.012) ** 2) / 1e-5)
    return nz * e * 0.35

def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR); t = np.arange(n) / SR
    nz = np.diff(rng.normal(0, 1, n + 1))
    return nz * np.exp(-t * (14 if open_ else 70)) * 0.12

def pluck(m, dur=0.9, bright=0.5, bend=True):
    """Karplus-Strong string with a little sitar-like buzz and pitch bend-in."""
    f = hz(m); n = int(dur * SR)
    p = int(SR / f); buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out = out + 0.25 * np.tanh(out * 4)  # jawari-style buzz
    return out * env(n, 0.002, dur * 0.6)

def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.5 * s) * env(n, 0.004, dur * 0.7) * 0.55

def pad(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        for det in (-0.08, 0.08):
            f = hz(m + det); s += ((t * f) % 1 * 2 - 1)
    # simple one-pole lowpass
    a = 0.04; y = np.zeros(n); acc = 0
    for i in range(n): acc += a * (s[i] - acc); y[i] = acc
    fade = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return y * fade * 0.05

# chords: Dm  Bb  F  C  (one per bar = 2s)
CH = [(50, [62, 66, 69]), (47, [59, 62, 66]), (43, [59, 62, 67]), (45, [61, 64, 69])]  # D  Bm  G  A
# hook motif (16th grid within 2 bars), D minor pentatonic with a b2 colour
HOOK = [(0, 74), (0.5, 76), (0.75, 78), (1.0, 81), (1.5, 78), (2.0, 76), (2.5, 74), (3.0, 76), (3.5, 69)]

bars = int(DUR / (4 * B)) + 1
for bar in range(bars):
    t0 = bar * 4 * B
    root, notes = CH[bar % 4]
    if t0 < 28:
        put(pad(notes, 4 * B), t0, 1.0)
    for beat in range(4):
        tb = t0 + beat * B
        if tb >= DUR: break
        main = 3.0 <= tb < 27.5
        if main:
            put(kick(), tb, 0.9)
            if beat in (1, 3): put(clap(), tb, 0.8)
            put(bass(root - 12 if beat % 2 == 0 else root, B * 0.9), tb + (0 if beat % 2 == 0 else B / 2), 1.0)
            put(hat(True), tb + B / 2, 0.8, 0.3)
        for k in range(4):  # 16th hats with swing
            th = tb + k * B / 4 + (0.02 if k % 2 else 0)
            if tb < 3.0 and k % 2: continue
            put(hat(), th, 0.9 if k % 2 == 0 else 0.6, -0.3)

# hook: 2-bar phrase, plays in intro (soft), throughout main, and rings on end card
for phrase in range(0, 13):
    t0 = phrase * 8 * B
    if t0 >= DUR: break
    g = 0.35 if t0 < 3 else (0.5 if t0 < 27.5 else 0.45)
    for off, m in HOOK:
        put(pluck(m, 0.8), t0 + off * B, g, 0.15)

# riser into the group shot (12s) and impact on the cut
n = int(1.5 * SR); t = np.arange(n) / SR
riser = rng.normal(0, 1, n) * (t / 1.5) ** 2 * 0.15
put(riser, 13.0, 1.0)
for tt in (3.0, 9.5, 15.5, 27.5):
    n = int(1.2 * SR); t = np.arange(n) / SR
    put(rng.normal(0, 1, n) * np.exp(-t * 4) * 0.12, tt, 1.0)

# 'we will' style stomp-clap accents through the highlights section
for k in range(int(15.5 / B), int(27.5 / B)):
    tb = k * B
    if k % 2 == 0: put(kick(), tb, 0.5)
    else: put(clap(), tb, 1.0, 0.2); put(clap(), tb + 0.03, 0.7, -0.2)

# master: gentle fade in/out + soft clip
t = np.arange(N) / SR
mix *= np.minimum(1, t / 0.15)[:, None] * np.minimum(1, (DUR - t) / 1.8)[:, None]
mix = np.tanh(mix * 1.1)
mix /= np.max(np.abs(mix)) / 0.89
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', DUR)
