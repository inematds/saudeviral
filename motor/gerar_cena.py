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

# respiros (Nei, 14/10/2026): 1 s de pausa com cartão de virada antes de cada assunto ("assunto" na fala) e antes da
# pergunta (penúltima fala). A cena é deslocada aqui; o áudio/vídeo ganha o mesmo buraco no motor/respiros.py.
VIRA = 1.0
ASS = [i for i, f in enumerate(R["falas"]) if f.get("assunto")]
PERG = len(ORDEM) - 2 if len(ORDEM) >= 4 else None
RESP = []  # corte na linha ORIGINAL do áudio
for i in sorted({i for i in ASS if i} | ({PERG} if PERG else set())):
    a0, a1 = T[ORDEM[i - 1]]["fim"], T[ORDEM[i]]["ini"]
    RESP.append({"t": round((a0 + a1) / 2 if a1 > a0 else a1, 3), "dur": VIRA, "i": i})
desloca = lambda x: round(x + sum(r["dur"] for r in RESP if x >= r["t"]), 3)
for t_ in T.values():
    t_["ini"], t_["fim"] = desloca(t_["ini"]), desloca(t_["fim"])
    for p_ in t_["palavras"]:
        p_["t"] = desloca(p_["t"])
        if "f" in p_:
            p_["f"] = desloca(p_["f"])
(E / "respiros.json").write_text(json.dumps(RESP))


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
NUMW = {"zero", "um", "uma", "dois", "duas", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze", "treze",
        "quatorze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove", "vinte", "trinta", "quarenta", "cinquenta",
        "sessenta", "setenta", "oitenta", "noventa", "cem", "cento", "duzentos", "duzentas", "trezentos", "trezentas", "quatrocentos",
        "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos", "mil", "milhao", "milhoes", "bilhao", "bilhoes", "trilhao", "trilhoes", "virgula", "porcento"}
TELA = {r"\bésse ú ésse\b": "SUS", r"\binema ponto club\b": "inema.club", r"\binema club\b": "inema.club"}


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
    # f1 com hero: o número já está no quadro 0; nada por cima dele (11/10 saiu "+3,4%" sobre "+7,7%")
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
    grafia = {}  # grafia do roteiro (o Whisper erra nome próprio: "Ambima" por "Anbima")
    for tok in f["fala"].split():
        grafia.setdefault(tok.strip(".,;:!?\"'()").lower(), tok.strip("\"'()"))
    # o texto da legenda é o do ROTEIRO; do Whisper só o tempo (e o número em algarismo). Em 11/10 ele ouviu
    # "Segundo o assunto" onde o roteiro dizia "Segundo assunto" e a palavra inventada foi para a tela.
    # grafia falada → grafia da tela (a voz lê "ésse ú ésse", a tela mostra SUS)
    txt = f["fala"]
    for de, para in TELA.items():
        txt = re.sub(de, para, txt, flags=re.I)
    rot, ouv = txt.split(), T[fid]["palavras"]
    # número por extenso no roteiro e em algarismo no Whisper: os dois viram um "#" para o alinhamento,
    # e o número da tela é sempre o do Whisper ("dois mil e vinte" × "2020.")
    def grupos(ws, eh_num):
        g = []
        for k, w in enumerate(ws):
            if eh_num(k) and g and g[-1][0] == "#":
                g[-1][2] = k + 1
            else:
                g.append(["#" if eh_num(k) else n(w), k, k + 1])
        return g
    nr = lambda k: n(rot[k]) in NUMW or (n(rot[k]) == "e" and 0 < k < len(rot) - 1 and n(rot[k - 1]) in NUMW and n(rot[k + 1]) in NUMW) \
        or (n(rot[k]) == "por" and k + 1 < len(rot) and n(rot[k + 1]) == "cento")
    no = lambda k: re.search(r"[\d%]", ouv[k]["w"]) is not None or (ouv[k]["w"].startswith(",") and k > 0) \
        or (k > 0 and n(ouv[k]["w"]) in NUMW and re.search(r"\d", ouv[k - 1]["w"]) is not None)  # "35" "mil"
    gr, go = grupos(rot, nr), grupos([p["w"] for p in ouv], no)
    lista = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [g[0] for g in gr], [g[0] for g in go], autojunk=False).get_opcodes():
        rs = [w for g in gr[i1:i2] for w in rot[g[1]:g[2]]]
        os_ = [p for g in go[j1:j2] for p in ouv[g[1]:g[2]]]
        tem_num = any(g[0] == "#" for g in gr[i1:i2] + go[j1:j2])
        if op == "equal":
            for gi, gj in zip(gr[i1:i2], go[j1:j2]):
                if gi[0] == "#":
                    lista += ouv[gj[1]:gj[2]]
                else:  # palavra do roteiro, maiúscula como o Whisper ouviu ("2020. E pra", não "e pra")
                    w = rot[gi[1]].strip("\"'()"); o = ouv[gj[1]]
                    lista.append({**o, "w": (w[:1].upper() + w[1:]) if o["w"][:1].isupper() else w})
        elif op == "replace" and not tem_num and rs and os_:
            # "para a semana" ouvido × "pra semana" escrito: palavras do roteiro repartidas no tempo do trecho
            t0_, t1_ = os_[0]["t"], os_[-1]["f"]
            lista += [{"w": w.strip("\"'()"), "t": round(t0_ + k * (t1_ - t0_) / len(rs), 3),
                       "f": round(t0_ + (k + 1) * (t1_ - t0_) / len(rs), 3)} for k, w in enumerate(rs)]
        elif op in ("replace", "insert"):  # com número: fica o que o Whisper ouviu; palavra inventada sem número sai
            lista += [p for p in os_ if op == "replace" or re.search(r"[\d%]", p["w"]) or p["w"].startswith("-")]
    for p in lista:  # o Whisper separa "segunda" de "-feira": cola de volta
        w = p["w"]; nu = w.strip(".,;:!?").lower()
        if len(nu) >= 4 and nu not in grafia:
            par = difflib.get_close_matches(nu, list(grafia), n=1, cutoff=0.8)
            if par:
                p = {**p, "w": grafia[par[0]].rstrip(".,;:!?") + w[len(w.rstrip(".,;:!?")):]}
        # o Whisper parte número: "7" ",7" "%" → "7,7%"
        if pal and pal[-1]["w"][-1:].isdigit() and re.match(r"^([.,]\d|%)", p["w"]):
            pal[-1] = {**pal[-1], "w": pal[-1]["w"] + p["w"]}
        elif pal and pal[-1]["w"][-1:].isdigit() and n(p["w"]) in ("mil", "milhoes", "bilhoes", "trilhoes", "milhao", "bilhao", "trilhao"):
            pal[-1] = {**pal[-1], "w": pal[-1]["w"] + " " + p["w"]}  # "35 mil" fica no mesmo bloco da legenda
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

# cartão de virada (tela cheia), manchete no topo quando não há ficha/número, índice no lugar da caixa vazia (Nei, 14/10/2026)
NASS = len(ASS)
cena["viradas"], acum = [], 0.0
for r in RESP:
    t_ = r["t"] + acum; acum += r["dur"]; f = R["falas"][r["i"]]
    if r["i"] in ASS:
        cena["viradas"].append({"ini": t_, "fim": t_ + r["dur"], "k": f"ASSUNTO {ASS.index(r['i']) + 1} DE {NASS}",
                                "txt": f["assunto"], "img": str(E / f["fundo"]) if f.get("fundo") else ""})
    else:
        cena["viradas"].append({"ini": t_, "fim": t_ + r["dur"], "k": "AGORA É COM VOCÊ", "txt": "E VOCÊ?", "img": ""})
cena["manchetes"], atual = [], None
for i, f in enumerate(R["falas"]):
    if i in ASS:
        atual = (ASS.index(i) + 1, f["assunto"])
    if not i or f.get("hero") or i == len(ORDEM) - 1:
        continue
    fid = f["id"]; prox_ini = ini(ORDEM[i + 1]) - .05
    if f.get("manchete"):
        m = {"k": f"{NASS} ASSUNTOS" if f.get("caixa", {}).get("itens") and NASS else "", "txt": f["manchete"]}
    elif i == PERG:
        m = {"k": "COMENTE AQUI", "txt": "E AÍ, NA SUA CIDADE?"}
    elif atual:
        m = {"k": f"ASSUNTO {atual[0]} DE {NASS}", "txt": atual[1]}
    elif f.get("caixa", {}).get("itens"):
        m = {"k": f"{len(ASS) or len(f['caixa']['itens'])} ASSUNTOS", "txt": "HOJE NO RADAR"}
    else:
        continue
    cena["manchetes"].append({**m, "ini": ini(fid) - .05, "fim": prox_ini})
if ASS:
    cena["indice"] = {"itens": [R["falas"][i]["assunto"] for i in ASS], "t": [ini(ORDEM[i]) - .05 for i in ASS],
                      "ini": ini(ORDEM[ASS[0]]) - .05, "fim": ini(ORDEM[PERG]) - .05 if PERG else DUR + 1}

(E / "cena.js").write_text("window.CENA=" + json.dumps(cena, ensure_ascii=False) + ";")
print(f"cena.js  {DUR:.1f} s  {len(ORDEM)} falas")
for fid in ORDEM:
    print(fid, ini(fid), "→", fim(fid))
