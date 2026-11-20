"""Builds the v2 soundtrack pieces from edit_tl.json:
  meta2.json -> sfx2.wav (via sfx.py, SFX only)
  music2.wav  (tanpura plucks + soft drone + bansuri-like pad, with the editorial volume envelope)
"""
import json, os, pathlib, subprocess, wave
import numpy as np
H = pathlib.Path(__file__).resolve().parent
TL = json.loads((H / "edit_tl.json").read_text(encoding="utf-8"))
Q = lambda k: TL["cues"][k]["s"]
SH = {s["name"]: s for s in TL["shots"]}
S0 = lambda n: SH[n]["start"]; S1 = lambda n: SH[n]["end"]
bl = SH["blast"]; XPL = bl["start"] + (7.25 - bl["a"]) * (bl["end"] - bl["start"]) / (bl["b"] - bl["a"])
DUR = TL["total"]; SR = 44100

# ---------------- SFX cue list ----------------
E = []
def e(name, t, v=1, p=1): E.append({"t": round(t, 3), "name": name, "v": v, "p": p})
e("ting", .05, .75); e("ting", .35, .7, 1.06); e("ting", .65, .7, 1.12); e("ting", .95, .55, 1.2)  # rapid ting ting ting hook
e("sparkle", Q("1.1") + .2, .4)
e("whoosh", S0("gods_diwali") - .12, .6); e("chime", Q("1.2") + .1, .55); e("templebell", Q("1.2") + .3, .4)
e("boom", S0("tarakasur") + .05, .55); e("thud", Q("2.0") + .25, .45)
for k, pp in (("2.2", 1), ("2.3", 1.12), ("2.4", 1.25)): e("pling", Q(k), .35, pp)
e("whoosh", S0("three_cities") - .1, .45)
for k, pp in (("2.7", 1.25), ("2.8", 1.12), ("2.9", 1.0)): e("pling", Q(k), .35, pp)
e("boom", Q("2.9") + .1, .4)
e("chime", Q("3.0") + .3, .45)
for j in range(3): e("lock", S0("align") + .3 + j * .25, .45, 1 + j * .12)
e("charge", S0("align") + .8, .35)
e("whoosh", S0("one_arrow") - .05, .55)
e("thud", S0("brothers") + .02, .85); e("thud", S0("cities3") + .02, .85); e("thud", S0("arrow1") + .02, .95, 1.1)
e("boom", Q("5.0") + .12, .6); e("buzzer", Q("5.0") + .15, .2)
e("whoosh", S1("unless") - .5, .4, .8)
e("whoosh", S0("chariot") - .12, .55); e("chime", Q("6.0") + .3, .4)
for k, pp in (("6.1", 1), ("6.2", 1.06), ("6.3", 1.12), ("6.4", 1.19), ("6.5", 1.26), ("6.6", 1.33)): e("pop", Q(k) - .03, .45, pp); e("whoosh", Q(k) - .08, .2, 1.4); e("pling", Q(k), .3, pp)
e("fire", S0("agni") + .1, .6); e("whoosh", S0("agni") - .1, .5)
e("chime", Q("7.0") + .2, .35)
P0 = S0("pause"); P1 = S1("pause")
e("riser", P0 - .25, 1.0, (P1 - P0 + .25) / 1.35); e("deepdrum", P0 + .05, 1.0); e("heart", P0 + .1, 1.0); e("deepdrum", P0 + .55, 1.0, .9); e("heart", P0 + .55, .9); e("deepdrum", P0 + 1.0, 1.0, .8)
e("impact", P1 - .02, 1.0)
e("damru", Q("7.1") - .1, .85); e("boom", S0("mahadev") + .02, .7)
e("shankh", Q("7.2") - .05, .6); e("charge", Q("7.2") + .1, .5); mh = SH["mahadev"]; REL = mh["start"] + (3.6 - mh["a"]) * (mh["end"] - mh["start"]) / (mh["b"] - mh["a"]); e("twang", REL, .8); e("whoosh", REL + .05, .9)
e("bigboom", XPL, 1.0); e("impact", XPL + .05, .8); e("bigboom", XPL + .4, .7, .85)
e("gong", max(XPL + .6, Q("7.4") + .3), .9); e("sparkle", Q("7.5"), .4)
e("whoosh", S0("celebrate") - .1, .5); e("sparkle", Q("8.1") + .5, .5)
e("templebell", S0("venue") + .2, .5); e("pop", Q("8.2"), .35)
e("pop", Q("8.5"), .35); e("chime", S0("chandra") + .1, .45); e("fire", S0("agni_diyas") + .1, .45)
e("wind", S0("vayu") + .1, .55); e("pop", Q("8.9") + .1, .35)
e("whoosh", S0("vimaan") - .1, .45); e("whoosh", S0("vimaan") + .6, .3, 1.3); e("buzzer", Q("9.2") + .05, .3); e("thud", Q("9.2") + .05, .5)
e("templebell", S0("arrival") + .2, .45); e("sparkle", S0("arrival") + .6, .4)
e("templebell", S0("dev_deep") + .1, .7); e("shankh", Q("10.2") + .3, .4); e("gong", Q("10.2") + .55, .55)
e("chime", Q("10.4"), .35); e("templebell", Q("10.6"), .35, 1.26)
e("thud", Q("10.7") + .02, .55); e("sparkle", Q("10.8"), .45)
e("chime", S0("endcard") + .25, .55)
for j in range(6): e("pop", S0("endcard") + 1.2 + j * .1, .35, 1 + j * .08)
(H / "meta2.json").write_text(json.dumps({"dur": DUR, "sfx": sorted(E, key=lambda x: x["t"]), "cues": {"pause": 0, "fs1": 0, "fs1end": 0, "fs2": 0}, "nobed": True, "out": "sfx2.wav"}), encoding="utf-8")
env = dict(os.environ, META="meta2.json")
subprocess.run([str(pathlib.Path(os.sys.executable)), str(H / "sfx.py")], check=True, env=env)

# ---------------- music bed ----------------
N = int((DUR + .5) * SR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
def pluck(f, dur=2.6):
    n = int(dur * SR); p = int(SR / f); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):  # Karplus-Strong with a bright jawari-ish decay
        out[i] = buf[i % p]; buf[i % p] = .4985 * (buf[i % p] + buf[(i + 1) % p])
    return out * np.exp(-np.arange(n) / SR / 1.6)
SA = 146.83  # D
notes = [SA * 1.5 / 2, SA, SA, SA / 2]  # Pa Sa' Sa' Sa (tanpura cycle)
cache = {f: pluck(f) for f in set(notes)}
mus = np.zeros(N); step = .62
k = 0; x = 0.0
while x < DUR:
    s = cache[notes[k % 4]]; a = int(x * SR); mus[a:a + len(s)] += s[:max(0, N - a)] * (.9 if k % 4 else 1)
    x += step; k += 1
drone = sum(a * np.sin(2 * np.pi * f * t + .7 * np.sin(2 * np.pi * w * t)) for f, a, w in [(SA / 2, .5, .1), (SA, .7, .13), (SA * 1.5, .35, .17)])
# soft bansuri-like pad: slow breathy sine on Sa-Re-Ga-Pa motif
flute = np.zeros(N)
motif = [(1, 4), (9 / 8, 2), (5 / 4, 2), (3 / 2, 4), (5 / 4, 2), (9 / 8, 2), (1, 6)]
x = 6.0
while x < DUR - 4:
    for r, d in motif:
        a, n = int(x * SR), int(d * .8 * SR); tt = np.arange(n) / SR
        env = np.minimum(tt / .35, 1) * np.minimum((d * .8 - tt) / .5, 1)
        tone = np.sin(2 * np.pi * SA * 2 * r * tt + .004 * np.sin(2 * np.pi * 5 * tt) * 40) + .25 * np.sin(4 * np.pi * SA * 2 * r * tt)
        flute[a:a + n] += (tone * env)[:max(0, N - a)]
        x += d * .8
    x += 4.0
breath = np.convolve(rng.standard_normal(N), np.ones(30) / 30, "same") * .05
flute = (flute + breath * (np.abs(flute) > .05)) * .25
mix = mus * .55 + drone * .1 + flute
# editorial envelope (music stays under the voice)
pts = [(0, 0), (.8, .8), (S0("unless"), .8), (S1("unless") - .3, .25), (S0("chariot") + .3, .75), (S0("aligned"), .7), (S1("aligned") - .9, 0),
       (S0("celebrate") - .1, 0), (S0("celebrate") + 1.2, .8), (S0("dev_deep") - .2, .8), (S0("dev_deep") + 1.5, 1.15), (DUR - 2.2, 1.15), (DUR, 0)]
g = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
mix = mix * g
mix = mix / np.abs(mix).max() * .7
st = np.stack([mix, np.roll(mix, 220)], 1)
with wave.open(str(H / "music2.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print("music2.wav + sfx2.wav", round(DUR, 2), "s")
