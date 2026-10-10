# FALHAS — saudeviral

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-10-10 | Semanal com 6 assuntos em fragmentos, termos sem explicação (lugol, Vigitel, protocolo do SUS): o Nei achou "muito mal explicado" | roteiro.md: explicar em 3 passos (contexto, o que ele disse, o que muda) e termo técnico explicado na fala; rodar.sh: no máximo 3 assuntos no curto | prompt |
| 2026-10-10 | Fundo = miniatura 16:9 cheia de letreiro ampliada em 9:16: letras gigantes cortadas ("RISCO", "ÓIDE") | palco.html: fundo com blur 38 px | prompt |
| 2026-10-10 | Título do hero estourou a largura ("EMAGRECEDO…"): fonte Google só baixa quando usada | palco.html: caber() reduz a fonte + document.fonts.load antes do 1º quadro | infra |
| 2026-10-10 | Avatar e longo sem HeyGen: "ProcessSingleton", lote de tradução de outra sessão abriu o perfil sem pegar a trava | avatar_heygen.sh: tenta de novo a cada 2 min, até 1 h | infra |
