# saudeviral

[![saudeviral — Radar Salud](guia/assets/banner-es.jpg)](https://inematds.github.io/saudeviral/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

saudeviral es un sistema que hace, solo, videos cortos (9:16) sobre lo que dijeron en sus videos los mayores influencers de salud de Brasil: los médicos, nutricionistas y psicólogos con mayor audiencia. Mira los videos de YouTube mediante transcripción, separa los hechos, los números y las polémicas, y arma un video con números grandes animados, la fuente de cada dato en pantalla y Nei comentando (avatar). Todo se relata y se atribuye, y lo que no tiene consenso en la medicina sale con el sello "SIN CONSENSO". No sustituye una consulta médica. Corre en una computadora con GPU, con las suscripciones de Claude Code y HeyGen. Es el hermano de [finviral](https://github.com/inematds/finviral) (el mismo motor, otro tema).

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/saudeviral/guia/es/**

## Cómo funciona

1. **Recolección:** lista los videos de los canales de `canais.json` (solo metadatos, yt-dlp), descarga el audio y lo transcribe localmente (inemavox, Whisper large-v3).
2. **Guion:** `claude -p` (suscripción, sin API) lee las transcripciones y graba tres archivos:
   - `base.md`: cada hecho o número, quién lo dijo, el video y el fragmento literal;
   - `roteiro.json`: falas y visuales;
   - `legenda.txt`: el texto para aprobación.
3. **Verificación (`auto/checar.py`):** verifica que cada fragmento de `base.md` esté realmente en la transcripción, que los números hablados estén escritos con letras, que las imágenes existan, que haya CTA y que aparezca "Não substitui consulta médica" (no sustituye una consulta médica). Si reprueba, el guion vuelve una vez para corrección. Si reprueba de nuevo, el video no se hace.
4. **Avatar:** HeyGen genera el avatar de Nei por el estudio (suscripción, sin API de generación). Si falla, sale la versión con la foto y la voz de Nei (Chatterbox).
5. **Video:** `motor/palco.html` se renderiza cuadro a cuadro con Playwright, con contadores, sellos, subtítulos palabra por palabra y la fuente en cada escena. El avatar queda en la esquina.
6. **Publicación:** el video se publica en el canal **Inema Pro (lives12)** de YouTube con `yt-pubx` (`auto/publicar.sh`) y siempre va al bot v3 en Telegram con el enlace. Si el avatar falló, la versión con foto solo va al bot.
7. **Sábado y domingo — el largo 16:9:** después del corto sale "La semana explicada" (5 a 7 min, un capítulo por influencer), con las escenas animadas de explicavideo v2 (`motor/longo.html`, `auto/roteiro-longo.md`, `auto/checar.py --longo`, `auto/longo.sh`).

## Agenda (systemd, usuario)

| Cuándo | Ronda | Qué sale |
|---|---|---|
| Lunes a viernes, 05:00 | `diario` | 40–60 s con lo que publicaron ayer y anteayer |
| Sábado, 05:00 | `semanal` | 90 s a 2 min: balance de la semana + largo 16:9 "La semana explicada" |
| Domingo, 05:00 | `domingo` | ~90 s: alertas, hábitos y mitos de la semana + largo 16:9 |

El horario es 05:00 para no disputar la GPU y HeyGen con finviral, que corre a las 02:00. El bot v3 siempre recibe una de tres cosas: el video (con el enlace de lives12), "sin tema" o "falló en X".

```bash
cp systemd/saudeviral-* ~/.config/systemd/user/ && systemctl --user daemon-reload
systemctl --user enable --now saudeviral-diario.timer saudeviral-semanal.timer saudeviral-domingo.timer
systemctl --user list-timers 'saudeviral-*'
```

## Suelto (fuera de la agenda)

```bash
auto/rodar.sh diario 2026-10-09                # ronda de un día específico
SEM_AVATAR=1 SEM_BOT=1 auto/rodar.sh semanal   # prueba: sin HeyGen y sin enviar
echo "2026-10-17 diario" >> auto/pular.txt     # saltar una ronda
```

## Influencers

La lista está en `canais.json`, con `"ativo": false` para pausar. La base es la investigación del 10/10/2026 (`pesquisa/influenciadores.md`): Drauzio Varella, Dayan Siebra, Fernando Lemos, Ana Beatriz Barbosa (PodPeople), Patricia Leite, Paulo Muzy, Rossandro Klinjey, Marcio Atalla, Ana Escobar, Lair Ribeiro, Instituto Dr. Barakat, Christian Aguiar y Victor Sorrentino. La recolección lee solo YouTube; quienes son fuertes solo en Instagram están en la investigación.

Si se destaca otro profesional de salud consolidado, con registro y confiable, el sistema sugiere incluirlo en el mensaje del bot. Un nombre emergente nunca entra, y la inclusión solo ocurre con el ok de Nei.

## Reglas de cada video

- Cuadro 0 lleno: fecha dd/mm/aaaa y el hecho más fuerte.
- Solo entra el hecho o número que está en la transcripción, con la fuente (canal, fecha, título) en pantalla.
- Todo relatado y atribuido ("según él"). Nada de dosis, medicamento o dieta como instrucción.
- Un tratamiento sin consenso científico lleva el sello "SIN CONSENSO" o queda fuera.
- Política: atribuida, sin tomar partido.
- "No sustituye una consulta médica" en todo video.
- Habla en el tono de Nei ("você", "usted"), con números y años escritos con letras. Cierre: gancho de comentario y CTA de gestión de agentes de IA en inema.club.

## Requisitos

- yt-dlp
- inemavox (`~/projetos/inemavox`)
- cardshorts (voz Chatterbox `nei`)
- Node con Playwright (`motor/node_modules` → enlace al de eventosextremospub)
- ffmpeg
- `claude` (Claude Code con la suscripción)
- Xvfb `:99` y el perfil de HeyGen de explicavideos
- bot v3 (`refazvideo/ferramentas/enviar_bot_v3.mjs`)

Licencia MIT. El contenido citado pertenece a los canales de origen, siempre acreditados en pantalla.
