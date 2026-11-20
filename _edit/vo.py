"""Tighten + speed-adjust the 10 VO files into one track.
python vo.py chunks   -> print phrase chunks with transcript text
python vo.py build    -> vo_track.wav + vo_map.json (phrase output times)
"""
import json, pathlib, re, subprocess, sys
H = pathlib.Path(__file__).resolve().parent
VO = H.parent / "VO"
FF = r"C:\Users\nidhi\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
WORDS = json.loads((H / "vo_words.json").read_text(encoding="utf-8"))

# per file: speed, lead silence before the file (seconds of output), max gap kept between phrases
CFG = {
    1: dict(speed=1.10, lead=0.30, gap=0.40),
    2: dict(speed=1.30, lead=0.20, gap=0.12),
    3: dict(speed=1.30, lead=0.20, gap=0.12),
    4: dict(speed=1.15, lead=0.20, gap=0.15),
    5: dict(speed=1.15, lead=0.25, gap=0.30),
    6: dict(speed=1.12, lead=0.35, gap=0.38),
    7: dict(speed=1.08, lead=0.30, gap=0.18),
    8: dict(speed=1.30, lead=0.45, gap=0.12),
    9: dict(speed=1.25, lead=0.20, gap=0.14),
    10: dict(speed=1.22, lead=0.45, gap=0.18),
}
# gaps to keep longer: (file, chunk index after which) -> output seconds
SPECIAL = {(7, 0): 1.7, (10, 1): 0.3, (10, 3): 0.28,
           (2, 7): 0.55, (2, 8): 0.55, (2, 9): 0.15,
           (7, 1): 0.5, (7, 2): 0.3,
           (8, 2): 0.2, (8, 4): 0.55, (8, 5): 0.2, (8, 6): 0.55, (8, 7): 0.35}
TAIL = 0.15  # padding kept around each phrase

def silences(f):
    r = subprocess.run([FF, "-hide_banner", "-i", str(f), "-af", "silencedetect=n=-38dB:d=0.33", "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    dur = float(re.search(r"Duration: (\d+):(\d+):([0-9.]+)", r.stderr).groups()[2])
    if len(en) < len(st): en.append(dur)
    return list(zip(st, en)), dur

def chunks(i):
    f = VO / f"BG Scene {i}.m4a"
    sil, dur = silences(f)
    pts, cur = [], 0.0
    for a, b in sil:
        if a > cur + 0.05: pts.append([cur, a])
        cur = b
    if cur < dur - 0.05: pts.append([cur, dur])
    out = []
    for a, b in pts:
        a2, b2 = max(0, a - TAIL), min(dur, b + TAIL)
        if out and a2 <= out[-1][1]: out[-1][1] = b2
        else: out.append([a2, b2])
    return out, f

def text_of(i, a, b):
    return " ".join(w["w"] for w in WORDS[str(i)]["words"] if a - .05 <= (w["s"] + w["e"]) / 2 <= b + .05)

def build(write=True):
    t, pieces, cmap = 0.0, [], []
    for i in range(1, 11):
        cf = CFG[i]; ch, f = chunks(i); t += cf["lead"]
        keep = [(k, ab) for k, ab in enumerate(ch) if text_of(i, *ab).strip() or (ab[1] - ab[0]) > .8]
        ch = [ab for _, ab in keep]; ks = [k for k, _ in keep]
        for n, (a, b) in enumerate(ch):
            k = ks[n]
            d = (b - a) / cf["speed"]
            cmap.append({"file": i, "k": k, "start": round(t, 3), "end": round(t + d, 3), "text": text_of(i, a, b)})
            pieces.append((f, a, b, cf["speed"], t))
            t += d
            if n < len(ch) - 1: t += SPECIAL.get((i, k), cf["gap"])
    total = round(t + 0.3, 3)
    if write:
        import numpy as np, wave
        SR = 44100
        dec = {}
        def pcm(f, sp):
            key = (str(f), sp)
            if key not in dec:
                raw = subprocess.run([FF, "-loglevel", "error", "-i", str(f), "-af", f"atempo={sp}", "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
                dec[key] = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
            return dec[key]
        buf = np.zeros(int((total + 1) * SR), np.float32)
        for f, a, b, sp, st in pieces:
            x = pcm(f, sp)[int(a / sp * SR):int(b / sp * SR)].copy()
            n = len(x); r = min(n // 2, int(.05 * SR))
            if r: x[:r] *= np.linspace(0, 1, r); x[-r:] *= np.linspace(1, 0, r)
            o = int(st * SR); buf[o:o + n] += x
        tmp = H / "_vo_raw.wav"
        with wave.open(str(tmp), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(tmp), "-af",
                        f"atrim=duration={total},afftdn=nf=-30,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,loudnorm=I=-15:TP=-1.5:LRA=7",
                        "-ar", str(SR), "-ac", "2", str(H / "vo_track.wav")], check=True)
        (H / "vo_map.json").write_text(json.dumps({"total": total, "chunks": cmap}, ensure_ascii=False, indent=1), encoding="utf-8")
    return cmap, total

if __name__ == "__main__":
    cmap, total = build(write=sys.argv[1] == "build")
    for c in cmap: sys.stdout.buffer.write(f"VO{c['file']}.{c['k']}  {c['start']:7.2f}-{c['end']:7.2f}  {c['text']}\n".encode("utf-8"))
    print("TOTAL", total)
