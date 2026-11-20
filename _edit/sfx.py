"""Synthesize the SFX track from meta.json (written by render.py) -> sfx.wav"""
import json, wave, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
SR = 44100
import os
meta = json.loads((HERE / os.environ.get("META", "meta.json")).read_text(encoding="utf-8"))
DUR = meta["dur"] + 0.5; C = meta["cues"]
rng = np.random.default_rng(7)
T = lambda d: np.arange(int(d * SR)) / SR
sine = lambda f, t: np.sin(2 * np.pi * f * t)
def sweep(f0, f1, t): return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, len(t))) / SR)
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def noise(d): return rng.standard_normal(int(d * SR))
def fade(x, a=.005, r=.02):
    n = len(x); e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[n - nr:] = np.linspace(1, 0, nr); return x * e

def ting(p=1): t = T(.9); return (sine(1568 * p, t) + .6 * sine(2349 * p, t) + .25 * sine(3136 * p, t)) * np.exp(-t / .22) * .5
def msg(p=1): t = T(.07); a = sine(880 * p, t) * np.hanning(len(t)); b = sine(1175 * p, t) * np.hanning(len(t)); return np.concatenate([a, b]) * .35
def pop(p=1): t = T(.09); return sweep(380 * p, 950 * p, t) * np.hanning(len(t)) * .5
def pling(p=1): t = T(.6); return (sine(660 * p, t) + .4 * sine(1320 * p, t) + .15 * sine(1980 * p, t)) * np.exp(-t / .16) * .45
def lock(p=1): t = T(.2); return (sine(220 * p, t) * np.exp(-t / .05) + .5 * bp(noise(.2), 1500, 6000) * np.exp(-t / .01)) * .6
def thud(p=1): t = T(.4); return (sweep(110, 42, t) * np.exp(-t / .1) + .35 * bp(noise(.4), 60, 900) * np.exp(-t / .04)) * .9
def boom(p=1): t = T(1.3); return (sweep(70, 32, t) * np.exp(-t / .35) + .3 * bp(noise(1.3), 40, 500) * np.exp(-t / .25)) * .95
def bigboom(p=1): t = T(1.8); return (sweep(85 * p, 30, t) * np.exp(-t / .4) + .5 * bp(noise(1.8), 80, 5000) * np.exp(-t / .45)) * .9
def whoosh(p=1):
    d = .55 / p; n = noise(d); lo = bp(n, 300, 1500); hi = bp(n, 1500, 7000); k = np.linspace(0, 1, len(n))
    return (lo * (1 - k) + hi * k) * np.hanning(len(n)) * .5
def alarm(p=1): t = T(.84); f = np.where((t // .12) % 2 == 0, 740, 990); return fade(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .12)
def fire(p=1):
    t = T(1.2); n = bp(noise(1.2), 400, 5000); cr = np.zeros(len(t))
    for i in rng.integers(0, len(t) - 300, 40): cr[i:i + 300] += np.exp(-np.arange(300) / 40) * rng.uniform(.3, 1)
    return fade((n * .25 + bp(noise(1.2), 1000, 8000) * cr) * np.exp(-t / .5) * .6, .03, .2)
def sparkle(p=1):
    o = np.zeros(int(1.2 * SR))
    for i in range(9):
        t = T(.5); s = sine(rng.uniform(2200, 5200), t) * np.exp(-t / .1) * .22; a = int(i * .045 * SR); o[a:a + len(s)] += s
    return o
def chime(p=1):
    o = np.zeros(int(1.8 * SR))
    for i, f in enumerate([1047, 1319, 1568]):
        t = T(1.4); s = (sine(f, t) + .3 * sine(2 * f, t)) * np.exp(-t / .4) * .25; a = int(i * .08 * SR); o[a:a + len(s)] += s
    return o
def bell(p=1):
    o = np.zeros(int(.7 * SR))
    for i in range(2):
        t = T(.4); s = (sine(540, t) + .7 * sine(805, t) + .3 * sine(1210, t)) * np.exp(-t / .07) * .35; a = int(i * .16 * SR); o[a:a + len(s)] += s
    return o
def heart(p=1):
    o = np.zeros(int(.5 * SR))
    for i, v in enumerate([1, .7]):
        t = T(.25); s = sweep(70, 40, t) * np.exp(-t / .06) * v; a = int(i * .16 * SR); o[a:a + len(s)] += s
    return o
def shankh(p=1):
    t = T(3.0); f = 349 + 20 * np.minimum(t / .6, 1) + 3 * np.sin(2 * np.pi * 5 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR; x = np.sin(ph) + .5 * np.sin(2 * ph) + .28 * np.sin(3 * ph) + .12 * np.sin(4 * ph)
    e = np.minimum(t / .5, 1) * np.minimum((3.0 - t) / .9, 1); return bp(x, 200, 3000) * e * .32
def damru(p=1):
    o = np.zeros(int(2.0 * SR)); tt = 0; gap = .16; i = 0
    while tt < 1.7:
        t = T(.12); s = (sine(190 if i % 2 else 250, t) * np.exp(-t / .03) + .4 * bp(noise(.12), 800, 5000) * np.exp(-t / .008)) * .6
        a = int(tt * SR); o[a:a + len(s)] += s; tt += gap; gap = max(.055, gap * .9); i += 1
    return o
def charge(p=1): t = T(.9); return sweep(180, 1400, t) * (.6 + .4 * sine(18, t)) * np.linspace(0, 1, len(t)) ** 2 * .3
def twang(p=1):
    t = T(.6); f = 140 + 30 * np.exp(-t / .05) * np.sin(2 * np.pi * 30 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + .5 * np.sin(2 * ph) + .3 * np.sin(3 * ph)) * np.exp(-t / .12) * .7
def gong(p=1):
    t = T(4.0); x = sum(a * sine(f, t) * np.exp(-t / d) for f, a, d in [(98, 1, 1.6), (147, .7, 1.3), (203, .5, 1.0), (271, .4, .8), (349, .3, .6), (466, .2, .4), (622, .12, .3)])
    return fade(x * .45, .004, .3)
def templebell(p=1):
    t = T(3.0); x = sum(a * sine(f * p, t) * np.exp(-t / d) for f, a, d in [(587, 1, 1.0), (1180, .5, .7), (1770, .3, .4), (2390, .2, .25), (3010, .1, .15)])
    return fade(x * .3, .002, .2)
def wind(p=1): t = T(2.8); return bp(noise(2.8), 200, 1400) * np.hanning(len(t)) * (.7 + .3 * sine(1.3, t)) * .5
def lightup(p=1):
    o = np.zeros(int(2.2 * SR)); sc = [523, 587, 659, 784, 880, 1047, 1175, 1319, 1568, 1760, 2093, 2349]
    for i, f in enumerate(sc):
        t = T(.5); s = (sine(f, t) + .3 * sine(2 * f, t)) * np.exp(-t / .12) * .22; a = int(i * .115 * SR); o[a:a + len(s)] += s
    return o
def trumpet(p=1):
    t = T(1.0); f = np.interp(t, [0, .25, .6, 1.0], [300, 540, 500, 360]) + 12 * np.sin(2 * np.pi * 9 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 9)); return bp(x, 350, 3500) * np.hanning(len(t)) * .28
def buzzer(p=1): t = T(.36); q = np.sign(sine(150, t)); return fade(q * .1 + bp(q, 300, 2000) * .12)
def swell(p=1): return np.zeros(1)
S = dict(ting=ting, msg=msg, pop=pop, pling=pling, lock=lock, thud=thud, boom=boom, bigboom=bigboom, whoosh=whoosh, alarm=alarm, fire=fire, sparkle=sparkle, chime=chime, bell=bell, heart=heart, shankh=shankh, damru=damru, charge=charge, twang=twang, gong=gong, templebell=templebell, wind=wind, lightup=lightup, trumpet=trumpet, buzzer=buzzer, swell=swell)

def riser(p=1):
    d = 1.35 * p; tt = T(d); k = tt / d
    tone = sweep(55, 420, tt) * (.6 + .4 * np.sin(2 * np.pi * (4 + 22 * k) * tt))
    nz = bp(noise(d), 300, 6000) * k ** 2
    sub = sine(42, tt) * .8
    return fade((tone * .5 + nz * .55 + sub * .5) * (k ** 1.6), .02, .03)
def deepdrum(p=1):
    tt = T(1.1); return (sweep(95 * p, 38, tt) * np.exp(-tt / .28) + .45 * bp(noise(1.1), 40, 700) * np.exp(-tt / .05)) * 1.0
def impact(p=1):
    tt = T(2.2); return fade((sweep(70, 28, tt) * np.exp(-tt / .6) + .6 * bp(noise(2.2), 60, 4000) * np.exp(-tt / .35) + .3 * sine(55, tt) * np.exp(-tt / 1.2)), .002, .4)
S.update(riser=riser, deepdrum=deepdrum, impact=impact)
N = int(DUR * SR); L = np.zeros(N); Rr = np.zeros(N)
for i, e in enumerate(meta["sfx"]):
    s = S[e["name"]](e.get("p", 1)) * e.get("v", 1); a = int(e["t"] * SR); s = s[:max(0, N - a)]
    pan = .5 + .18 * np.sin(i * 1.7); L[a:a + len(s)] += s * (1 - pan) * 1.4; Rr[a:a + len(s)] += s * pan * 1.4
# tanpura-like drone bed (D), ducked for the pause, lifted for Mahadev and the ending
t = np.arange(N) / SR; bed = np.zeros(N)
for f, a, w in [(73.42, .5, .11), (146.83, 1, .17), (220.0, .7, .23), (293.66, .6, .13), (440.0, .22, .19), (587.33, .14, .29)]:
    bed += a * np.sin(2 * np.pi * f * t + 1.5 * np.sin(2 * np.pi * w * t)) * (.6 + .4 * np.sin(2 * np.pi * w * 1.7 * t + f))
g = np.interp(t, [0, 1, 3, C["pause"] - .4, C["pause"] + .2, C["fs1"], C["fs1"] + 1, C["fs1"] + 8, C["fs1end"] + .5, C["fs2"], C["fs2"] + 2.5, DUR - 2.5, DUR],
              [0, .05, .035, .035, 0, 0, .075, .075, .035, .035, .085, .085, 0])
bed = bed * g
if not meta.get("nobed"): L += bed; Rr += np.roll(bed, 300)
# soft high shimmer pad in the ending
pad = sum(np.sin(2 * np.pi * f * t + i) * (.5 + .5 * np.sin(2 * np.pi * .21 * t + i * 2)) for i, f in enumerate([587.33, 739.99, 880.0, 1174.66]))
pg = np.interp(t, [0, C["fs2"], C["fs2"] + 3, DUR - 2.5, DUR], [0, 0, .022, .022, 0])
if not meta.get("nobed"): L += pad * pg; Rr += np.roll(pad * pg, 500)
mix = np.stack([L, Rr], 1); mix = np.tanh(mix * 1.1); mix = mix / np.abs(mix).max() * .84
with wave.open(str(HERE / meta.get("out", "sfx.wav")), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("sfx.wav", round(DUR, 2), "s,", len(meta["sfx"]), "events")
