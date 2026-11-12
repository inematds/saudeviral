#!/usr/bin/env bash
# Publica um vídeo do saudeviral no YouTube INEMA TIA (lives2, Radar Viral) pelo yt-pubx e manda SEMPRE ao bot v3 (com o link).
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
# Radar Viral (Nei, 10/11/2026): com RADAR_VIRAL=1 (vem do serviço) o vídeo pronto fica pendente e o
# ~/projetos/radar-viral/radar.py (timer de hora em hora) publica no lives2 (Nei, 11/11: lives24 não entrega; só o futviral fica lá), 1 por hora, respeitando o
# "a partir de" de cada nicho (radar.json). Para segurar: crie <ed>/SEGURAR.
if { [ -n "${RADAR_VIRAL:-}" ] || [ -e "$E/SEGURAR" ]; } && [ "${SEM_YT:-}" != 1 ] && [ -z "${PUBLICANDO_PENDENTE:-}" ]; then
  QUANDO="pelo Radar Viral (lives2, 1 por hora)"; [ -e "$E/SEGURAR" ] && QUANDO="só quando o Nei liberar (rm $E/SEGURAR; o radar pega na hora seguinte)"
  printf '%s\n%s\n%s\n' "$V" "$ROT" "$EXTRA" > "$E/PUBLICAR_PENDENTE.$(basename "$V" .mp4)"
  echo "pendente: publica $QUANDO"; exit 0
fi
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V" | cut -d. -f1)
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$V")
TIT=$(head -1 "$E/legenda.txt" | cut -c1-90)
[ "$W" -lt 1000 ] && TIT="$TIT #Shorts"
URL=""
if [ "${SEM_YT:-}" != 1 ]; then
  CTX="saudeviral (Radar Viral): resumo do que os maiores influenciadores de saúde do Brasil (médicos, nutricionistas e psicólogos) disseram, com a fonte de cada fato na tela e o Nei Maldaner comentando. Não substitui consulta médica. Curso gratuito de gestão de agentes de IA em https://inema.club. Não cite outros canais na descrição além dos influenciadores do vídeo."
  timeout 2400 "$HOME/projetos/yt-pubx/yt-pubx" publicar "$V" --canal lives2 --title "$TIT" --contexto "$CTX" \
      --contexto-arquivo "$E/legenda.txt" > "$PL" 2>&1
  URL=$(grep -o 'https://www.youtube.com/watch?v=[A-Za-z0-9_-]*\|https://youtu.be/[A-Za-z0-9_-]*' "$PL" | tail -1)
fi
if [ -n "$URL" ]; then ST="publicado no INEMA TIA (lives2): $URL"
elif [ "${SEM_YT:-}" = 1 ]; then ST="(sem YouTube nesta rodada)"
else ST="⚠ NÃO publicou no lives2: $(grep -h -i 'erro\|error\|quota\|limit' "$PL" | tail -1 | cut -c1-200)"; fi
if [ -z "$URL" ]; then  # (Nei, 06/11/2026: aviso do YouTube no v3 só se der erro)
  VB="$V"  # bot aceita até ~49 MB: acima disso vai uma cópia 720p (o YouTube recebe o original)
  if [ "$(stat -c %s "$V")" -gt 48000000 ]; then
    VB="${V%.mp4}-720p.mp4"
    RAIZ="$(cd "$(dirname "$0")/.." && pwd)"  # encode na vaga render da máquina (motor/vaga.sh, 09/11/2026)
    RENDER_ESPERA_MIN="${RENDER_ESPERA_MIN:-30}" bash "$RAIZ/motor/vaga.sh" render "$(basename "$RAIZ")-720p" \
      ffmpeg -v error -y -i "$V" -vf "scale=-2:720" -c:v libx264 -crf 27 -preset medium -c:a aac -b:a 128k -movflags +faststart "$VB"
  fi
  rm -f "$VB.envio-v3.json"
  node "$BOT" $DRY "$VB" "saudeviral · $ROT · ${DUR}s
$ST
$(head -c 600 "$E/legenda.txt")$EXTRA" || echo "falhou o envio ao bot"
fi
echo "$ST"
# TikTok + Instagram @inemafuturos pelo Metricool (projeto metricool-pub2), 1 por dia, só o curto vertical
# já publicado no YouTube. Horário: finviral 07:00, saudeviral 05:00, advviral 08:00 (ou assim que pronto).
# Pedidos do Nei em 22 e 24/10/2026. Falha aqui não derruba a rodada (o script avisa no bot).
MP="$HOME/projetos/metricool-pub2/publicar_reel.sh"
# Desligado em 10/11/2026: o Radar Viral agenda na marca Radar do metritds (IG+TikTok inema.club24). METRICOOL_PUB2=1 religa o @inemafuturos.
if [ -n "$URL" ] && [ -n "${METRICOOL_PUB2:-}" ] && [ "$W" -lt "$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$V")" ] && [ -x "$MP" ]; then
  SEM_BOT="${SEM_BOT:-}" timeout 900 bash "$MP" saudeviral "$V" "$E" "$URL" || echo "metricool: não agendou (ver ~/projetos/metricool-pub2/estado/saudeviral/)"
fi
