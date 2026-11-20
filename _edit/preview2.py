"""Preview: composite overlay over base.mp4 at given times -> one contact-sheet PNG.
python preview.py OUT.png t1,t2,...
Render: python preview.py --frames OUTDIR START END   (transparent PNG frames of the overlay at 24 fps)
"""
import sys, pathlib, subprocess, io
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
FF = r"C:\Users\nidhi\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
FPS = 30

def page_ctx(p):
    b = p.chromium.launch(channel="msedge", headless=True, args=["--force-device-scale-factor=1", "--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.goto((HERE / "overlay2.html").as_uri()); pg.wait_for_function("window.READY===true", timeout=90000)
    return b, pg

def shot(pg, t):
    pg.evaluate(f"seek({t})"); pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
    for k in range(4):
        try: return pg.screenshot(omit_background=True, timeout=120000)
        except Exception as ex: print("retry", t, ex)
    raise RuntimeError(t)

with sync_playwright() as p:
    if sys.argv[1] == "--frames":
        out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        a, e = int(sys.argv[3]), int(sys.argv[4])
        b, pg = page_ctx(p)
        for i in range(a, e):
            (out / f"{i:05d}.png").write_bytes(shot(pg, i / FPS))
            if (i - a) % 120 == 0: print("frame", i, flush=True)
        b.close()
    else:
        out = pathlib.Path(sys.argv[1]); ts = [float(x) for x in sys.argv[2].split(",")]
        b, pg = page_ctx(p)
        tmp = out.parent / "_pv"; tmp.mkdir(exist_ok=True)
        tiles = []
        for k, t in enumerate(ts):
            ov = tmp / f"o{k}.png"; ov.write_bytes(shot(pg, t)); fr = tmp / f"f{k}.png"
            subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(t), "-i", str(HERE / "base2.mp4"), "-i", str(ov), "-filter_complex", "[0:v][1:v]overlay=format=auto,scale=360:-1", "-frames:v", "1", str(fr)], check=True)
            tiles.append(fr)
        b.close()
        args = []
        for f in tiles: args += ["-i", str(f)]
        subprocess.run([FF, "-y", "-loglevel", "error", *args, "-filter_complex", f"hstack=inputs={len(tiles)}", str(out)], check=True)
