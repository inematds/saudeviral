#!/usr/bin/env python3
"""Portão antes do render: confere roteiro.json e base.md de uma edição gerada pela automação.
uso: auto/checar.py <pasta-da-edicao> [pasta-tx] [--longo]
Sai 0 se ok; 1 com a lista de problemas (o vídeo não é feito nem enviado)."""
import json, os, re, sys, unicodedata
from pathlib import Path

LONGO = "--longo" in sys.argv  # vídeo longo 16:9 (roteiro de gerar_cena_longo.py): outros limites + deixas dos shots
args = [a for a in sys.argv[1:] if a != "--longo"]
E = Path(args[0]).resolve()
TX = Path(args[1] if len(args) > 1 else Path.home() / "projetos/output/saudeviral/coleta/tx")
erros = []


def n(s):
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9%]+", " ", s)).strip()


NUMERAIS = set("dois tres quatro cinco seis sete oito nove dez onze doze treze quatorze catorze quinze dezesseis dezessete dezoito "
               "dezenove vinte trinta quarenta cinquenta sessenta setenta oitenta noventa cem cento duzentos trezentos "
               "quatrocentos quinhentos seiscentos setecentos oitocentos novecentos mil milhao milhoes bilhao bilhoes "
               "trilhao virgula".split())
ids = {l.split("\t")[2] for l in (E / "videos.tsv").read_text().splitlines() if l.count("\t") >= 6}

# base.md: cada trecho é cópia literal do transcript do vídeo citado
linhas = [l for l in (E / "base.md").read_text().splitlines() if l.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", l)]
linhas = [l for l in linhas if "Trecho" not in l]
MIN_FATOS = 10 if LONGO else 3
if len(linhas) < MIN_FATOS:
    erros.append(f"base.md com {len(linhas)} linhas (mínimo {MIN_FATOS})")
for l in linhas:
    cols = [c.strip() for c in l.strip("|").split("|")]
    vid = next((c for c in cols if c.strip("` ") in ids), None)
    if not vid:
        erros.append(f"base.md: linha sem id do videos.tsv: {l[:90]}")
        continue
    vid = vid.strip("` ")
    trechos = re.findall(r'"([^"]{20,})"', cols[-1])  # trecho = última coluna
    if not trechos:
        erros.append(f"base.md: linha sem trecho entre aspas: {l[:90]}")
        continue
    t = TX / vid / "transcript.txt"
    if not t.exists():
        erros.append(f"base.md: {vid} sem transcrição")
        continue
    alvo = n(t.read_text())
    for tr in trechos:
        partes = [p for p in re.split(r"\.\.\.|…", tr) if len(p.strip()) > 8]
        if not all(n(p) in alvo for p in partes):
            erros.append(f"base.md: trecho NÃO está no transcript de {vid}: \"{tr[:80]}\"")

# curto = resumo dos dez com pelo menos 5 assuntos (Nei, 13/10/2026): conta os vídeos distintos do base.md.
# MIN_ASSUNTOS vem do rodar.sh (menor só quando o período teve menos vídeos transcritos).
if not LONGO:
    vids = {v for l in linhas for v in re.findall(r"[\w-]{11}", l) if v in ids}
    MIN_ASS = int(os.environ.get("MIN_ASSUNTOS", "5"))
    if len(vids) < MIN_ASS:
        erros.append(f"{len(vids)} assuntos (vídeos distintos no base.md); mínimo {MIN_ASS}")
    try:
        _F = json.loads((E / "roteiro.json").read_text()).get("falas", [])
    except Exception:
        _F = []
    nass = [f.get("assunto") for f in _F if f.get("assunto")]
    if len(nass) < MIN_ASS:
        erros.append(f"{len(nass)} falas com \"assunto\" (a 1ª fala de cada assunto; mínimo {MIN_ASS})")
    if any(len(a) > 24 for a in nass):
        erros.append("\"assunto\" com mais de 24 letras (não cabe no cartão)")

# roteiro.json
try:
    R = json.loads((E / "roteiro.json").read_text())
except Exception as ex:
    sys.exit(f"roteiro.json inválido: {ex}")
F = R.get("falas", [])
FMIN, FMAX = (25, 70) if LONGO else (4, 22)  # curto: resumo dos dez com 5+ assuntos (Nei, 13/10/2026)
if not FMIN <= len(F) <= FMAX:
    erros.append(f"{len(F)} falas (esperado {FMIN} a {FMAX})")
if LONGO:
    caps = {c.get("id") for c in R.get("capitulos", [])}
    if len(caps) < 4:
        erros.append(f"{len(caps)} capítulos (mínimo 4: abertura, 2+ influenciadores, fecho)")
    s0 = (F[0].get("shots") or [{}])[0] if F else {}
    if not (s0.get("type") == "hook" and s0.get("at") == "@start" and s0.get("capa")):
        erros.append("f1 não abre com a capa (hook capa em @start)")
elif not R.get("hero"):
    erros.append("sem hero (quadro 0)")
vistos = set()
for f in F:
    fid = f.get("id")
    if not fid or fid in vistos:
        erros.append(f"id de fala vazio ou repetido: {fid}")
    vistos.add(fid)
    fala = f.get("fala", "")
    if len(fala.split()) < 4:
        erros.append(f"{fid}: fala curta demais")
    if re.search(r"(?<![A-Za-z])\d", fala):
        erros.append(f"{fid}: número em algarismo na fala (escrever por extenso): {fala[:80]}")
    for k in ("numero", "grafico", "carimbo", "caixa", "ficha"):
        a = (f.get(k) or {}).get("em")
        if a and re.search(r"\d", a):
            erros.append(f"{fid}: âncora '{a}' com número")
    if LONGO:
        if f.get("cap") not in caps:
            erros.append(f"{fid}: capítulo '{f.get('cap')}' não existe")
        alvo_fala = " " + n(fala) + " "
        def deixas(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if (k == "at" or k.endswith("_at")) and isinstance(v, str):
                        yield v
                    else:
                        yield from deixas(v)
            elif isinstance(x, list):
                for v in x:
                    yield from deixas(v)
        for d in deixas(f.get("shots", [])):
            if d == "@start":
                continue
            if re.search(r"\d", d) or set(n(d.split("#")[0]).split()) & NUMERAIS:
                erros.append(f"{fid}: deixa '{d}' com número (o Whisper escreve em algarismo; usar palavra comum)")
            elif " " + n(d.split("#")[0]) + " " not in alvo_fala:
                erros.append(f"{fid}: deixa '{d}' não está na fala")
    for img in re.findall(r"img/[\w.-]+", json.dumps(f)):
        if not (E / img).exists():
            erros.append(f"{fid}: imagem ausente {img}")
for f in F:
    if re.search(r"ponto gov|gov ponto", f.get("fala", ""), re.I):
        erros.append(f"{f.get('id')}: gov.br se fala 'gov bê érre', sem 'ponto' (Nei, 13/10/2026)")
    fala = f.get("fala", "")
    if re.search(r"\b(tu|teu|tua|teus|tuas|ti|contigo|te prepara)\b", fala, re.I):
        erros.append(f"{f.get('id')}: trata por 'tu' (usar 'você'): {fala[:80]}")
    if re.search(r"inema pro\b|v[ií]deo longo|inscrev|canal do youtube", fala, re.I):
        erros.append(f"{f.get('id')}: CTA é só o inema.club (sem canal do YouTube nem vídeo longo): {fala[:80]}")
if not LONGO and F and R.get("hero") and any(F[0].get(k) for k in ("numero", "ficha", "caixa", "carimbo")):
    erros.append("f1 com numero/ficha/caixa/carimbo por cima do hero (o número já está no hero)")
if F and "inema" not in F[-1].get("fala", "").lower():
    erros.append("última fala sem CTA do inema")
if "não substitui consulta médica" not in json.dumps(R, ensure_ascii=False).lower():
    erros.append("falta 'Não substitui consulta médica'")
palavras = sum(len(f.get("fala", "").split()) for f in F)
if not LONGO and palavras > 420:
    erros.append(f"{palavras} palavras (curto: até 420, senão passa de 3 min e deixa de ser Short)")
if LONGO and not 650 <= palavras <= 1150:
    erros.append(f"{palavras} palavras (longo: 650 a 1150, ≈ 5 a 7 min)")
print(f"{len(F)} falas · {palavras} palavras · {len(linhas)} fatos no base.md")
if erros:
    print("\n".join("PROBLEMA " + e for e in erros))
    sys.exit(1)
print("ok")
