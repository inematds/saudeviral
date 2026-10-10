#!/usr/bin/env python3
"""Lista (só metadados, yt-dlp) os vídeos dos canais ativos de canais.json publicados entre duas datas.
uso: coleta/listar.py <de AAAAMMDD> <ate AAAAMMDD> <saida.tsv> [n por canal]
Colunas: handle, data, id, duração(s), views, canal, título (PT)."""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DE, ATE, SAIDA = sys.argv[1], sys.argv[2], Path(sys.argv[3])
N = sys.argv[4] if len(sys.argv) > 4 else "8"
canais = [c for c in json.loads((RAIZ / "canais.json").read_text())["canais"] if c.get("ativo", True)]
linhas, erros = [], []
for c in canais:
    h = c["handle"]
    r = subprocess.run(["timeout", "300", "yt-dlp", "--playlist-end", N, "--skip-download", "--no-warnings",
                        "--extractor-args", "youtube:lang=pt",
                        "--print", f"{h}\t%(upload_date)s\t%(id)s\t%(duration)s\t%(view_count)s\t%(channel)s\t%(title)s",
                        f"https://www.youtube.com/{h}/videos"], capture_output=True, text=True)
    achou = [l for l in r.stdout.splitlines() if l.count("\t") >= 6]
    if not achou:
        erros.append(f"{h}: {r.stderr.strip()[-200:]}")
    linhas += [l for l in achou if DE <= l.split("\t")[1] <= ATE]
SAIDA.write_text("".join(l + "\n" for l in linhas))
print(f"{len(linhas)} vídeos entre {DE} e {ATE} -> {SAIDA}")
for e in erros:
    print("ERRO", e, file=sys.stderr)
