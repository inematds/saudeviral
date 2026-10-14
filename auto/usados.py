#!/usr/bin/env python3
"""Base do que já foi publicado (auto/usados.tsv), para o diário não repetir vídeo nem assunto.
Colunas: data, modo, handle, id do vídeo, assunto (do roteiro), título do vídeo.
Só entra o vídeo CITADO no base.md da edição publicada: o que foi escolhido e ficou de fora continua disponível.
uso:
  auto/usados.py ids                        ids já usados pelo diário (um por linha)
  auto/usados.py recentes <AAAA-MM-DD> [N]  assuntos do diário nos N dias antes da data (padrão 7), para o roteiro
  auto/usados.py registrar <edição> <AAAA-MM-DD> <modo>"""
import json, re, sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "auto/usados.tsv"
CAB = "data\tmodo\thandle\tid\tassunto\ttitulo\n"


def linhas():
    if not BASE.exists():
        return []
    return [l.rstrip("\n").split("\t") for l in BASE.read_text().splitlines()[1:] if l.count("\t") >= 5]


def nomes():
    return {c["handle"]: c["nome"] for c in json.loads((RAIZ / "canais.json").read_text())["canais"]}


def registrar(ed, dia, modo):
    ed = Path(ed)
    videos = {c[2]: c for c in (l.split("\t") for l in (ed / "videos.tsv").read_text().splitlines()) if len(c) >= 7}
    base = (ed / "base.md").read_text()
    citados = [i for i in videos if i in base]
    assunto = {}
    try:
        for f in json.loads((ed / "roteiro.json").read_text())["falas"]:
            if f.get("assunto"):
                img = (f.get("ficha") or {}).get("foto") or f.get("fundo") or ""
                m = re.search(r"img/([\w-]{11})\.jpg", img)
                if m:
                    assunto.setdefault(m.group(1), f["assunto"])
    except (OSError, ValueError, KeyError):
        pass
    ja = {(l[0], l[1], l[3]) for l in linhas()}
    novas = [[dia, modo, videos[i][0], i, assunto.get(i, ""), videos[i][6].replace("\t", " ")]
             for i in citados if (dia, modo, i) not in ja]
    if not BASE.exists():
        BASE.write_text(CAB)
    with BASE.open("a") as f:
        f.writelines("\t".join(c) + "\n" for c in novas)
    print(f"usados.tsv: +{len(novas)} ({len(citados)} citados de {len(videos)} escolhidos)")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "ids":
        print("\n".join(sorted({l[3] for l in linhas() if l[1] == "diario"})))
    elif cmd == "recentes":
        fim = date.fromisoformat(sys.argv[2]); ini = fim - timedelta(days=int(sys.argv[3]) if len(sys.argv) > 3 else 7)
        nm = nomes()
        for l in linhas():
            if l[1] == "diario" and ini.isoformat() <= l[0] < fim.isoformat():
                print(f"- {l[0][8:10]}/{l[0][5:7]} · {nm.get(l[2], l[2])} · {l[4] or l[5]}")
    elif cmd == "registrar" and len(sys.argv) == 5:
        registrar(*sys.argv[2:5])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
