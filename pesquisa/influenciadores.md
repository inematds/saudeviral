# Influenciadores de saúde do Brasil — pesquisa de 10/10/2026

Base da lista do saudeviral (`canais.json`). Augusto Cury saiu por decisão do Nei (político).
Dados brutos em `pesquisa/2026-10-10/` (`ig_profiles*.json`, `ig_search.json`: Apify; `youtube-freq/`: yt-dlp).

## Como foi medido

- **Quem é grande:** Prêmio iBest 2024, categoria Influenciadores de Saúde (algoritmo + voto popular + júri); blog BIP sobre médico influenciador; estudo UFES (médicos no Instagram, 2019–2020); busca de perfis no Instagram por especialidade (Apify `instagram-search-scraper`).
- **Frequência no YouTube:** yt-dlp, data exata dos últimos 15 vídeos, shorts e lives de cada canal (10/10/2026).
- **Frequência no Instagram:** Apify `instagram-profile-scraper`, últimos ~12 posts sem os fixados. Stories não entram.
- **Custo Apify:** US$ 0,79 do crédito mensal de US$ 5 (ciclo 18/09–17/10).

## Top 10 inicial (YouTube + Instagram)

| Nome | Área | YouTube (inscritos) | YT: frequência | Instagram | IG: frequência |
|---|---|---|---|---|---|
| Ana Beatriz Barbosa (PodPeople) | Psiquiatra, saúde mental | 4,8 mi | ~2 vídeos/dia + ~2 shorts/dia | @anabeatriz11 · 7,2 mi | ~1,3/dia |
| Patricia Leite | Nutricionista | 8,3 mi | ~2 vídeos/dia | @nutricionistapatricialeite · 1,1 mi | ~3,5/sem |
| Drauzio Varella | Oncologista, saúde pública | 4,2 mi | ~6 vídeos/sem + ~8 shorts/sem | @sitedrauziovarella · 1,9 mi | ~1,3/dia |
| Fernando Lemos (Planeta Intestino) | Médico, intestino | 7,3 mi | ~1 vídeo/sem + ~2 shorts/dia | @dr.fernando_lemos · 2,9 mi | ~3/dia |
| Paulo Muzy | Médico do esporte | 1,4 mi | ~2 vídeos/sem, ~9 shorts/sem, ~3 lives/sem | @paulomuzy · 7,6 mi | ~1,3/dia |
| Christian Aguiar (Contra a Corrente) | Médico, metabolismo | 900 mil | ~2 vídeos/sem + ~4–5 shorts/sem | @dr.christianaguiar · 930 mil | ~5/sem |
| Mohamad Barakat (Instituto) | Medicina integrativa | 970 mil | ~2 vídeos/mês + ~4–5 shorts/sem | @institutodrbarakat · 440 mil | ~1,5/dia |
| Ana Escobar | Pediatra | 290 mil | ~1 vídeo/sem + ~3–4 shorts/sem | @draanaescobar · 1,5 mi | ~1/dia |
| Lair Ribeiro (Academy) | Cardiologista, nutrólogo | 1,5 mi | ~1 vídeo/sem | @drlairribeiro · 3,7 mi | ~4,5/sem |
| Juliano Pimentel | Médico, "medicina natural" | 1,9 mi | parado desde jul/2022 | @drjulianopimentel · 950 mil | ~2–3/dia |

## Grandes nas duas redes que entraram depois

| Nome | Área | Instagram | YouTube |
|---|---|---|---|
| Dayan Siebra | Cirurgião vascular, saúde geral | 4,9 mi (~3/dia) | 7,9 mi |
| Rossandro Klinjey | Psicólogo, família | 2,7 mi (~1/dia) | 1,1 mi |
| Victor Sorrentino | Médico, longevidade | 1,6 mi (~1,4/dia) | 376 mil |
| Marcio Atalla | Educador físico, movimento | 1,2 mi (~1,3/dia) | 476 mil |

## Fortes no Instagram, fracos no YouTube (fora da coleta: o saudeviral lê só YouTube)

| Nome (@) | Área | Instagram | YouTube | IG: frequência |
|---|---|---|---|---|
| Daniel Becker (@pediatriaintegralbr) | Pediatra, infância | 2,2 mi | 59 mil | ~4/sem |
| Flávia Cyfer (@flaviacyfer) | Nutricionista 40+, menopausa | 2,1 mi | 32 mil | ~2–3/dia |
| Thiago Castro (@dr.thiagocastro) | Pediatra, autismo | 1,9 mi | 241 mil | ~5/dia |
| Daniel Cady (@danielcady) | Nutricionista | 2,9 mi | 372 mil | ~1/dia |
| Isa Latuf Jardim (@isalatufjardim) | Emagrecimento (formação não confirmada) | 1,5 mi | 115 mil | ~4/sem |
| Leiliane Rocha (@leilianerochapsicologa) | Psicóloga, educação emocional | 1,4 mi | 121 mil | ~2/dia |
| Luiz Eduardo Xavier (@dreduxavierpsiquiatra) | Psiquiatra | 1,1 mi | 7 mil | ~2/dia |
| Moniele Cunha (@monielecunha) | Nutricionista, fertilidade | 730 mil | 87 mil | ~5/dia |
| Marília Cardoso (@mariliacardosoa) | Endocrinologista | 520 mil | 9 mil | ~2/dia |

## Ressalvas

- Lair Ribeiro, Barakat, Christian Aguiar, Victor Sorrentino e Juliano Pimentel são criticados pela comunidade científica por defender tratamentos sem consenso. O roteiro do saudeviral relata, atribui e carimba "SEM CONSENSO".
- O CFM vem apertando a fiscalização de médicos influenciadores (Resolução CFM nº 1.974/2011).
- O perfil pessoal de Mohamad Barakat (~1,6 mi) não foi encontrado; foi medido o do Instituto.

## Fontes

- [Prêmio iBest — Influenciadores de Saúde (Medicina S/A)](https://medicinasa.com.br/?p=127787)
- [BIP — Médico influenciador](https://www.usebip.com/blogs/bip-insights/medico-influenciador-por-que-o-mercado-bilionario-cresce-no-mundo-e-o-brasil-ainda-hesita)
- [Estudo UFES — médicos no Instagram](https://periodicos.ufes.br/poscomufes/article/view/32350/21476)
- [HypeAuditor — Top Saúde e Medicina Instagram Brasil](https://hypeauditor.com/pt/top-instagram-health-medicine-brazil/)
- [Heepsy — YouTube Fitness Brasil](https://www.heepsy.com/en/find-influencers/youtube/fitness/brazil)
