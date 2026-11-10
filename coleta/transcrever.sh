#!/usr/bin/env bash
# Baixa só o áudio (inemavox) e transcreve local (Whisper) cada id da lista.
# uso: transcrever.sh id1 id2 ...   -> $TX/<id>/transcript.txt  (TX padrão: ~/projetos/output/saudeviral/coleta/tx, fora do repo)
set -uo pipefail
TX="${TX:-$HOME/projetos/output/saudeviral/coleta/tx}"
VOX="$HOME/projetos/inemavox"
MODELO="${MODELO:-large-v3}"
# Whisper na vaga gpu da máquina (motor/vaga.sh → wifi/scripts/fila-vaga, 09/11/2026); o download fica fora da vaga.
# Espera até GPU_ESPERA_MIN (45 min por vídeo; o rodar.sh dá 7200 s ao todo); estourou → sai 75 (máquina ocupada).
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; VAGA="$RAIZ/motor/vaga.sh"; M="$(basename "$RAIZ")"
cd "$VOX"
for id in "$@"; do
  D="$TX/$id"; mkdir -p "$D/audio"
  if ls "$D"/*.txt >/dev/null 2>&1; then echo "já tem $id"; continue; fi
  echo "== $id baixando $(date +%T)"
  python3 baixar_v1.py --url "https://www.youtube.com/watch?v=$id" --outdir "$D/audio" --quality audio > "$D/baixar.log" 2>&1 || { echo "falhou download $id"; continue; }
  A=$(ls -S "$D"/audio/*.{wav,m4a,mp3,webm,opus} 2>/dev/null | head -1)
  [ -z "$A" ] && { echo "sem audio $id"; continue; }
  echo "== $id transcrevendo $(date +%T) $A"
  GPU_ESPERA_MIN="${GPU_ESPERA_MIN:-45}" bash "$VAGA" gpu "$M-whisper" python3 transcrever_v1.py --in "$A" --outdir "$D" --whisper-model "$MODELO" --src pt > "$D/tx.log" 2>&1; rc=$?
  [ "$rc" = 75 ] && { echo "máquina ocupada: a vaga gpu não abriu a tempo para o Whisper ($id)"; exit 75; }
  [ "$rc" = 0 ] || echo "falhou tx $id"
done
echo "fim $(date +%T)"
