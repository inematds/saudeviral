# FALHAS — saudeviral

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-10-11 | curto de domingo com legenda sobre as miniaturas, carimbo sobre o texto, "Segundo assunto"/"o assunto" na fala e na legenda; Nei mandou tirar do ar (2Wcm60z2Yvg removido) | portão VISUAL antes do YouTube + legenda com texto do roteiro — pendente | infra + prompt |
| 2026-10-11 | domingo LONGO não saiu: estúdio HeyGen "o menu do card não tem Editar como Novo" (menu ⋮ não abriu em 1,2 s; mesmo template ok antes e depois) | heygen-studio.mjs: 3 tentativas de abrir o menu; + retempo.py com interpolação (vindo do finviral) | infra |
| 2026-10-11 | (vindo do finviral) topo vazio até a âncora, legenda "15 %", "teu"/"te prepara" na fala e CTA para o vídeo longo do Inema Pro | mesmo patch do gerar_cena.py + checar.py reprova tu/CTA fora do inema.club + AVISO_LONGO vazio | prompt + infra |
| 2026-10-10 | Longo foi ao bot mas não ao YouTube: o codex de /usr/bin (0.116) não lê o config.toml gravado pelo codex novo (service_tier="default") | publicar.sh põe ~/.npm-global/bin no PATH | infra |
| 2026-10-10 | Semanal com 6 assuntos em fragmentos, termos sem explicação (lugol, Vigitel, protocolo do SUS): o Nei achou "muito mal explicado" | roteiro.md: explicar em 3 passos (contexto, o que ele disse, o que muda) e termo técnico explicado na fala; rodar.sh: no máximo 3 assuntos no curto | prompt |
| 2026-10-10 | Fundo = miniatura 16:9 cheia de letreiro ampliada em 9:16: letras gigantes cortadas ("RISCO", "ÓIDE") | palco.html: fundo com blur 38 px | prompt |
| 2026-10-10 | Título do hero estourou a largura ("EMAGRECEDO…"): fonte Google só baixa quando usada | palco.html: caber() reduz a fonte + document.fonts.load antes do 1º quadro | infra |
| 2026-10-10 | Avatar e longo sem HeyGen: "ProcessSingleton", lote de tradução de outra sessão abriu o perfil sem pegar a trava | avatar_heygen.sh: tenta de novo a cada 2 min, até 1 h | infra |
