#!/usr/bin/env python3
"""uso: motor/gerar_cena_longo.py <pasta-da-edicao> [--avatar]
Monta <ed>/cena-longo.js para motor/longo.html (16:9) a partir de roteiro.json (formato longo) e dos tempos
(tempos.json do narrar.py; com --avatar, avatar/tempos.json do retempo.py).

roteiro.json (longo):
{ "marca": "<b>Inema Pro</b> · RADAR SAÚDE", "avatar": {"img": "img/avatar-teste.jpg"},
  "capitulos": [ {"id": "c0", "titulo": "...", "kicker": "...", "takeaway": "..."},              # abertura: sem tela de nome
                 {"id": "c1", "nome": "Drauzio Varella", "kicker": "MÉDICO · ONCOLOGISTA", "sub": "Drauzio Varella · 08/10",
                  "foto": "img/<id>.jpg", "titulo": "...", "takeaway": "..."} ],
  "falas": [ {"id": "f1", "cap": "c0", "fala": "...", "fonte": "<b>Canal</b>, YouTube, 08/10/2026", "destaque": ["..."],
              "shots": [ {"type": "hook", "at": "@start", ...}, {"type": "numero", "at": "deixa falada", ...} ] } ] }

Tempos: "at" e todo campo "*_at" (inclusive dentro de items/lines/left/right) são DEIXAS — trecho literal de 1 a 5
palavras da própria fala; "trecho#2" = 2ª ocorrência; "@start" só no hook da 1ª fala. Deixa não achada = aviso e
cai no início da fala (a automação não para). Shots: os do explicavideo v2 (AUTHORING.md) + ficha, numero, citacao,
grafico, carimbo (motor/v2/saudeviral-v2.js).
"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

E = Path(sys.argv[1]).resolve()
AVATAR = "--avatar" in sys.argv
R = json.loads((E / "roteiro.json").read_text())
T = {t["id"]: t for t in json.loads((E / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())}
FALAS = R["falas"]
CAPS = {c["id"]: c for c in R["capitulos"]}
avisos = []


def n(s):
    return re.sub(r"[^a-z0-9%]", "", unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode())


def deixa(fid, cue):
    """instante (absoluto) em que a deixa é dita na fala fid."""
    if cue == "@start":
        return 0.0
    k = 1
    if "#" in cue:
        cue, k = cue.rsplit("#", 1); k = int(k)
    alvo = [n(w) for w in cue.split() if n(w)]
    ws = [n(p["w"]) for p in T[fid]["palavras"]]
    achou = 0
    for i in range(len(ws)):
        if all(i + j < len(ws) and (ws[i + j] == a or (j == len(alvo) - 1 and ws[i + j].startswith(a))) for j, a in enumerate(alvo)):
            achou += 1
            if achou == k:
                return T[fid]["palavras"][i]["t"]
    # tolerância: o ASR escreve diferente ("Drauzio"/"Dráuzio") — casa a 1ª palavra parecida
    par = difflib.get_close_matches(alvo[0] if alvo else "", ws, n=1, cutoff=0.8)
    if par:
        return T[fid]["palavras"][ws.index(par[0])]["t"]
    avisos.append(f"{fid}: deixa '{cue}' não achada")
    return T[fid]["ini"]


def tamanho(img):
    try:
        from PIL import Image
        with Image.open(img) as im:
            return im.size
    except Exception:
        return None


def resolve(fid, x, base):
    """troca deixas por segundos relativos à cena (base) e img/… por caminho absoluto, em qualquer profundidade."""
    if isinstance(x, list):
        return [resolve(fid, v, base) for v in x]
    if not isinstance(x, dict):
        return x
    out = {}
    for k, v in x.items():
        if (k == "at" or k.endswith("_at")) and isinstance(v, str):
            out[k] = round(max(0.0, deixa(fid, v) - base), 3)
        elif k in ("src", "foto") and isinstance(v, str) and v.startswith("img/"):
            out[k] = str(E / v)
            if k == "src" and (wh := tamanho(E / v)):
                out.setdefault("iw", wh[0]); out.setdefault("ih", wh[1])
        elif k == "fotos" and isinstance(v, list):
            out[k] = [str(E / x) if isinstance(x, str) and x.startswith("img/") else x for x in v]
        else:
            out[k] = resolve(fid, v, base)
    return out


ORDEM = [f["id"] for f in FALAS]
DUR = round(T[ORDEM[-1]]["fim"] + 1.5, 2)
cena = {"duracao": DUR, "marca": R.get("marca", ""), "cenas": [], "capitulos": [], "fontes": [], "legenda": []}
if R.get("avatar", {}).get("img"):
    cena["avatar_img"] = str(E / R["avatar"]["img"])

# cenas: uma por capítulo, do início da 1ª fala do capítulo até o início do próximo
grupos = []
for f in FALAS:
    if not grupos or grupos[-1][0] != f["cap"]:
        grupos.append((f["cap"], []))
    grupos[-1][1].append(f)
for k, (cid, fs) in enumerate(grupos):
    cap = CAPS[cid]
    ini = 0.0 if k == 0 else round(T[fs[0]["id"]]["ini"] - 0.05, 3)
    fim = DUR if k == len(grupos) - 1 else round(T[grupos[k + 1][1][0]["id"]]["ini"] - 0.05, 3)
    shots = []
    for f in fs:
        for s in f.get("shots", []):
            r = resolve(f["id"], s, ini)
            if "at" not in r:
                r["at"] = round(T[f["id"]]["ini"] - ini, 3)
            if r["type"] == "statement" and r.get("strike_at") is not None and "~~" not in r.get("text", ""):
                r["text"] = f"~~{r['text']}~~"  # pediu riscado sem marcar: risca a frase toda (nunca deixa a frase errada de pé)
            if r["type"] == "statement" and r.get("strike_at") is not None:
                r["strike_at"] = min(r["strike_at"], r["at"] + 1.2)  # frase errada não fica mais de ~1 s sem o risco
            shots.append(r)
    capa = bool(shots and shots[0].get("capa"))  # o v2 sempre desenha o cabeçalho: na cena da capa ele vai vazio
    cena["cenas"].append({"lang": "pt", "n": k + 1, "total": len(grupos), "chapter": "" if capa else cap.get("kicker", ""),
                          "title": "" if capa else cap.get("titulo", ""),
                          "takeaway": cap.get("takeaway") or None, "dur": round(fim - ini, 3), "ini": ini, "shots": shots,
                          "reel": False, "header": True})
    if cap.get("nome") and k:  # troca de assunto = tela limpa com o nome grande
        cena["capitulos"].append({"ini": ini, "fim": ini + 1.9, "nome": cap["nome"], "kicker": cap.get("kicker", ""),
                                  "sub": cap.get("sub", ""), "foto": str(E / cap["foto"]) if cap.get("foto") else None})

for f in FALAS:
    fid, a, b = f["id"], T[f["id"]]["ini"], T[f["id"]]["fim"]
    if f.get("fonte"):
        cena["fontes"].append({"html": f["fonte"], "ini": a, "fim": b + .1})
    # legenda: até 4 palavras e 26 letras por bloco (numa linha a 46 px); grafia do roteiro; "-feira" colado
    dest = {n(x) for x in f.get("destaque", [])}
    grafia = {}
    for tok in f["fala"].split():
        grafia.setdefault(tok.strip(".,;:!?\"'()").lower(), tok.strip("\"'()"))
    pal = []
    for p in T[fid]["palavras"]:
        w = p["w"]; nu = w.strip(".,;:!?").lower()
        if len(nu) >= 4 and nu not in grafia:
            par = difflib.get_close_matches(nu, list(grafia), n=1, cutoff=0.8)
            if par:
                p = {**p, "w": grafia[par[0]].rstrip(".,;:!?") + w[len(w.rstrip(".,;:!?")):]}
        if pal and p["w"].startswith("-"):
            pal[-1] = {**pal[-1], "w": pal[-1]["w"] + p["w"]}
        else:
            pal.append(p)
    blocos, cur = [], []
    for p in pal:
        if cur and (len(cur) == 4 or len(" ".join(x["w"] for x in cur + [p])) > 26):
            blocos.append(cur); cur = []
        cur.append(p)
    if cur:
        blocos.append(cur)
    for k, bl in enumerate(blocos):
        ws = [{"w": p["w"], "t": p["t"], **({"cor": "#ffb638"} if (any(ch.isdigit() for ch in p["w"]) or n(p["w"]) in dest) else {})} for p in bl]
        cena["legenda"].append({"ini": bl[0]["t"], "fim": blocos[k + 1][0]["t"] if k + 1 < len(blocos) else b, "palavras": ws})

(E / "cena-longo.js").write_text("window.CENA=" + json.dumps(cena, ensure_ascii=False) + ";")
print(f"cena-longo.js  {DUR:.1f} s  {len(ORDEM)} falas  {len(grupos)} capítulos  {sum(len(c['shots']) for c in cena['cenas'])} shots")
for a in avisos:
    print("aviso", a)
