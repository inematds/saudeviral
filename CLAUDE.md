# CLAUDE.md — saudeviral

Conta/autor: `inematds <inematds@gmail.com>`, repo `inematds/saudeviral`. Fluxo e agenda: README.md. Base de cada edição: `edicoes/<ed>/base.md`. Projeto irmão (mesmo motor): `~/projetos/finviral`.

- Criado em 10/10/2026 a pedido do Nei: "vamos fazer algo igual o finviral … pode publicar no lives12 e no bot v3, e publique no portal". Sai SEMPRE com o avatar HeyGen, é PUBLICADO no YouTube **Inema Pro (lives12)** por `auto/publicar.sh` (yt-pubx) e vai SEMPRE ao bot v3 com o link. A versão com foto (quando o avatar falha) só vai ao bot.
- Agenda (systemd usuário, `systemd/`): diário seg–sex 05:00, semanal sáb 05:00, domingo dom 05:00 → `auto/rodar.sh <modo>`. O horário é 05:00 para não disputar GPU/Whisper e o perfil do HeyGen com o finviral (02:00). Avulso: `auto/rodar.sh <modo> <data>`.
- Influenciadores em `canais.json` (só YouTube; base em `pesquisa/influenciadores.md`). O Nei inclui/exclui. Augusto Cury fica FORA (político, decisão do Nei em 10/10/2026). Eu posso SUGERIR (no bot) nome consolidado, com registro profissional (CRM/CRN/CRP) e confiável — nunca emergente; só entra com ok dele.
- Coleta só por yt-dlp (metadados) + inemavox (áudio e Whisper local). Roteiro por `claude -p` (assinatura). Sem API paga. A Apify foi usada só na pesquisa inicial, com autorização do Nei; não entra na rotina.
- Avatar: HeyGen pelo ESTÚDIO (assinatura, `motor/avatar_heygen.sh`, trava compartilhada `~/.cache/inemaccbot/heygen-estudio.lock`). Títulos `SAUDEVIRAL-…` (o finviral usa `FINVIRAL-…`). Oferta de troca de plano do HeyGen: SEMPRE recusar.
- Sábado e domingo: além do curto 9:16, o LONGO 16:9 "A semana explicada" (`auto/roteiro-longo.md` → `auto/checar.py --longo` → `auto/longo.sh`).
- Regras de saúde (no roteiro e no `checar.py`): todo fato/número tem trecho literal no base.md; tudo relatado e atribuído; nada de dose/remédio/dieta como instrução; tratamento sem consenso leva carimbo "SEM CONSENSO" ou fica fora; política atribuída, sem lado; "Não substitui consulta médica." obrigatório.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- Tratar por "você" (nunca "tu/teu/ti/te prepara") e CTA SEMPRE só o inema.club — nada de "segue o canal", vídeo longo ou canal do YouTube; o portão (checar.py / rodar.sh) reprova. (Nei, 11/10/2026)
- Motor do curto: f1 com hero não leva numero/ficha/caixa (ficava número sobre número); o numero entra no início da fala e fica até o próximo visual (senão a parte de cima fica vazia); legenda cola número partido pelo Whisper ("7 ,7 %" → "7,7%"). (11/10/2026)
- Narração e pergunta tratam por "você", nunca "tu"/"teu"/"te prepara" (pedido do Nei, 10/10/2026). A edição de referência foi convertida também, porque o modelo copia o tom dela.
- Miniatura do fundo aparece INTEIRA (16:9, sem zoom) no meio da tela escura, sem preenchimento desfocado: o Nei reprovou o zoom de cover em 9:16 e depois o desfocado ("parece que quer esconder algo"). (10/10/2026)
- Curto não é lista: no máximo 3 assuntos, cada um com contexto, o que ele disse e o que muda pra quem assiste; termo técnico explicado na fala (o Nei reprovou o semanal de 10/10 por "assunto muito mal explicado"). (10/10/2026)
- Título do hero mede depois de carregar a fonte (document.fonts.load). (10/10/2026)
- (Herdadas do finviral, mesmo motor.) Cadeia longa (HeyGen + render + publicação) disparada à mão vai por `systemd-run --user --unit …`, nunca como background da sessão. O `avatar_heygen.sh` retoma sem reenviar.
- Legenda palavra a palavra: bloco por TAMANHO (≤18 letras); palavra da legenda vem do roteiro (o Whisper erra nome próprio).
- No palco.html, função global não pode se chamar `render` (usar `desenhar`).
- Âncora `"em"` casa com o Whisper, que escreve números em algarismos: ancorar em palavra comum.
- O conferidor de voz reprova "dois e meio por cento": escrever "dois vírgula cinco".
- Citação no quadro e no base.md = literal do transcript; o `auto/checar.py` reprova paráfrase.
- Não editar `auto/rodar.sh` (ou qualquer .sh) enquanto uma rodada está em execução: editar cópia e trocar com `mv`.
- A voz do HeyGen chega ~-26 dB: mixar SEMPRE com loudnorm -14 LUFS e medir antes de enviar.
