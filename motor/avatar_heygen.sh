#!/usr/bin/env bash
# Avatar do Nei pelo ESTÚDIO do HeyGen (assinatura, sem API de geração): envia a fala, espera, baixa e retemporiza.
# uso: motor/avatar_heygen.sh <pasta-da-edicao> <titulo>   -> <ed>/avatar/avatar.mp4 + avatar/tempos.json
# O estúdio aceita até 4500 caracteres por vídeo: a fala é dividida em blocos de até 4000 (sempre entre falas),
# todos são enviados antes (o HeyGen gera em paralelo), depois baixados e emendados num avatar.mp4 só.
# Trava (flock) no perfil do estúdio: outras sessões (explicavideos, eventosextremos) usam o mesmo perfil.
# O script do estúdio recusa oferta de troca de plano (o Nei NUNCA troca de plano).
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
E="$(cd "$1" && pwd)"; TITULO="$2"
A="$E/avatar"; mkdir -p "$A"
PERFIL="$HOME/.cache/inemaccbot/perfil-heygen"
ENG="$HOME/projetos/explicavideos/engine"
export DISPLAY=:99
N=$(python3 - "$E/roteiro.json" "$A" <<'EOF'
import json, sys
falas = [f["fala"] for f in json.load(open(sys.argv[1]))["falas"]]
open(f"{sys.argv[2]}/fala.txt", "w").write(" ".join(falas))
blocos, cur = [], []
for f in falas:
    if cur and len(" ".join(cur + [f])) > 4000:
        blocos.append(cur); cur = []
    cur.append(f)
blocos.append(cur)
for i, b in enumerate(blocos, 1):
    open(f"{sys.argv[2]}/fala-b{i}.txt", "w").write(" ".join(b))
print(len(blocos))
EOF
)
# O heygen-studio.mjs entra na fila do perfil sozinho (explicavideos/engine/heygen-perfil.mjs, até 3 h): por isso o timeout do envio é 12000 s.
# Quem não pega a trava (ex.: lote de tradução do explicavideos) abre o mesmo perfil e o Chrome recusa
# ("ProcessSingleton", 10/10/2026): espera 2 min e tenta de novo, até 1 h. Nada foi enviado quando isso acontece.
tenta(){ local log="$1" k; shift
  for k in $(seq 1 30); do
    "$@" > "$log" 2>&1 && return 0
    grep -q ProcessSingleton "$log" || return 1
    echo "perfil do HeyGen aberto por outro processo; nova tentativa em 2 min ($k/30)"; sleep 120
  done; return 1; }
{
  flock -w 1800 9 || { echo "ERRO: perfil do HeyGen ocupado há 30 min"; exit 5; }
  cd "$HOME/projetos/explicavideos"
  for i in $(seq 1 "$N"); do
    # retomada: bloco já enviado (id gravado) não é reenviado — só baixa (REFAZER_HEYGEN=1 força novo envio)
    if [ -s "$A/video_id-b$i.txt" ] && [ "${REFAZER_HEYGEN:-}" != 1 ]; then echo "bloco $i já enviado: $(cat "$A/video_id-b$i.txt")"; continue; fi
    T="$TITULO"; [ "$N" -gt 1 ] && T="$TITULO-b$i"
    tenta "$A/studio-b$i.log" timeout 12000 node "$ENG/heygen-studio.mjs" --titulo "$T" --fala-arquivo "$A/fala-b$i.txt" --perfil "$PERFIL" --template TEMPLATE-AVATAR16 \
      || { echo "ERRO no estúdio (bloco $i/$N): $(grep -h ERRO "$A/studio-b$i.log" | tail -1)"; exit 3; }
    ID=$(grep -o 'create-v4/[0-9a-f]\{32\}' "$A/studio-b$i.log" | tail -1 | cut -d/ -f2)
    [ -n "$ID" ] || { echo "ERRO: id do vídeo do bloco $i não achado no studio-b$i.log"; exit 3; }
    echo "$ID" > "$A/video_id-b$i.txt"
    [ "$i" = 1 ] && echo "$ID" > "$A/video_id.txt"
    sleep 20
  done
  sleep 60
  for i in $(seq 1 "$N"); do
    [ -s "$A/avatar-b$i.mp4" ] && continue
    tenta "$A/baixar-b$i.log" timeout 18000 node "$ENG/heygen-estudio-baixar.mjs" --id "$(cat "$A/video_id-b$i.txt")" --saida "$A/avatar-b$i.mp4" --perfil "$PERFIL" --minutos 290 --intervalo 120 \
      || { echo "ERRO ao baixar o bloco $i/$N: $(tail -1 "$A/baixar-b$i.log")"; exit 4; }
  done
} 9>"$HOME/.cache/inemaccbot/heygen-estudio.lock"
if [ "$N" = 1 ]; then
  mv "$A/avatar-b1.mp4" "$A/avatar.mp4"
else
  ARGS=(); FIL=""
  for i in $(seq 1 "$N"); do ARGS+=(-i "$A/avatar-b$i.mp4"); FIL+="[$((i-1)):v]fps=30,scale=1920:1080,setsar=1[v$i];[$((i-1)):a]aresample=48000[a$i];"; done
  for i in $(seq 1 "$N"); do FIL+="[v$i][a$i]"; done
  ffmpeg -v error -y "${ARGS[@]}" -filter_complex "${FIL}concat=n=$N:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset fast -c:a aac -b:a 192k "$A/avatar.mp4"
fi
python3 "$AQUI/retempo.py" "$E"
