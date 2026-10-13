# saudeviral

[![saudeviral — Health Radar](guia/assets/banner-en.jpg)](https://inematds.github.io/saudeviral/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

saudeviral is a system that, on its own, makes short videos (9:16) about what Brazil's biggest health influencers said in their videos: the doctors, nutritionists and psychologists with the largest audiences. It watches the YouTube videos through transcription, picks out the facts, numbers and controversies, and builds a video with big animated numbers, the source of every data point on screen and Nei commenting (avatar). Everything is reported and attributed, and anything without medical consensus gets a "NO CONSENSUS" stamp. It does not replace a medical consultation. It runs on a computer with a GPU, using the Claude Code and HeyGen subscriptions. It is the sibling of [finviral](https://github.com/inematds/finviral) (same engine, different topic).

## 📖 User guide

Full guide (landing + step by step): **https://inematds.github.io/saudeviral/guia/en/**

## How it works

1. **Collection:** lists the videos of the channels in `canais.json` (metadata only, yt-dlp), downloads the audio and transcribes it locally (inemavox, Whisper large-v3).
2. **Script:** `claude -p` (subscription, no API) reads the transcripts and writes three files:
   - `base.md`: each fact or number, who said it, the video and the literal excerpt;
   - `roteiro.json`: lines and visuals;
   - `legenda.txt`: the text for approval.
3. **Fact-check (`auto/checar.py`):** checks that every excerpt in `base.md` really is in the transcript, that spoken numbers are written out, that images exist, that the CTA is there and that "Não substitui consulta médica" (does not replace a medical consultation) appears. If it fails, the script goes back once for correction. If it fails again, the video is not made.
4. **Avatar:** HeyGen generates Nei's avatar through the studio (subscription, no generation API). If it fails, a version with Nei's photo and voice (Chatterbox) is made.
5. **Video:** `motor/palco.html` is rendered frame by frame by Playwright, with counters, stamps, word-by-word captions and the source in every scene. The avatar sits in the corner.
6. **Publishing:** the video is published on the **Inema Pro (lives12)** YouTube channel through `yt-pubx` (`auto/publicar.sh`) and always goes to bot v3 on Telegram with the link. If the avatar failed, the photo version only goes to the bot.
7. **Saturday and Sunday — the long 16:9:** after the short, "The week explained" comes out (5 to 7 min, one chapter per influencer), with the explicavideo v2 animated scenes (`motor/longo.html`, `auto/roteiro-longo.md`, `auto/checar.py --longo`, `auto/longo.sh`).

## Schedule (systemd, user)

| When | Run | Output |
|---|---|---|
| Monday to Friday, 05:00 | `diario` | 40–60 s with what they published yesterday and the day before |
| Saturday, 05:00 | `semanal` | 90 s to 2 min: the week in review + long 16:9 "The week explained" |
| Sunday, 05:00 | `domingo` | ~90 s: the week's warnings, habits and myths + long 16:9 |

The time is 05:00 so it doesn't compete for the GPU and HeyGen with finviral, which runs at 02:00. Bot v3 always receives one of three things: the video (with the lives12 link), "no topic" or "failed at X".

```bash
cp systemd/saudeviral-* ~/.config/systemd/user/ && systemctl --user daemon-reload
systemctl --user enable --now saudeviral-diario.timer saudeviral-semanal.timer saudeviral-domingo.timer
systemctl --user list-timers 'saudeviral-*'
```

## Ad hoc (outside the schedule)

```bash
auto/rodar.sh diario 2026-10-09                # run for a specific day
SEM_AVATAR=1 SEM_BOT=1 auto/rodar.sh semanal   # test: no HeyGen, nothing sent
echo "2026-10-17 diario" >> auto/pular.txt     # skip a run
```

## Influencers

The list lives in `canais.json`, with `"ativo": false` to pause. It is based on the 10/10/2026 research (`pesquisa/influenciadores.md`): Drauzio Varella, Dayan Siebra, Fernando Lemos, Ana Beatriz Barbosa (PodPeople), Patricia Leite, Paulo Muzy, Rossandro Klinjey, Marcio Atalla, Ana Escobar, Lair Ribeiro, Instituto Dr. Barakat, Christian Aguiar and Victor Sorrentino; on 10/13/2026 Juliano Teles, Moacir Rosa, Leiliane Rocha, Daniel Cady and Thiago Castro joined. Collection reads YouTube only; those who are strong only on Instagram are listed in the research.

If another established, licensed and trustworthy health professional stands out, the system suggests adding them in the bot message. Emerging names never join, and inclusion only happens with Nei's ok.

## Rules for every video

- Full frame 0: date dd/mm/yyyy and the strongest fact.
- Only facts or numbers that are in the transcript, with the source (channel, date, title) on screen.
- Everything reported and attributed ("according to him"). No dose, medicine or diet as an instruction.
- Treatments without scientific consensus get the "NO CONSENSUS" stamp or are left out.
- Politics: attributed, no sides taken.
- "Does not replace a medical consultation" in every video.
- Spoken in Nei's tone ("você", formal "you"), with numbers and years written out. Ending: comment hook and the AI agent management CTA at inema.club.

## Requirements

- yt-dlp
- inemavox (`~/projetos/inemavox`)
- cardshorts (Chatterbox voice `nei`)
- Node with Playwright (`motor/node_modules` → link to eventosextremospub's)
- ffmpeg
- `claude` (Claude Code logged in on the subscription)
- Xvfb `:99` and the explicavideos HeyGen profile
- bot v3 (`refazvideo/ferramentas/enviar_bot_v3.mjs`)

MIT license. Quoted content belongs to the original channels, always credited on screen.
