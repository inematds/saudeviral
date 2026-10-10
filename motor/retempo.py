#!/usr/bin/env python3
"""uso: motor/retempo.py <pasta-da-edicao>
Tira o áudio de <ed>/avatar/avatar.mp4 (HeyGen), transcreve com tempo por palavra e divide nas falas do
roteiro.json (alinhamento por sequência de palavras), gravando <ed>/avatar/tempos.json no formato do narrar.py.
Mesmo método do eventosextremospub/avatar/retempo.py."""
import difflib, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projetos/cardshorts"))
import cardshorts as cs

E = Path(sys.argv[1]).resolve()
A = E / "avatar"
falas = json.loads((E / "roteiro.json").read_text())["falas"]
wav = A / "avatar.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", A / "avatar.mp4", "-vn", "-ac", "1", "-ar", "48000", wav], check=True)
pal = cs.transcrever(wav, A / "t", palavras=True)

ouv = [(w, i) for i, p in enumerate(pal) for w in cs.norm(p["word"])]
esp = [(w, k) for k, f in enumerate(falas) for w in cs.norm(f["fala"])]
m = difflib.SequenceMatcher(None, [w for w, _ in esp], [w for w, _ in ouv], autojunk=False)
fala_de = {}  # índice da palavra ouvida → fala
for a, b, n in m.get_matching_blocks():
    for j in range(n):
        fala_de.setdefault(ouv[b + j][1], esp[a + j][1])
atual, dono = 0, []
for i in range(len(pal)):  # palavra sem par fica com a fala da vizinha anterior
    atual = fala_de.get(i, atual)
    dono.append(atual)

tempos = []
for k, f in enumerate(falas):
    ps = [p for p, d in zip(pal, dono) if d == k]
    if not ps:
        sys.exit(f"fala {f['id']} não achada na transcrição do avatar")
    tempos.append({"id": f["id"], "fala": f["fala"], "ini": 0, "fim": 0,
                   "palavras": [{"w": p["word"].strip(), "t": round(p["start"], 3), "f": round(p["end"], 3)} for p in ps]})
for k, t in enumerate(tempos):
    t["ini"] = 0.0 if k == 0 else round(tempos[k - 1]["palavras"][-1]["f"] + 0.05, 3)
for k, t in enumerate(tempos):
    t["fim"] = round(tempos[k + 1]["ini"], 3) if k + 1 < len(tempos) else round(cs.dur(wav), 3)
(A / "tempos.json").write_text(json.dumps(tempos, ensure_ascii=False, indent=1))
sem = difflib.SequenceMatcher(None, [w for w, _ in esp], [w for w, _ in ouv]).ratio()
print(f"duração {cs.dur(wav):.1f} s · semelhança {sem:.0%}")
for t in tempos:
    print(t["id"], t["ini"], "→", t["fim"], " ".join(p["w"] for p in t["palavras"])[:100])
if sem < 0.8:
    sys.exit(f"semelhança baixa ({sem:.0%}): o avatar não leu o roteiro")
