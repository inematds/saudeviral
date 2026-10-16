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
fala_de, pos_de = {}, {}  # índice da palavra ouvida → fala / posição no roteiro
for a, b, n in m.get_matching_blocks():
    for j in range(n):
        fala_de.setdefault(ouv[b + j][1], esp[a + j][1])
        pos_de.setdefault(ouv[b + j][1], a + j)
ultima = {k: max(p for p, (_, kk) in enumerate(esp) if kk == k) for k in range(len(falas))}
dono, ant = [], None  # ant = última palavra com par
for i in range(len(pal)):  # palavra sem par fica com a fala da vizinha anterior...
    if i in fala_de:
        dono.append(fala_de[i]); ant = i; continue
    prox = next((j for j in range(i + 1, len(pal)) if j in fala_de), None)
    # ...menos quando a anterior já fechou a fala dela: aí é o começo da seguinte ("Vazinhos" ≠ "Vasinhos" no
    # saudeviral 16/10 ia para a fala de antes e o corte da virada caía entre "Vasinhos" e "roxos")
    if ant is not None and prox is not None and pos_de[ant] == ultima[fala_de[ant]] and fala_de[prox] > fala_de[ant]:
        dono.append(fala_de[prox])
    else:
        dono.append(fala_de[ant] if ant is not None else 0)

tempos = []
for k, f in enumerate(falas):
    ps = [p for p, d in zip(pal, dono) if d == k]
    tempos.append({"id": f["id"], "fala": f["fala"], "ini": 0, "fim": 0,
                   "palavras": [{"w": p["word"].strip(), "t": round(p["start"], 3), "f": round(p["end"], 3)} for p in ps]})
# fala sem palavra = o Whisper pulou o trecho (finviral 11/10: 7,6 s de áudio sem texto na f22):
# reparte a lacuna entre a fala anterior e a seguinte pelas palavras do roteiro; mais de 3 = o avatar não leu
vazias = [k for k, t in enumerate(tempos) if not t["palavras"]]
if len(vazias) > 3:
    sys.exit(f"{len(vazias)} falas não achadas na transcrição do avatar: {[tempos[k]['id'] for k in vazias]}")
k = 0
while k < len(tempos):
    if tempos[k]["palavras"]:
        k += 1; continue
    fim_run = k
    while fim_run < len(tempos) and not tempos[fim_run]["palavras"]:
        fim_run += 1
    t0 = tempos[k - 1]["palavras"][-1]["f"] if k > 0 else 0.0
    t1 = tempos[fim_run]["palavras"][0]["t"] if fim_run < len(tempos) else cs.dur(wav)
    ws = [(j, w) for j in range(k, fim_run) for w in falas[j]["fala"].split()]
    passo = max(t1 - t0, 0.3 * len(ws)) / max(len(ws), 1)
    for n, (j, w) in enumerate(ws):
        tempos[j]["palavras"].append({"w": w, "t": round(t0 + n * passo, 3), "f": round(t0 + (n + 1) * passo, 3)})
    print("aviso: fala(s)", [tempos[j]["id"] for j in range(k, fim_run)], f"sem transcrição; interpolada(s) em {t0:.1f}–{t1:.1f} s")
    k = fim_run
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
