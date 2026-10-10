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
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$A")
# fade só na música: o HeyGen termina logo após a última palavra e o fade na mistura engolia o CTA
FADE=$(python3 -c "print(max(0, $D - 1.4))")
ffmpeg -v error -y -i "$E/build/palco-avatar.mp4" -i "$A" -stream_loop -1 -i "$MUSICA" -filter_complex \
  "[1:v]crop=900:1020:510:0,scale=400:453,setsar=1,fps=30[av];[0:v][av]overlay=640:1290:shortest=1,drawbox=x=640:y=1700:w=400:h=43:color=0x0b0f14@0.85:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile=$AQUI/tag-nei.txt:x=656:y=1712:fontsize=19:fontcolor=white[v];
   [1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,asplit=2[voz][sc];[2:a]volume=0.2,aresample=48000[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300,afade=t=out:st=$FADE:d=1.4[md];
   [voz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 23 -preset slow -maxrate 4M -bufsize 8M -c:a aac -b:a 192k -movflags +faststart -shortest "$SAIDA"
echo "ok $SAIDA ($(du -h "$SAIDA" | cut -f1))"
