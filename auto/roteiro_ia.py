#!/usr/bin/env python3
"""Contrato texto -> arquivos dos virais; nenhuma ferramenta de escrita/publicação no modelo."""
import argparse, ast, json, re, sys, tempfile
from pathlib import Path
from ia_motor import executar
RAIZ=Path(__file__).resolve().parent.parent
PERMITIDOS={'base.md','roteiro.json','legenda.txt','sugestao.txt','SEM_PAUTA.txt'}

def salvar(resposta, pasta):
    dados=json.loads(resposta)
    arquivos=dados.get('arquivos') if isinstance(dados,dict) else None
    if not isinstance(arquivos,dict) or not arquivos or set(arquivos)-PERMITIDOS:
        raise ValueError('Saída exige arquivos com nomes permitidos')
    if 'SEM_PAUTA.txt' in arquivos:
        if set(arquivos)!={'SEM_PAUTA.txt'} or not str(arquivos['SEM_PAUTA.txt']).strip():
            raise ValueError('Sem pauta deve conter somente o motivo')
    elif not {'base.md','roteiro.json','legenda.txt'} <= set(arquivos):
        raise ValueError('Faltam base.md, roteiro.json ou legenda.txt')
    prontos={}
    for nome,valor in arquivos.items():
        if nome=='roteiro.json':
            obj=json.loads(valor) if isinstance(valor,str) else valor
            if not isinstance(obj,dict) or not obj: raise ValueError('roteiro.json inválido')
            valor=json.dumps(obj,ensure_ascii=False,indent=2)
        if not isinstance(valor,str) or not valor.strip(): raise ValueError('Arquivo vazio/inválido: '+nome)
        prontos[nome]=valor+'\n'
    # Toda a resposta é validada antes da primeira escrita; cada arquivo é trocado atomicamente.
    for nome,valor in prontos.items():
        with tempfile.NamedTemporaryFile(mode='w',dir=pasta,delete=False) as f:
            f.write(valor); tmp=Path(f.name)
        tmp.replace(pasta/nome)
    if 'SEM_PAUTA.txt' not in prontos:
        (pasta/'SEM_PAUTA.txt').unlink(missing_ok=True)
    return list(prontos)

def entradas(pedido,pasta,tx):
    textos=[]
    def anexar(q):
        if q.is_file(): textos.append(f'\n<arquivo caminho="{q}">\n{q.read_text()}\n</arquivo>')
    for q in [pasta/'videos.tsv',pasta/'transcritos.txt',RAIZ/'canais.json']:
        anexar(q)
    ids=(pasta/'transcritos.txt').read_text().split()
    if not ids or any(not re.fullmatch(r'[A-Za-z0-9_-]+',v) for v in ids): raise ValueError('Lista de transcrições inválida')
    for vid in ids:
        q=tx/vid/'transcript.txt'
        if not q.is_file(): raise ValueError('Transcrição ausente: '+vid)
        anexar(q)
    # Referências e esquema presentes no pedido já expandido, só dentro do próprio projeto.
    for path in dict.fromkeys(re.findall(r'`(/[^`\n]+\.(?:json|md|py))`',pedido)):
        q=Path(path).resolve()
        if not q.is_relative_to(RAIZ) or not q.is_file() or q in [pasta/'roteiro.json',pasta/'base.md']: continue
        if q.suffix=='.py':
            doc=ast.get_docstring(ast.parse(q.read_text()))
            if doc: textos.append(f'\n<esquema caminho="{q}">\n{doc}\n</esquema>')
        else: anexar(q)
    for nome in ['roteiro.json','base.md']:
        anexar(pasta/nome)  # Em correção, preservar a resposta anterior e ajustar os erros do portão.
    return ''.join(textos)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('etapa'); ap.add_argument('pedido'); ap.add_argument('--tx',required=True,type=Path)
    a=ap.parse_args(); pasta=Path.cwd()
    prompt=a.pedido+entradas(a.pedido,pasta,a.tx)
    prompt+='''\n\nCONTRATO FINAL DO EXECUTOR: todos os dados necessários estão anexados. Não leia/escreva arquivos nem execute comandos, não pesquise na internet nem use APIs. As instruções anteriores de gravar arquivos serão cumpridas pelo script, não pelo modelo. Responda SOMENTE um objeto JSON: {"arquivos":{"base.md":"conteúdo completo","roteiro.json":{...objeto completo...},"legenda.txt":"conteúdo completo","sugestao.txt":"opcional"}}. Se não houver pauta, responda {"arquivos":{"SEM_PAUTA.txt":"motivo"}}. Nunca misture sem-pauta com roteiro. Nenhum outro arquivo é permitido. Não escreva crases ou explicações fora do JSON.'''
    resposta=executar(a.etapa,prompt,pasta)
    print(json.dumps({'arquivos_salvos':salvar(resposta,pasta)},ensure_ascii=False))
if __name__=='__main__':
    try: main()
    except Exception as e: print('IA roteiro: '+str(e),file=sys.stderr); sys.exit(1)
