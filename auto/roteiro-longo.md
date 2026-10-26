# Tarefa: roteiro do saudeviral LONGO 16:9 ({MODO}, {DATA})

Você monta o roteiro de um vídeo **16:9 de 5 a 7 minutos** do **saudeviral**, para o canal INEMA TIA no YouTube:
**"A semana explicada"**. O curto 9:16 da mesma rodada dá só o placar; este vídeo EXPLICA cada assunto: o que
cada influenciador disse, o que isso quer dizer, o contexto e os números com fonte. O Nei (avatar) apresenta.
Trabalhe só com os arquivos abaixo. Não use a internet nem outra API.

## Entrada
- Pasta da edição: `{ED}`. Escreva nela apenas os arquivos pedidos.
- Vídeos do período: `{ED}/videos.tsv` (handle, data, id, duração em s, views, canal, título).
- Transcrições: `{TX}/<id>/transcript.txt`, só dos ids em `{ED}/transcritos.txt`.
- Canais e ranking: `{RAIZ}/canais.json`.
- Esquema do roteiro e das deixas: docstring de `{RAIZ}/motor/gerar_cena_longo.py`.
- Tipos de shot: tabela "Primitivos" de `~/projetos/explicavideos/engine/v2/AUTHORING.md` + os de dados abaixo.
- Curto da mesma semana (para não contradizer): `{CURTO}/roteiro.json`, se existir.

## Modo
{INSTRUCAO_MODO}

## Saída
Grave TODOS estes arquivos, ou só o `SEM_PAUTA.txt`.

### 1. `{ED}/base.md`
Tabela `| Número ou fato usado | Quem disse | Vídeo | Data | Trecho da transcrição |`, uma linha por número OU fato
explicado no vídeo (no longo são de 12 a 30 linhas). **Vídeo** = id do videos.tsv. **Trecho** entre aspas retas,
cópia LITERAL de um pedaço contínuo do transcript.txt desse id, de 6 a 30 palavras, sem editar nem juntar pedaços.
Um script confere cada trecho; se algum não estiver no transcript, o vídeo é descartado.

### 2. `{ED}/roteiro.json` (formato longo — ver a docstring)
- `marca`: "<b>INEMA TIA</b> · RADAR SAÚDE". `avatar`: `{"img": "img/avatar-teste.jpg"}`.
- `capitulos`: `c0` = abertura (sem `nome`); depois **um capítulo por influenciador com assunto forte** (3 a 5
  capítulos; quem não disse nada relevante fica de fora); por último `cz` = fecho (sem `nome`). Cada capítulo de
  influenciador tem `nome`, `kicker` (o `rk` do canais.json, ex.: "MÉDICO · ONCOLOGISTA"), `sub` ("Canal · dd/mm"),
  `foto` `img/<id>.jpg`, `titulo` (o assunto em até 40 caracteres) e `takeaway` (frase de até 60 caracteres com
  `**destaque**`: a conclusão do capítulo).
- `falas`: de 30 a 60 falas, **de 800 a 1000 palavras no total** (≈ 5,5 a 7 min). Cada fala tem `id` (f1, f2…), `cap`,
  `fala`, `shots` (1 ou 2), `fonte` quando cita alguém ("<b>Fonte:</b> Canal, YouTube, dd/mm/aaaa · “título curto”")
  e `destaque` (palavras para a legenda em âmbar).

**Abertura (c0, 3 a 5 falas):**
- f1 começa com o shot `{"type":"hook","at":"@start","capa":true,"data":"{DATA_BR} · <DIA DA SEMANA>","linhas":[
  {"text":"A SEMANA EXPLICADA","size":96},{"text":"<NÚMERO MAIS FORTE>","size":150,"cor":"#3ef0a0"},
  {"text":"<linha âmbar curta>","size":92,"cor":"#ffb638"}],"sub":"<promessa>","fotos":["img/<id>.jpg", …]}`
  (fotos = miniaturas dos vídeos dos capítulos, até 5; SEM `src`).
- A 1ª frase diz o GANHO de quem assiste ("Em seis minutos você entende o que os maiores influenciadores de saúde
  disseram nesta semana e o que isso muda para você"). Nunca abrir com "Olá", "Neste vídeo" ou "Imagine".
- Depois, a prévia: um `bullets` (row) com os capítulos e um "no fim: …" que prende até o final.

**Cada capítulo de influenciador (5 a 10 falas, 120 a 200 palavras):**
1. Abre com o nome falado ("Agora, Drauzio Varella.") e o shot `ficha`.
2. O QUE ELE DISSE: shot `citacao` com o trecho literal (pode encurtar com "…"; o texto da citação TEM de estar no
   base.md) e, se houver, `numero` com o número principal.
3. O QUE ISSO QUER DIZER: a explicação, em linguagem simples, usando SÓ o que está nas transcrições (o raciocínio, os
   dados e os exemplos que ele mesmo deu). Pode definir termo básico (o que é colesterol, glicemia, microbiota). Nada de fato ou
   número de fora das transcrições. Visuais: `compare`, `timeline`, `bullets`, `flow`, `statement`, `grafico` (só
   série dita no vídeo), `carimbo` com `"keep": true` (POLÊMICA / ALERTA / SEM CONSENSO / ESTUDO).
4. Fecha com uma frase-síntese (é o `takeaway` do capítulo).
- Divergência entre eles (um recomenda, outro desaconselha) é ouro: mostre com `compare`, sempre atribuído.

**Fecho (cz, 3 a 5 falas):**
- Resumo em `bullets` (um item por capítulo).
- Gancho de comentário: pergunta sobre o tema ("E você? … Comente aqui."), com `fonte` "<b>Não substitui consulta
  médica.</b> Resumo do que os influenciadores disseram, com a fonte de cada fato".
- Última fala: CTA — ponte curta do tema para a IA + "Se prepare pra gestão de agentes de IA com o curso gratuito do inema
  ponto club." O CTA é SEMPRE só o inema.club: não citar canal do YouTube, "inscreva-se" nem outro destino. Shots: `{"type":"media","src":"img/cta.jpg","calm":true,"label":"**inema.club** · gestão de agentes de IA"}`
  e `keyword` "inema.club".

**Shots — regras:**
- `at` e todo `*_at` = DEIXA: trecho literal de 1 a 4 palavras da PRÓPRIA fala, só palavras comuns — nunca número,
  nem por extenso ("duzentos", "sete vírgula", "por cento"): o tempo vem do Whisper, que escreve número em algarismo.
  Repetida na fala → `"trecho#2"`. Os itens internos (`items`, `lines`, `events`) entram nas deixas das palavras
  ditas, em ordem.
- O visual muda a cada ≤ 10 s (≈ a cada 25 palavras): nunca 3 falas seguidas sem shot novo.
- Área útil à esquerda; textos curtos e grandes: `bullets` ≤ 4 itens de ≤ 40 caracteres; `compare` ≤ 3 linhas por
  lado; `timeline` ≤ 5 eventos; `label` de `media` ≤ 40 caracteres.
- `statement` com `strike_at`: marque com `~~…~~` a parte ERRADA ("Ovo ~~aumenta o colesterol de todo mundo~~"); sem a marca
  a frase errada fica de pé na tela.
- Na TELA os números podem ir em algarismo ("2.000 mg", "+30%"); na FALA, sempre por extenso.
- Miniatura do vídeo citado: `{"type":"media","src":"img/<id>.jpg","calm":true,"zoom":[1,1.15],"label":"Canal · dd/mm"}`.
- Dados: `ficha {foto, rk, nome, canal}`, `numero {k, ate, de?, dec?, pre?, unid?, cor?, seta?("▲"|"▼"), l?}`,
  `citacao {q, w, k?}`, `grafico {serie[], cor?, rotulo}`, `carimbo {txt, cor?}` (com `"keep": true`).

**Texto falado:** tom do Nei, tratando por "você" (nunca "tu"/"teu"), frases curtas; TODOS os números e anos por extenso ("trinta por cento", "dois mil e vinte e seis"); siglas comuns em maiúsculas (SUS, OMS, IMC, Anvisa);
sem emoji. **Saúde (regras duras):**
  - Relatar e atribuir sempre ("segundo ele", "ela recomenda"). Nunca vira conselho do Nei.
  - Nada de dose, remédio, suplemento, jejum ou dieta como instrução para quem assiste. Quando citar, fechar com "fale com seu médico antes".
  - Promessa de cura, tratamento sem consenso científico, discurso antivacina ou contra tratamento estabelecido NÃO vira manchete. Se entrar, vem com `carimbo` "SEM CONSENSO" e a fala diz que isso não tem consenso na medicina. Na dúvida, fica de fora.
  - Polêmica é o que ELES disseram. Política: atribuída, sem lado, sem opinião do Nei.

### 3. `{ED}/legenda.txt`
Linha 1: título para o YouTube (até 70 caracteres, gancho, pode ter número). Linhas 2–6: descrição curta com um
item por capítulo ("Drauzio Varella: o que muda com a nova vacina"). Última linha: "Não substitui consulta
médica."

### Sem pauta
Se a semana não tiver pelo menos 3 assuntos fortes, grave só `{ED}/SEM_PAUTA.txt` com o motivo.
