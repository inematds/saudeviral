#!/usr/bin/env bash
# Vídeo LONGO 16:9 de uma edição que já tem roteiro.json aprovado no checar --longo:
# avatar (HeyGen estúdio, em blocos) → retempo → cena → render → publica no lives2 + bot v3.
# uso: auto/longo.sh <pasta-da-edicao-longa> <rotulo>      (ex.: edicoes/2026-10-17-semanal-longo "semanal · LONGO · 17/10/2026")
set -uo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
E="$(cd "$1" && pwd)"; ROT="$2"; T="SAUDEVIRAL-$(basename "$E")"
# saída 75 = máquina ocupada (a vaga gpu/render não abriu a tempo, motor/vaga.sh, 09/11/2026): repassa 75, não é erro de conteúdo
bash "$RAIZ/motor/avatar_heygen.sh" "$E" "$T" > "$E/avatar.log" 2>&1 || { rc=$?; [ "$rc" = 75 ] && { echo "OCUPADO: máquina ocupada no retempo/emenda do avatar"; exit 75; }; echo "ERRO avatar: $(grep -h ERRO "$E/avatar.log" | tail -1)"; exit 3; }
python3 "$RAIZ/motor/gerar_cena_longo.py" "$E" --avatar > "$E/cena.log" 2>&1 || { echo "ERRO cena: $(tail -1 "$E/cena.log")"; exit 4; }
RENDER_ESPERA_MIN="${RENDER_ESPERA_MIN:-60}" bash "$RAIZ/motor/vaga.sh" render "$(basename "$RAIZ")-longo" bash "$RAIZ/motor/compor_longo.sh" "$E" "$E/video-longo.mp4" > "$E/compor.log" 2>&1 \
  || { rc=$?; [ "$rc" = 75 ] && { echo "OCUPADO: máquina ocupada no render do longo"; exit 75; }; echo "ERRO render: $(tail -1 "$E/compor.log")"; exit 5; }
bash "$RAIZ/auto/publicar.sh" "$E/video-longo.mp4" "$E" "$ROT"
