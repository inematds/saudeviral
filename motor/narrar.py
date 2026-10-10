#!/usr/bin/env python3
"""uso: motor/narrar.py <pasta-da-edicao> [atempo] [f1,f2 só para teste]
Grava as falas do roteiro.json com a voz do Nei (motor do cardshorts: confere por transcrição e corta o fim),
junta com pausa curta e grava o tempo de cada palavra em tempos.json. Mesmo método do eventosextremospub."""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projetos/cardshorts"))
import cardshorts as cs

E = Path(sys.argv[1]).resolve()
PAD = 0.2
TEMPO = float(sys.argv[2]) if len(sys.argv) > 2 else 1.12  # atempo (≤1,15 para não chiar)
VOZ = dict(cs.VOZ_PADRAO)  # 0.6/0.6: a 0.85/0.35 chiava o "s" (lição 08/10)
SO = sys.argv[3].split(",") if len(sys.argv) > 3 else None

falas = [{"id": f["id"], "fala": f["fala"]} for f in json.loads((E / "roteiro.json").read_text())["falas"]
         if not SO or f["id"] in SO]
r = {"voz": dict(VOZ), "cenas": falas, "_obra": E / ".obra"}
r["_obra"].mkdir(exist_ok=True)
cs.gerar_voz(r)

build = E / "build"; build.mkdir(exist_ok=True)
lista, t0, tempos = [], 0.0, []
for c in r["cenas"]:
    w = build / f"{c['id']}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", c["_wav"], "-af", f"atempo={TEMPO},apad=pad_dur={PAD}",
                    "-ar", "48000", "-ac", "1", w], check=True)
    d = cs.dur(w)
    pal = cs.transcrever(w, build / f"t_{c['id']}", palavras=True)
    tempos.append({"id": c["id"], "fala": c["fala"], "ini": round(t0, 3), "fim": round(t0 + d, 3),
                   "palavras": [{"w": p["word"].strip(), "t": round(t0 + p["start"], 3), "f": round(t0 + p["end"], 3)} for p in pal]})
    lista.append(f"file '{w}'")
    t0 += d
(build / "lista.txt").write_text("\n".join(lista))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", build / "lista.txt", "-c:a", "pcm_s16le", E / "narracao.wav"], check=True)
(E / "tempos.json").write_text(json.dumps(tempos, ensure_ascii=False, indent=1))
print(f"narração {t0:.1f} s -> {E/'narracao.wav'}")
for t in tempos:
    print(t["id"], t["ini"], "→", t["fim"], " ".join(p["w"] for p in t["palavras"]))
