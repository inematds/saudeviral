## 17/11/2026 — Trava de cota

`auto/ia_motor.py` atualizado para o executor do r7ex 1.7.6: recusa estruturada de cota do Claude grava o horário de volta em `~/.local/state/enginebridge/state.sqlite` e as chamadas seguintes falham na hora, sem abrir o programa (`python3 auto/ia_motor.py cota ver|liberar`). Chamadas automáticas do Claude sem sessão no disco. Codex (motor atual dos roteiros) ainda sem trava automática. Sem reserva configurada: o motor continua o de cada etapa. Testes do roteiro e dois contratos novos passaram.

## 16/11/2026 — Citações do roteiro

Normaliza escapes literais de espaço no base.md retornado em JSON. Preserva números, texto do roteiro e a comparação estrita com a transcrição. Oito testes passaram, incluindo regressão de escapes.

## 15/11/2026 — IA independente por etapa

Roteiros curtos e longos configuráveis por modo: tipo, motor, modelo e esforço em auto/ia.yaml. Contrato texto/JSON com escrita local restrita e portão factual preservado; operação Codex assinatura, APIs desativadas. Seis contratos locais passaram e roteiro curto real passou no checar.py deste projeto, sem avatar/render/publicação.

