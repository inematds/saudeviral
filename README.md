# saudeviral

[![saudeviral — Radar Saúde](guia/assets/banner.jpg)](https://inematds.github.io/saudeviral/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O saudeviral é um sistema que faz, sozinho, vídeos curtos (9:16) sobre o que os maiores influenciadores de saúde do Brasil disseram nos vídeos deles: médicos, nutricionistas e psicólogos com maior audiência. Ele assiste aos vídeos do YouTube por transcrição, separa os fatos, os números e as polêmicas, e monta um vídeo com números grandes animados, a fonte de cada dado na tela e o Nei comentando (avatar). Tudo é relatado e atribuído, e o que não tem consenso na medicina sai com o carimbo "SEM CONSENSO". Não substitui consulta médica. Roda num computador com GPU, com a assinatura do Claude Code e do HeyGen. É o irmão do [finviral](https://github.com/inematds/finviral) (mesmo motor, outro tema).

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/saudeviral/guia/**

## Como funciona

1. **Coleta:** lista os vídeos dos canais de `canais.json` (só metadados, yt-dlp), baixa o áudio e transcreve localmente (inemavox, Whisper large-v3).
2. **Roteiro:** o `claude -p` (assinatura, sem API) lê as transcrições e grava três arquivos:
   - `base.md`: cada fato ou número, quem disse, o vídeo e o trecho literal;
   - `roteiro.json`: falas e visuais;
   - `legenda.txt`: o texto para aprovação.
3. **Conferência (`auto/checar.py`):** confere se cada trecho do `base.md` está de fato na transcrição. Também confere se os números da fala estão por extenso, se as imagens existem, se o CTA está presente e se aparece "Não substitui consulta médica". Se reprovar, o roteiro volta uma vez para correção. Se reprovar de novo, o vídeo não é feito.
4. **Avatar:** o HeyGen gera o avatar do Nei pelo estúdio (assinatura, sem API de geração). Se falhar, sai a versão com a foto e a voz do Nei (Chatterbox).
5. **Vídeo:** o `motor/palco.html` é renderizado quadro a quadro pelo Playwright, com contadores, carimbo, legenda palavra a palavra e fonte em toda cena. O avatar fica no canto.
6. **Publicação:** o vídeo é publicado no YouTube **Inema Pro (lives12)** pelo `yt-pubx` (`auto/publicar.sh`) e vai sempre ao bot v3 no Telegram, com o link. Se o avatar falhar, a versão com foto só vai ao bot.
7. **Sábado e domingo — o longo 16:9:** depois do curto, sai "A semana explicada" (5 a 7 min, um capítulo por influenciador), com as cenas animadas do explicavideo v2 (`motor/longo.html`, `auto/roteiro-longo.md`, `auto/checar.py --longo`, `auto/longo.sh`).

## Agenda (systemd, usuário)

| Quando | Rodada | O que sai |
|---|---|---|
| Segunda a sexta, 05:00 | `diario` | 40–60 s com o que eles publicaram ontem e anteontem |
| Sábado, 05:00 | `semanal` | 90 s a 2 min: balanço da semana + longo 16:9 "A semana explicada" |
| Domingo, 05:00 | `domingo` | ~90 s: os alertas, hábitos e mitos da semana + longo 16:9 |

O horário é 05:00 para não disputar a GPU e o HeyGen com o finviral, que roda às 02:00. O bot v3 sempre recebe uma de três coisas: o vídeo (com o link do lives12), "sem pauta" ou "falhou em X".

```bash
cp systemd/saudeviral-* ~/.config/systemd/user/ && systemctl --user daemon-reload
systemctl --user enable --now saudeviral-diario.timer saudeviral-semanal.timer saudeviral-domingo.timer
systemctl --user list-timers 'saudeviral-*'
```

## Avulso (fora da agenda)

```bash
auto/rodar.sh diario 2026-10-09                # rodada de um dia específico
SEM_AVATAR=1 SEM_BOT=1 auto/rodar.sh semanal   # teste: sem HeyGen e sem enviar
echo "2026-10-17 diario" >> auto/pular.txt     # pular uma rodada
```

## Influenciadores

A lista fica em `canais.json`, com `"ativo": false` para pausar. A base é a pesquisa de 10/10/2026 (`pesquisa/influenciadores.md`): Drauzio Varella, Dayan Siebra, Fernando Lemos, Ana Beatriz Barbosa (PodPeople), Patricia Leite, Paulo Muzy, Rossandro Klinjey, Marcio Atalla, Ana Escobar, Lair Ribeiro, Instituto Dr. Barakat, Christian Aguiar e Victor Sorrentino. A coleta lê só o YouTube; quem é forte só no Instagram está listado na pesquisa.

Se aparecer em destaque outro profissional de saúde consolidado, com registro e confiável, o sistema sugere a inclusão na mensagem do bot. Nome emergente nunca entra, e a inclusão só acontece com o ok do Nei.

## Regras de cada vídeo

- Quadro 0 cheio: data dd/mm/aaaa e o fato mais forte.
- Só entra fato ou número que está na transcrição, com a fonte (canal, data, título) na tela.
- Tudo relatado e atribuído ("segundo ele"). Nada de dose, remédio ou dieta como instrução.
- Tratamento sem consenso científico leva o carimbo "SEM CONSENSO" ou fica de fora.
- Política: atribuída, sem tomar lado.
- "Não substitui consulta médica." em todo vídeo.
- Fala no tom do Nei ("tu"), com números e anos por extenso. Fim: gancho de comentário e CTA de gestão de agentes de IA no inema.club.

## Requisitos

- yt-dlp
- inemavox (`~/projetos/inemavox`)
- cardshorts (voz Chatterbox `nei`)
- Node com Playwright (`motor/node_modules` → link para o do eventosextremospub)
- ffmpeg
- `claude` (Claude Code logado na assinatura)
- Xvfb `:99` e o perfil do HeyGen do explicavideos
- bot v3 (`refazvideo/ferramentas/enviar_bot_v3.mjs`)

Licença MIT. O conteúdo citado pertence aos canais de origem, sempre creditados na tela.
