#!/bin/bash
# v2: render overlay2 frames (3 workers, resumable), composite over base2.mp4, mix VO + music (ducked) + SFX.
cd "$(dirname "$0")"
PY="C:/Users/nidhi/AppData/Local/Temp/claude/c869c2981ca08201/0d51dc12-28d3-434c-a001-5531329f1cca/scratchpad/venv/Scripts/python"
FF="/c/Users/nidhi/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg"
N=$("$PY" -I -c "import json,math;print(round(json.load(open('edit_tl.json'))['total']*30))")
read P0 P1 < <("$PY" -I -c "import json;d={s['name']:s for s in json.load(open('edit_tl.json'))['shots']};print(round(d['pause']['start']-.4,2),round(d['pause']['end']+.9,2))")
date +%T; echo "frames to render: $N  pause SFX boost $P0-$P1"
mkdir -p ovl2
run() {
  local a=$1
  while [ $a -lt $2 ] && [ -f "ovl2/$(printf %05d $a).png" ]; do a=$((a+1)); done
  [ $a -lt $2 ] && "$PY" preview2.py --frames ovl2 $a $2 > "$3" 2>&1
}
T=$(( (N + 2) / 3 ))
run 0 $T l0.txt & run $T $((2*T)) l1.txt & run $((2*T)) $N l2.txt &
wait
echo "frames: $(ls ovl2 | wc -l)"; grep -h -iE "retry|error" l?.txt | head -3
"$FF" -y -loglevel error -i base2.mp4 -framerate 30 -i ovl2/%05d.png -i vo_track.wav -i music2.wav -i sfx2.wav \
  -filter_complex "[0:v][1:v]overlay=format=auto,format=yuv420p[v];\
[2:a]volume=1.0,asplit=2[vo][vok];\
[3:a]volume=0.32[mu];[mu][vok]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[mud];\
[4:a]volume='if(between(t,$P0,$P1),1.7,0.5)':eval=frame[sx];\
[vo][mud][sx]amix=inputs=3:normalize=0:duration=longest,apad,alimiter=limit=0.84:level=false[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 17 -preset slow -profile:v high -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest \
  "../Dev Deepawali - Final (with VO).mp4"
date +%T; echo DONE
