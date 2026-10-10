# Tarefa: roteiro do saudeviral ({MODO}, {DATA})

Você monta o roteiro de um vídeo 9:16 do **saudeviral**: o que os maiores influenciadores de saúde do Brasil (médicos, nutricionistas e psicólogos com maior audiência) disseram, com números grandes, fonte na tela, o Nei comentando e CTA do inema.club no fim. Trabalhe só com os arquivos abaixo. Não use a internet nem outra API.

## Entrada
- Pasta da edição: `{ED}`. Escreva nela apenas os arquivos pedidos.
- Vídeos do período: `{ED}/videos.tsv`, com as colunas handle, data, id, duração em segundos, views, canal e título.
- Transcrições: `{TX}/<id>/transcript.txt`. Só existem as dos ids listados em `{ED}/transcritos.txt`.
- Canais e ranking: `{RAIZ}/canais.json`.
- Edição de referência (do finviral, projeto irmão, aprovada pelo Nei). Copie SÓ o formato dela; o assunto é outro:
  - `{RAIZ}/edicoes/referencia/roteiro.json`
  - `{RAIZ}/edicoes/referencia/base.md`
- Esquema do roteiro: docstring de `{RAIZ}/motor/gerar_cena.py`.

## Modo
{INSTRUCAO_MODO}

## Saída
Grave TODOS estes arquivos, ou só o `SEM_PAUTA.txt`.

### 1. `{ED}/base.md`
Uma tabela com as colunas `| Número usado | Quem disse | Vídeo | Data | Trecho da transcrição |`. Regras:
- Uma linha por número ou fato que aparece no vídeo.
- **Vídeo** é o id do YouTube, exatamente como está no videos.tsv.
- **Trecho** fica entre aspas retas `"..."` e é cópia LITERAL de um pedaço contínuo do transcript.txt desse id: de 6 a 30 palavras, sem editar nem juntar pedaços.
- Um script confere cada trecho. Se algum não estiver no transcript, o vídeo é descartado.

### 2. `{ED}/roteiro.json`
Mesmo formato da edição de referência:
- `marca`: "INEMA · RADAR SAÚDE".
- `selo`: período, por exemplo "YOUTUBE · 09/10" ou "YOUTUBE · 03 A 08/10".
- `avatar`: `{"img": "img/avatar-teste.jpg", "tag": "<b>NEI MALDANER</b> · INEMA"}`.
- `hero` é o quadro 0. Leva:
  - a data `{DATA_BR}` com o dia da semana;
  - o tema;
  - o número mais forte, em `t2`;
  - uma linha `t3`;
  - um `t4` curto;
  - os rostos (miniaturas `img/<id>.jpg` dos vídeos citados).

Regras das `falas`:
- **Abertura (f1):** a frase-choque com o número mais forte. Nunca abrir com "Neste vídeo", "Imagine" ou "Olá".
- **Uma ideia por fala.** Cada influenciador citado ganha `ficha` (nome, canal com "dd/mm · N mil views", `rk` do canais.json, foto `img/<id>.jpg`) e `fundo` `img/<id>.jpg`.
- **Números:**
  - Usar `numero` (contador grande), `grafico` (só se houver série real dita no vídeo), `caixa` com citação literal ou itens, e `carimbo` ("POLÊMICA", "ALERTA", "SEM CONSENSO", "ESTUDO") quando couber.
  - Todo número mostrado está no base.md.
- **`fonte`:** "<b>Fonte:</b> Canal, YouTube, dd/mm/aaaa · “título curto”".
- **Texto falado (`fala`), no tom do Nei:**
  - Tratar por "tu", frases curtas.
  - Escrever TODOS os números e anos por extenso, sem algarismo: "sete vírgula sete por cento", "dois mil e vinte e oito".
  - Siglas lidas como se fala ("ésse ú ésse" para SUS, "ó ême ésse" para OMS). Sem emoji.
- **`em` (âncora):** uma palavra comum que está na fala, nunca um número.
- **Penúltima fala:** gancho de comentário. É uma pergunta sobre o tema ("E tu? ... Comenta aqui"), com `"limpa": true`. A `fonte` dela é "<b>Não substitui consulta médica.</b> Resumo do que os influenciadores disseram, com a fonte de cada fato".
- **Última fala:** CTA com `fundo` "img/cta.jpg" e `"limpa": true`.
  - Fala: uma ponte curta do tema para a IA, mais "Te prepara pra gestão de agentes de IA: curso gratuito no inema ponto club."
  - `hero` igual ao da referência (GESTÃO DE / AGENTES DE IA / img/cta.jpg).
  - `caixa` tipo cta com "INEMA.CLUB".
- **Saúde (regras duras):**
  - Relatar e atribuir sempre ("segundo ele", "ela recomenda"). Nunca vira conselho do Nei.
  - Nada de dose, remédio, suplemento, jejum ou dieta como instrução para quem assiste. Quando citar, fechar com "fala com teu médico antes".
  - Promessa de cura, tratamento sem consenso científico, discurso antivacina ou contra tratamento estabelecido NÃO vira manchete. Se entrar, vem com `carimbo` "SEM CONSENSO" e a fala diz que isso não tem consenso na medicina. Na dúvida, fica de fora.
  - Polêmica é o que ELES disseram. Política: atribuída, sem lado, sem opinião do Nei.

### 3. `{ED}/legenda.txt`
Até 6 linhas para o Nei aprovar no Telegram:
- linha 1: título sugerido para o YouTube, até 70 caracteres, com gancho;
- linhas 2 a 4: os números principais com quem disse;
- linha 5: "Não substitui consulta médica."

### 4. `{ED}/sugestao.txt` (opcional)
Se, nos títulos ou transcrições, outro influenciador de saúde CONSOLIDADO e confiável aparecer em destaque, escreva uma linha com nome, canal e motivo. Consolidado quer dizer profissional de saúde com registro (CRM, CRN, CRP), anos de canal, grande audiência; nunca emergente nem quem vende cura milagrosa. É só sugestão: não inclua essa pessoa no vídeo.

### Sem pauta
Se não houver nada relevante (nenhum número ou fato forte, só repetição ou conteúdo publicitário), grave apenas `{ED}/SEM_PAUTA.txt` com uma linha explicando o motivo. Melhor não publicar do que publicar morno.
