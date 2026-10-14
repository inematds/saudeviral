#!/usr/bin/env bash
# A voz do HeyGen chega ~-26 dB: loudnorm a -14 LUFS (padrão de short) antes de mixar.
# Palco (cena.js gerado com --avatar) + avatar do HeyGen no canto (rosto 400x453 em 640,1290, moldura âmbar do palco) + trilha.
# uso: motor/compor_avatar.sh <pasta-da-edicao> [saida.mp4]   (precisa de <ed>/avatar/avatar.mp4)
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
E="$(cd "$1" && pwd)"; SAIDA="${2:-$E/video-avatar.mp4}"
MUSICA="${MUSICA:-$HOME/projetos/cardshorts/musicas/tensa.mp3}"
A="$E/avatar/avatar.mp4"
mkdir -p "$E/build"
# palco já renderizado e mais novo que a cena? não refaz
[ "$E/build/palco-avatar.mp4" -nt "$E/cena.js" ] || node "$AQUI/render.mjs" "$E" "$E/build/palco-avatar.mp4"
# respiros (1 s do cartão de virada): avatar com o mesmo buraco da cena; durante o cartão o avatar some (Nei, 14/10/2026)
python3 "$AQUI/respiros.py" "$E" "$A" "$E/build/avatar-resp.mp4"; A="$E/build/avatar-resp.mp4"
GAP=$(python3 -c "import json,sys; s=open(sys.argv[1]).read(); C=json.loads(s[s.index('{'):s.rindex('}')+1]); print('+'.join(f\"between(t,{v['ini']:.3f},{v['fim']:.3f})\" for v in C.get('viradas',[])) or '0')" "$E/cena.js")
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$A")
# fade só na música: o HeyGen termina logo após a última palavra e o fade na mistura engolia o CTA
FADE=$(python3 -c "print(max(0, $D - 1.4))")
# quadro 0 (capa): o rosto ocupa toda a parte de baixo (1080x720 em y=1200, sem moldura) até o fim da 1ª fala; depois o quadro normal (Nei, 13/10/2026)
T0=$(python3 -c "import json,sys; s=open(sys.argv[1]).read(); C=json.loads(s[s.index('{'):s.rindex('}')+1]); h=(C.get('hero') or [{}])[0]; print(h['fim'] if h.get('ini',1)<=0 else 0)" "$E/cena.js")
# pergunta da cidade: rosto grande no centro (1080x600 em y=490, acima da legenda, sem moldura) até o CTA (Nei, 14/10/2026)
PG=$(python3 -c "import json,sys; s=open(sys.argv[1]).read(); C=json.loads(s[s.index('{'):s.rindex('}')+1]); g=C.get('avgrande'); print(f\"between(t,{g['ini']:.3f},{g['fim']:.3f})\" if g else '0')" "$E/cena.js")
ffmpeg -v error -y -i "$E/build/palco-avatar.mp4" -i "$A" -stream_loop -1 -i "$MUSICA" -filter_complex \
  "[1:v]split=3[a1][a2][a3];[a1]crop=900:1020:510:0,scale=400:453,setsar=1,fps=30[av];[a2]crop=1620:1080:300:0,scale=1080:720,setsar=1,fps=30[avg];[a3]crop=1800:1000:60:0,scale=1080:600,setsar=1,fps=30[avc];[0:v][avg]overlay=0:1200:enable='lt(t,$T0)*not($GAP)':shortest=1[p0];[p0][avc]overlay=0:490:enable='($PG)*not($GAP)':shortest=1[p1];[p1][av]overlay=640:1290:enable='gte(t,$T0)*not($GAP)*not($PG)':shortest=1,drawbox=x=640:y=1700:w=400:h=43:color=0x0b0f14@0.85:t=fill:enable='gte(t,$T0)*not($GAP)*not($PG)',drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile=$AQUI/tag-nei.txt:x=656:y=1712:fontsize=19:fontcolor=white:enable='gte(t,$T0)*not($GAP)*not($PG)'[v];
   [1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,asplit=2[voz][sc];[2:a]volume=0.2,aresample=48000[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300,afade=t=out:st=$FADE:d=1.4[md];
   [voz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 23 -preset slow -maxrate 4M -bufsize 8M -c:a aac -b:a 192k -movflags +faststart -shortest "$SAIDA"
echo "ok $SAIDA ($(du -h "$SAIDA" | cut -f1))"
