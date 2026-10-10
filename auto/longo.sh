#!/usr/bin/env bash
# Vídeo LONGO 16:9 de uma edição que já tem roteiro.json aprovado no checar --longo:
# avatar (HeyGen estúdio, em blocos) → retempo → cena → render → publica no lives12 + bot v3.
# uso: auto/longo.sh <pasta-da-edicao-longa> <rotulo>      (ex.: edicoes/2026-10-17-semanal-longo "semanal · LONGO · 17/10/2026")
set -uo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
E="$(cd "$1" && pwd)"; ROT="$2"; T="SAUDEVIRAL-$(basename "$E")"
bash "$RAIZ/motor/avatar_heygen.sh" "$E" "$T" > "$E/avatar.log" 2>&1 || { echo "ERRO avatar: $(grep -h ERRO "$E/avatar.log" | tail -1)"; exit 3; }
python3 "$RAIZ/motor/gerar_cena_longo.py" "$E" --avatar > "$E/cena.log" 2>&1 || { echo "ERRO cena: $(tail -1 "$E/cena.log")"; exit 4; }
bash "$RAIZ/motor/compor_longo.sh" "$E" "$E/video-longo.mp4" > "$E/compor.log" 2>&1 || { echo "ERRO render: $(tail -1 "$E/compor.log")"; exit 5; }
bash "$RAIZ/auto/publicar.sh" "$E/video-longo.mp4" "$E" "$ROT"
