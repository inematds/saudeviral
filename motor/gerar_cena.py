#!/usr/bin/env python3
"""uso: motor/gerar_cena.py <pasta-da-edicao> [--avatar | --livre]
--livre: tempos.json do narrar.py, mas âncora não achada cai no início da fala (automação).
--avatar: tempos de avatar/tempos.json (fala do HeyGen, saída do retempo.py); âncora não achada cai no início da fala.
Monta cena.js a partir de roteiro.json (falas + visuais) e tempos.json (tempo de cada palavra, saída do narrar.py).
Cada visual pode ter "em": "palavra" (aparece quando a palavra é dita) — senão entra no início da fala.

roteiro.json:
{ "marca": "...", "selo": "...", "avatar": {"img": "img/x.jpg", "tag": "..."},
  "hero": "<html do quadro 0>",            # fica do t=0 até o fim da 1ª fala
  "falas": [ {"id": "f1", "fala": "...", "fundo": "img/a.jpg",
              "ficha": {"nome","canal","foto","rk"}, "numero": {"k","ate","de","dec","pre","unid","cor","l","seta","em"},
              "grafico": {"serie":[...],"cor","rotulo","em"}, "carimbo": {"txt","em","cor"},
              "caixa": {"k","q","w"} | {"k","itens":[{"txt","em"}]} | {"tipo":"cta","a","b"},
              "fonte": "<html>", "destaque": ["palavra", ...] } ] }
"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

E = Path(sys.argv[1]).resolve()
AVATAR = "--avatar" in sys.argv
LIVRE = AVATAR or "--livre" in sys.argv  # automação: âncora não achada não derruba o vídeo
R = json.loads((E / "roteiro.json").read_text())
T = {t["id"]: t for t in json.loads((E / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())}
ORDEM = [f["id"] for f in R["falas"]]


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def em(fid, palavra, k=1):
    """instante em que a k-ésima ocorrência de `palavra` é dita na fala `fid`."""
    achou = 0
    for p in T[fid]["palavras"]:
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    msg = f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in T[fid]["palavras"])
    if LIVRE:  # outra voz, outra transcrição: não derruba o vídeo, entra no início da fala
        print("aviso", msg[:160])
        return T[fid]["ini"]
    raise KeyError(msg)


ini = lambda fid: T[fid]["ini"]
fim = lambda fid: T[fid]["fim"]
DUR = round(fim(ORDEM[-1]) + 1.2, 2)
cena = {"duracao": DUR, "marca": R["marca"], "selo": R["selo"], "fundos": [], "hero": [], "fichas": [], "numeros": [],
        "graficos": [], "carimbos": [], "caixas": [], "fontes": [], "legenda": []}
if R.get("avatar"):
    cena["avatar"] = {**R["avatar"], "img": str(E / R["avatar"]["img"]), "ini": -1, "fim": DUR + 1}
def chamada(hero):
    """quadro 0 diz com todas as letras que é o RESUMO do que os influenciadores falaram (Nei, 11/10/2026):
    faixa vermelha no lugar da etiqueta de data (a data vai junto) e sem o t4, que repetia isso em letra miúda."""
    modo = E.name.split("-")[3] if E.name.count("-") >= 3 else ""
    area = "SAÚDE" if "SAÚDE" in R.get("marca", "").upper() else "FINANÇAS"
    nomes = {f["ficha"]["nome"] for f in R["falas"] if f.get("ficha", {}).get("nome")}
    quem = f"{len(nomes)} INFLUENCIADORES" if len(nomes) >= 2 else "OS INFLUENCIADORES"
    l1 = {"diario": "RESUMO DO DIA", "semanal": "RESUMO DA SEMANA", "domingo": "RESUMO DA SEMANA"}.get(modo, "RESUMO")
    l2 = f"O QUE {quem} DE {area} FALARAM" + (" E ESPERAM PARA A PRÓXIMA" if modo == "domingo" else "")
    dt = re.search(r'<div class="dt">(.*?)</div>', hero)
    html = f'<div class="chamada"><div class="c1"><i></i>{l1}</div><div class="c2">{l2}</div>' \
           + (f'<div class="c3">{dt.group(1)}</div>' if dt else "") + "</div>"
    hero = re.sub(r'<div class="t4">.*?</div>', "", hero)
    return hero.replace(dt.group(0), html) if dt else html + hero


if R.get("hero"):
    cena["hero"].append({"ini": -1, "fim": fim(ORDEM[0]) - .05, "html": chamada(R["hero"]).replace('src="img/', f'src="{E}/img/')
                         .replace("url('img/", f"url('{E}/img/")})


def t0(fid, v):
    return em(fid, v["em"]) - .1 if v.get("em") else ini(fid)


fundo_atual = None
for i, f in enumerate(R["falas"]):
    fid = f["id"]
    a, b = ini(fid), fim(fid)
    # fim do bloco = início da próxima fala que troca aquele visual (evita piscar entre falas)
    prox = lambda chave: next((ini(g["id"]) for g in R["falas"][i + 1:] if g.get(chave) or g.get("limpa")), DUR + 1)
    if f.get("fundo") and f["fundo"] != fundo_atual:
        if cena["fundos"]:
            cena["fundos"][-1]["fim"] = a + .3
        cena["fundos"].append({"img": str(E / f["fundo"]), "ini": a - .3 if i else -1, "fim": DUR + 1})
        fundo_atual = f["fundo"]
    # f1 com hero: o número já está no quadro 0; nada por cima dele (finviral 11/10 saiu "+3,4%" sobre "+7,7%")
    if not i and R.get("hero"):
        f = {k: v for k, v in f.items() if k not in ("numero", "ficha", "caixa", "carimbo", "grafico")}
    if f.get("hero") and i:
        cena["hero"].append({"ini": a - .05, "fim": DUR + 1, "html": f["hero"].replace('src="img/', f'src="{E}/img/')})
    if f.get("ficha"):
        cena["fichas"].append({**f["ficha"], "foto": str(E / f["ficha"]["foto"]), "ini": t0(fid, f["ficha"]), "fim": prox("ficha")})
    if f.get("numero"):
        # entra no início da fala e fica até o próximo número, ficha ou tela limpa (a parte de cima não fica vazia)
        fim_n = next((ini(g["id"]) for g in R["falas"][i + 1:] if g.get("numero") or g.get("ficha") or g.get("limpa") or g.get("hero")), DUR + 1)
        cena["numeros"].append({**f["numero"], "ini": a - .05, "fim": fim_n})
    if f.get("grafico"):
        cena["graficos"].append({**f["grafico"], "ini": t0(fid, f["grafico"]), "fim": b + .1})
    if f.get("carimbo"):
        cena["carimbos"].append({**f["carimbo"], "ini": t0(fid, f["carimbo"]), "fim": b + .1})
    if f.get("caixa"):
        c = dict(f["caixa"])
        if c.get("itens"):
            c["itens"] = [{"txt": it["txt"], "t": em(fid, it["em"]) if it.get("em") else a} for it in c["itens"]]
        cena["caixas"].append({**c, "ini": t0(fid, c), "fim": b + (1.2 if fid == ORDEM[-1] else .1)})
    if f.get("fonte"):
        cena["fontes"].append({"html": f["fonte"], "ini": a, "fim": b + .1})
    # legenda: blocos de até 3 palavras e até 18 letras (cabe numa linha); números e destaques em amarelo
    dest = {n(x) for x in f.get("destaque", [])}
    pal = []
    grafia = {}  # grafia do roteiro (o Whisper erra nome próprio: "Dráuzio" por "Drauzio")
    for tok in f["fala"].split():
        grafia.setdefault(tok.strip(".,;:!?\"'()").lower(), tok.strip("\"'()"))
    for p in T[fid]["palavras"]:  # o Whisper separa "segunda" de "-feira": cola de volta
        w = p["w"]; nu = w.strip(".,;:!?").lower()
        if len(nu) >= 4 and nu not in grafia:
            par = difflib.get_close_matches(nu, list(grafia), n=1, cutoff=0.8)
            if par:
                p = {**p, "w": grafia[par[0]].rstrip(".,;:!?") + w[len(w.rstrip(".,;:!?")):]}
        # o Whisper parte número: "15" "%" ou "7" ",7" → "15%", "7,7"
        if pal and pal[-1]["w"][-1:].isdigit() and re.match(r"^([.,]\d|%)", p["w"]):
            pal[-1] = {**pal[-1], "w": pal[-1]["w"] + p["w"]}
        elif pal and p["w"].startswith("-"):
            pal[-1] = {**pal[-1], "w": pal[-1]["w"] + p["w"]}
        else:
            pal.append(p)
    blocos, cur = [], []
    for p in pal:
        if cur and (len(cur) == 3 or len(" ".join(x["w"] for x in cur + [p])) > 18):
            blocos.append(cur); cur = []
        cur.append(p)
    if cur: blocos.append(cur)
    for k, bloco in enumerate(blocos):
        ws = [{"w": p["w"], "t": p["t"], **({"cor": "#ffd23f"} if (any(ch.isdigit() for ch in p["w"]) or n(p["w"]) in dest) else {})}
              for p in bloco]
        fimb = blocos[k + 1][0]["t"] if k + 1 < len(blocos) else b
        cena["legenda"].append({"ini": bloco[0]["t"], "fim": fimb, "palavras": ws})

(E / "cena.js").write_text("window.CENA=" + json.dumps(cena, ensure_ascii=False) + ";")
print(f"cena.js  {DUR:.1f} s  {len(ORDEM)} falas")
for fid in ORDEM:
    print(fid, ini(fid), "→", fim(fid))
