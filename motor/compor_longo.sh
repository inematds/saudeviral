#!/usr/bin/env bash
# Vídeo LONGO 16:9: renderiza motor/longo.html (cena-longo.js) e mistura com a voz.
# uso: motor/compor_longo.sh <pasta-da-edicao> <saida.mp4> [--narracao]
#   padrão     : avatar/avatar.mp4 do HeyGen no canto (1478,36 · 406×228, cantos arredondados) + voz dele
#   --narracao : prévia sem HeyGen — foto no canto (já no palco) + narracao.wav (chatterbox, voz do Nei)
# Voz normalizada a −14 LUFS; música baixa com ducking; fade final SÓ na música (a voz do CTA não cai).
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
E="$(cd "$1" && pwd)"; SAIDA="$2"; MODO="${3:-}"
MUSICA="${MUSICA:-$HOME/projetos/cardshorts/musicas/tensa.mp3}"
mkdir -p "$E/build"
PALCO="$E/build/palco-longo.mp4"
[ "$PALCO" -nt "$E/cena-longo.js" ] || node "$AQUI/render.mjs" "$E" "$PALCO" --palco longo
if [ "$MODO" = --narracao ]; then
  VOZ="$E/narracao.wav"
  VIDEO="[0:v]null[v]"
else
  VOZ="$E/avatar/avatar.mp4"
  VIDEO="[1:v]scale=406:228,setsar=1,fps=30,format=yuva420p,geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a='if(gt(hypot(max(0,abs(X-202.5)-180.5),max(0,abs(Y-113.5)-91.5)),22),0,255)'[av];[0:v][av]overlay=1478:36:shortest=1[v]"
fi
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VOZ")
FADE=$(python3 -c "print(max(0, $D - 2))")
ffmpeg -v error -y -i "$PALCO" -i "$VOZ" -stream_loop -1 -i "$MUSICA" -filter_complex \
  "$VIDEO;
   [1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,asplit=2[voz][sc];[2:a]volume=0.12,aresample=48000[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300,afade=t=out:st=$FADE:d=2[md];
   [voz][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 22 -preset medium -maxrate 6M -bufsize 12M -c:a aac -b:a 192k -movflags +faststart -shortest "$SAIDA"
echo "ok $SAIDA ($(du -h "$SAIDA" | cut -f1))"
