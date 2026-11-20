"""Voiceover-driven edit.  python edit.py [shots|base]
Shots start on voiceover phrase cues (vo_map.json). Each shot = a clip range (optionally reversed / slowed with
motion interpolation) or a still image, with a Ken-Burns move (zoom + pan) and optional shake, graded alike.
Writes edit_tl.json / edit_tl.js (cues + shots) for the graphics layer, renders seg/*.mp4 and base2.mp4 (30 fps).
"""
import json, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
H = pathlib.Path(__file__).resolve().parent
ROOT = H.parent
FF = r"C:\Users\nidhi\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
FPS = 30
VM = json.loads((H / "vo_map.json").read_text(encoding="utf-8"))
CUE = {f"{c['file']}.{c['k']}": c for c in VM["chunks"]}
def C(k, d=-0.06): return round(CUE[k]["start"] + d, 3)
def E(k): return CUE[k]["end"]
END_CARD = 4.2
TOTAL = round(VM["total"] + END_CARD - 0.3, 3)

def clip(n, a, b, **k): return dict(kind="clip", src=n, a=a, b=b, **k)
def img(name, **k): return dict(kind="img", src=name, **k)
BLACK = dict(kind="black")
# kb = (z0, z1, cx0, cy0, cx1, cy1)  centre in source fractions
SHOTS = [
    ("diwali_over", 0.0,          clip(9, 4.6, 7.9, kb=(1.0, 1.15, .5, .5, .5, .45))),
    ("gods_diwali", C("1.2"),     clip(7, 1.0, 4.4, kb=(1.0, 1.1, .5, .45, .5, .4))),
    ("tarakasur",   C("2.0"),     clip(1, 0.0, 3.6, kb=(1.0, 1.15, .5, .62, .5, .6))),
    ("names",       C("2.2"),     img("Scene 1", kb=(1.3, 1.3, .5, .28, .5, .7))),
    ("three_cities",C("2.5"),     img("Scene 1", kb=(1.35, 1.0, .5, .5, .5, .5))),
    ("cities_tilt", C("2.7"),     clip(1, 1.0, 9.6, rev=True, kb=(1.12, 1.12, .5, .45, .5, .5))),
    ("boon",        C("3.0"),     img("Scene 2", kb=(2.0, 2.3, .4, .38, .4, .36))),
    ("align",       C("3.2"),     img("Scene 1", kb=(1.0, 1.06, .5, .5, .5, .5))),
    ("one_arrow",   C("3.3"),     img("Scene 3", kb=(1.5, 1.85, .3, .74, .26, .78))),
    ("brothers",    C("4.0"),     clip(1, 0.3, 2.2, kb=(1.2, 1.4, .5, .62, .5, .62), dim=.45)),
    ("cities3",     C("4.0", 1.38), clip(1, 8.5, 9.7, rev=True, kb=(1.0, 1.2, .5, .35, .5, .35), dim=.45)),
    ("arrow1",      C("4.1"),     clip(3, 4.0, 5.4, kb=(1.6, 1.9, .3, .75, .28, .76), dim=.35)),
    ("impossible",  C("5.0"),     img("Scene 1", kb=(1.0, 1.04, .5, .5, .5, .5), dim=.7, shake=(0.18, 14))),
    ("unless",      C("5.1"),     img("Mahadev", kb=(1.35, 1.15, .5, .35, .5, .4), dim=.55)),
    ("chariot",     C("6.0"),     clip(2, 0.0, 3.0, kb=(1.0, 1.12, .55, .5, .5, .5))),
    ("chariot_list",C("6.1"),     clip(2, 0.0, 10.0, path=[("6.1", 1.2, .38, .5), ("6.2", 1.55, .42, .67), ("6.3", 1.9, .25, .38), ("6.4", 1.6, .55, .23), ("6.5", 1.75, .6, .3)])),
    ("vishnu",      C("6.6"),     img("Scene 3", kb=(1.2, 1.35, .45, .62, .4, .66))),
    ("agni",        C("6.7"),     clip(3, 1.0, 4.0, kb=(1.0, 1.12, .5, .4, .5, .38))),
    ("aligned",     C("7.0"),     clip(4, 0.0, 2.6, kb=(2.3, 2.0, .62, .2, .62, .22))),
    ("pause",       E("7.0") + .25, BLACK),
    ("mahadev",     C("7.1", -.12), clip(4, 1.0, 5.0, kb=(1.12, 1.0, .42, .5, .52, .42))),
    ("blast",       C("7.3"),     clip(4, 6.6, 10.0, kb=(1.0, 1.15, .6, .35, .62, .3), shake=(0.9, 18))),
    ("tripurari",   C("7.5"),     img("Scene 4", kb=(1.35, 1.6, .3, .38, .28, .36))),
    ("celebrate",   C("8.0"),     clip(6, 0.0, 3.6, kb=(1.25, 1.1, .5, .3, .5, .35))),
    ("venue",       C("8.2"),     clip(9, 0.0, 5.0, kb=(1.0, 1.18, .5, .5, .5, .42))),
    ("chandra",     C("8.7"),     img("Chandra Dev", kb=(1.0, 1.12, .5, .42, .5, .4))),
    ("agni_diyas",  C("8.8"),     img("Agni Dev", kb=(1.0, 1.12, .5, .4, .5, .38))),
    ("vayu",        C("8.9"),     clip(5, 4.0, 8.6, kb=(1.0, 1.1, .5, .5, .5, .55))),
    ("vimaan",      C("9.0"),     clip(6, 0.6, 7.6, kb=(1.0, 1.15, .5, .35, .5, .4))),
    ("arrival",     C("10.0"),    clip(7, 2.0, 9.6, kb=(1.0, 1.1, .5, .45, .5, .55))),
    ("dev_deep",    C("10.2"),    clip(9, 0.0, 5.0, kb=(1.12, 1.0, .5, .5, .5, .5))),
    ("purnima",     C("10.4"),    clip(8, 3.2, 7.5, kb=(1.0, 1.1, .5, .45, .55, .4))),
    ("nanak",       C("10.6"),    clip(9, 4.6, 7.9, kb=(1.0, 1.12, .5, .55, .5, .5))),
    ("diya",        C("10.7"),    img("Scene 6", kb=(2.0, 1.7, .3, .66, .35, .64))),
    ("endcard",     VM["total"] - 0.35, img("Scene 9", kb=(1.12, 1.0, .5, .5, .5, .5), blur=18, dim=.35)),
]

GRADE = "eq=contrast=1.05:brightness=0.015:saturation=1.12:gamma=0.98,colorbalance=rm=0.035:gm=0.005:bm=-0.03:rh=0.03:bh=-0.02,unsharp=5:5:0.45:5:5:0"

def shot_list():
    out = []
    for i, (name, t, spec) in enumerate(SHOTS):
        t1 = SHOTS[i + 1][1] if i + 1 < len(SHOTS) else TOTAL
        f0, f1 = round(t * FPS), round(t1 * FPS)
        out.append(dict(name=name, start=f0 / FPS, end=f1 / FPS, frames=f1 - f0, **spec))
    return out

def path_expr(keys, idx):
    # keys: [(t, z, cx, cy)] shot-relative; eased 0.75s moves after each key time, hold otherwise
    expr = f"{keys[-1][idx]}"
    for j in range(len(keys) - 1, 0, -1):
        t0, v0, v1 = keys[j][0], keys[j - 1][idx], keys[j][idx]
        e = f"(0.5-0.5*cos(PI*min(max((t-{t0:.3f})/0.75,0),1)))"
        expr = f"if(lt(t,{t0:.3f}),{v0},{v0}+({v1}-{v0})*{e})" if j == len(keys) - 1 else f"if(lt(t,{t0:.3f}),{v0},if(lt(t,{keys[j+1][0]:.3f}),{v0}+({v1}-{v0})*{e},{expr}))"
    return f"({expr})"

def kb_filters(s, D):
    z0, z1, cx0, cy0, cx1, cy1 = s.get("kb", (1, 1, .5, .5, .5, .5))
    p = f"min(t/{D:.4f},1)"; e = f"(0.5-0.5*cos(PI*{p}))"  # ease in-out
    z = f"({z0}+({z1}-{z0})*{e})"
    shake = s.get("shake")
    sx = sy = "0"
    if shake:
        dur, amp = shake
        dec = f"max(0,1-t/{dur})"
        sx = f"{amp}*{dec}*sin(t*71)"; sy = f"{amp}*{dec}*cos(t*53)"
    cx = f"({cx0}+({cx1}-{cx0})*{e})"; cy = f"({cy0}+({cy1}-{cy0})*{e})"
    if s.get("path"):
        keys = [(max(0, CUE[k]["start"] - .05 - s["start"]), zz, x, y) for k, zz, x, y in s["path"]]
        keys[0] = (0.0,) + keys[0][1:]
        z, cx, cy = path_expr(keys, 1), path_expr(keys, 2), path_expr(keys, 3)
    return (f"scale=w='trunc(BW*{z}/2)*2':h='trunc(BH*{z}/2)*2':eval=frame:flags=lanczos,"
            f"crop=1080:1920:x='max(0,min(iw-1080,{cx}*iw-540+{sx}))':y='max(0,min(ih-1920,{cy}*ih-960+{sy}))'")

def render(s):
    D = s["frames"] / FPS; outp = H / "seg" / f"{s['idx']:03d}_{s['name']}.mp4"
    if s["kind"] == "black":
        vf = None; inp = ["-f", "lavfi", "-i", f"color=c=0x04050c:s=1080x1920:r={FPS}:d={D + .5}"]
    elif s["kind"] == "clip":
        a, b = s["a"], s["b"]; sp = (b - a) / D
        src = ROOT / "Video" / f"Scene {s['src']}.mp4"
        inp = ["-i", str(src)]
        pre = ("delogo=x=560:y=1120:w=135:h=150," if s["src"] != 9 else "")
        chain = f"{pre}trim=start={a}:end={b},setpts=PTS-STARTPTS," + ("reverse," if s.get("rev") else "")
        chain += f"setpts=PTS/{sp:.5f},"
        chain += ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1," if sp < 0.8 else "fps=30,")
        cover = max(1080 / 720, 1920 / 1280)
        vf = chain + kb_filters(s, D).replace("BW", f"{720 * cover:.1f}").replace("BH", f"{1280 * cover:.1f}")
    else:
        src = ROOT / "Images" / f"{s['src']}.png"
        w, h = (2048, 2048) if s["src"] in ("Mahadev", "Chandra Dev", "Agni Dev", "Indra Dev", "Nandi", "Narad Muni", "Vayu dev") else ((768, 1376) if s["src"] == "Scene 2" else (1536, 2752))
        inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{D + .5}", "-i", str(src)]
        cover = max(1080 / w, 1920 / h)
        dl = f"delogo=x={int(w*.87)}:y={int(h*.925)}:w={int(w*.11)}:h={int(h*.06)}," if w != h else ""
        vf = f"{dl}format=yuv420p," + kb_filters(s, D).replace("BW", f"{w * cover:.1f}").replace("BH", f"{h * cover:.1f}")
    post = []
    if vf is not None:
        post.append(GRADE)
        if s.get("blur"): post.append(f"gblur=sigma={s['blur']}")
        if s.get("dim"): post.append(f"eq=brightness={-s['dim'] * .35:.3f}:saturation={1 - s['dim'] * .3:.2f}")
        vf = vf + "," + ",".join(post) + ",vignette=angle=PI/5.5,format=yuv420p"
    cmd = [FF, "-y", "-loglevel", "error", *inp] + (["-vf", vf] if vf else ["-vf", "format=yuv420p"]) + \
          ["-frames:v", str(s["frames"]), "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", str(outp)]
    subprocess.run(cmd, check=True)
    return outp

if __name__ == "__main__":
    sl = shot_list()
    for i, s in enumerate(sl): s["idx"] = i
    tl = {"total": sl[-1]["end"], "vo_total": VM["total"], "cues": {k: {"s": v["start"], "e": v["end"]} for k, v in CUE.items()},
          "shots": [{"name": s["name"], "start": s["start"], "end": s["end"], "a": s.get("a"), "b": s.get("b")} for s in sl]}
    (H / "edit_tl.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    (H / "edit_tl.js").write_text("window.TL=" + json.dumps(tl) + ";", encoding="utf-8")
    for s in sl:
        sp = f"speed {(s['b'] - s['a']) / ((s['frames']) / FPS):.2f}" if s["kind"] == "clip" else ""
        print(f"{s['idx']:2d} {s['name']:12s} {s['start']:7.2f}-{s['end']:7.2f} ({s['end'] - s['start']:4.2f}s) {s['kind']} {sp}")
    print("TOTAL", tl["total"])
    if len(sys.argv) > 1 and sys.argv[1] in ("base", "seg"):
        (H / "seg").mkdir(exist_ok=True)
        only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
        todo = [s for s in sl if not only or s["name"] in only]
        with ThreadPoolExecutor(4) as ex:
            for p in ex.map(render, todo): print("done", p.name, flush=True)
        if sys.argv[1] == "base":
            lst = H / "seg" / "list.txt"
            lst.write_text("".join(f"file '{H / 'seg' / f'{s['idx']:03d}_{s['name']}.mp4'}'\n".replace("\\", "/") for s in sl), encoding="utf-8")
            subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(H / "base2.mp4")], check=True)
            print("base2.mp4 written")
