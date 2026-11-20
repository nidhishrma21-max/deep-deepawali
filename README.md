# Bhagwan Ki Diwali – Dev Deepawali Short

A 9:16 YouTube Short (1080×1920, 30 fps, about 2 minutes) telling the Tripurasur / Tripurari story behind Dev Deepawali, with Hinglish voiceover, English on-screen graphics, music and sound effects.

**Final video:** `Dev Deepawali - Final (with VO).mp4`

## Folders

| Folder / file | What it is |
| --- | --- |
| `Video/` | The 9 source scene clips (720×1280) |
| `Images/` | Scene stills and the 7 character portraits |
| `VO/` | The 10 recorded voiceover files |
| `Notes/` | Voiceover script with delivery notes |
| `_edit/` | Everything used to build the final edit (see below) |

## How the final video is built (`_edit/`)

1. `transcribe.py` – transcribes the voiceover with Whisper (word timings → `vo_words.json`).
2. `vo.py build` – trims silences, adjusts speed per file and joins the voiceover → `vo_track.wav`, `vo_map.json` (phrase timings).
3. `edit.py base` – cuts, grades and moves each shot to the phrase timings → `seg/`, `base2.mp4`, `edit_tl.json`.
4. `audio2.py` – synthesizes the sound effects (`sfx.py`) and the tanpura/flute music bed → `sfx2.wav`, `music2.wav`.
5. `render_final2.sh` – renders the English graphics layer (`overlay2.html` / `overlay2.js`) frame by frame → `ovl2/`, then composites video, graphics, voiceover, ducked music and SFX into the final MP4.

Tools: FFmpeg, Python 3.12 (numpy, playwright, faster-whisper), Microsoft Edge for rendering the graphics. Rendered intermediates (`seg/`, `ovl2/`, `base2.mp4`, the `.wav` stems) are not stored; the scripts rebuild them.

Large media files are stored with Git LFS.
