#!/usr/bin/env bash
# Baixa só o áudio (inemavox) e transcreve local (Whisper) cada id da lista.
# uso: transcrever.sh id1 id2 ...   -> $TX/<id>/transcript.txt  (TX padrão: ~/projetos/output/saudeviral/coleta/tx, fora do repo)
set -uo pipefail
TX="${TX:-$HOME/projetos/output/saudeviral/coleta/tx}"
VOX="$HOME/projetos/inemavox"
MODELO="${MODELO:-large-v3}"
cd "$VOX"
for id in "$@"; do
  D="$TX/$id"; mkdir -p "$D/audio"
  if ls "$D"/*.txt >/dev/null 2>&1; then echo "já tem $id"; continue; fi
  echo "== $id baixando $(date +%T)"
  python3 baixar_v1.py --url "https://www.youtube.com/watch?v=$id" --outdir "$D/audio" --quality audio > "$D/baixar.log" 2>&1 || { echo "falhou download $id"; continue; }
  A=$(ls -S "$D"/audio/*.{wav,m4a,mp3,webm,opus} 2>/dev/null | head -1)
  [ -z "$A" ] && { echo "sem audio $id"; continue; }
  echo "== $id transcrevendo $(date +%T) $A"
  python3 transcrever_v1.py --in "$A" --outdir "$D" --whisper-model "$MODELO" --src pt > "$D/tx.log" 2>&1 || echo "falhou tx $id"
done
echo "fim $(date +%T)"
