"""Transcribe VO/BG Scene 1..10 with word timestamps -> vo_words.json"""
import json, pathlib, sys, subprocess
import numpy as np
from faster_whisper import WhisperModel
H = pathlib.Path(__file__).resolve().parent
VO = H.parent / "VO"
FF = r"C:\Users\nidhi\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"

def load(f):
    raw = subprocess.run([FF, "-loglevel", "error", "-i", str(f), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

model = WhisperModel("small", device="cpu", compute_type="int8")
out = {}
for i in range(1, 11):
    f = VO / f"BG Scene {i}.m4a"
    segs, info = model.transcribe(load(f), language="hi", word_timestamps=True, vad_filter=False, beam_size=5,
                                  initial_prompt="Hinglish in Roman script. Narad Muni, Tripurasur, Tarakaksh, Kamalaksh, Vidyunmali, Mahadev, Tripurari, Kashi, Dev Deepawali, Kartik Purnima, Agni Dev, Vayu Dev, Chandra Dev, Nandi, Indra Dev, Airavat, vimaan.")
    words, lines = [], []
    for s in segs:
        lines.append({"s": round(s.start, 2), "e": round(s.end, 2), "text": s.text.strip()})
        for w in (s.words or []):
            words.append({"s": round(w.start, 2), "e": round(w.end, 2), "w": w.word.strip()})
    out[i] = {"lines": lines, "words": words}
    sys.stdout.buffer.write((f"\n=== VO{i} ===\n" + "\n".join(f"{l['s']:6.2f}-{l['e']:6.2f}  {l['text']}" for l in lines) + "\n").encode("utf-8"))
    sys.stdout.flush()
(H / "vo_words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
