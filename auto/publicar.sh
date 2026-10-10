#!/usr/bin/env bash
# Publica um vídeo do saudeviral no YouTube Inema Pro (lives12) pelo yt-pubx e manda SEMPRE ao bot v3 (com o link).
# uso: auto/publicar.sh <video.mp4> <pasta-da-edicao> <rotulo> [extra-da-legenda]
#   título = 1ª linha de <ed>/legenda.txt (curto vertical recebe #Shorts e sai sem thumb; o longo ganha thumb do Codex).
#   SEM_YT=1 só manda ao bot; SEM_BOT=1 simula o envio ao bot (teste).
# Autorizado pelo Nei em 10/10/2026: "pode sempre criar direto com o avatar … publicar … e sempre manda para o bot também".
set -uo pipefail
# systemd não tem ~/.npm-global/bin no PATH e pegava o codex velho de /usr/bin (0.116), que não lê o config.toml do novo (10/10/2026)
export PATH="$HOME/.npm-global/bin:$PATH"
V="$1"; E="$(cd "$2" && pwd)"; ROT="$3"; EXTRA="${4:-}"
PL="$E/publicar-$(printf %s "$ROT" | tr -c 'A-Za-z0-9-' _).log"  # o rótulo traz a data dd/mm/aaaa: barra no nome quebrava o log (10/10/2026)
BOT="$HOME/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
DRY=""; [ "${SEM_BOT:-}" = 1 ] && DRY=--dry-run
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$V")
TIT=$(head -1 "$E/legenda.txt" | cut -c1-90)
[ "$W" -lt 1000 ] && TIT="$TIT #Shorts"
URL=""
if [ "${SEM_YT:-}" != 1 ]; then
  CTX="saudeviral (Inema Pro): resumo do que os maiores influenciadores de saúde do Brasil (médicos, nutricionistas e psicólogos) disseram, com a fonte de cada fato na tela e o Nei Maldaner comentando. Não substitui consulta médica. Curso gratuito de gestão de agentes de IA em https://inema.club. Não cite outros canais na descrição além dos influenciadores do vídeo."
  timeout 2400 "$HOME/projetos/yt-pubx/yt-pubx" publicar "$V" --canal lives12 --title "$TIT" --contexto "$CTX" \
      --contexto-arquivo "$E/legenda.txt" > "$PL" 2>&1
  URL=$(grep -o 'https://www.youtube.com/watch?v=[A-Za-z0-9_-]*\|https://youtu.be/[A-Za-z0-9_-]*' "$PL" | tail -1)
fi
if [ -n "$URL" ]; then ST="publicado no Inema Pro (lives12): $URL"
elif [ "${SEM_YT:-}" = 1 ]; then ST="(sem YouTube nesta rodada)"
else ST="⚠ NÃO publicou no lives12: $(grep -h -i 'erro\|error\|quota\|limit' "$PL" | tail -1 | cut -c1-200)"; fi
VB="$V"  # bot aceita até ~49 MB: acima disso vai uma cópia 720p (o YouTube recebe o original)
if [ "$(stat -c %s "$V")" -gt 48000000 ]; then
  VB="${V%.mp4}-720p.mp4"
  ffmpeg -v error -y -i "$V" -vf "scale=-2:720" -c:v libx264 -crf 27 -preset medium -c:a aac -b:a 128k -movflags +faststart "$VB"
fi
rm -f "$VB.envio-v3.json"
node "$BOT" $DRY "$VB" "saudeviral · $ROT · ${DUR}s
$ST
$(head -c 600 "$E/legenda.txt")$EXTRA" || echo "falhou o envio ao bot"
echo "$ST"
