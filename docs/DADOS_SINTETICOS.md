# Geração de dados sintéticos

## Seed e reprodutibilidade

O script [`scripts/prepare_data.py`](../scripts/prepare_data.py) usa `RNG_SEED = 42` e gera **63** casos
aleatórios além dos casos fixos em `gold_fixed.json`.

## Campos

- Sintomas amostrados de lista fechada (ver `src/triagem_remota/constants.py`).
- Sinais vitais dentro de faixas fisiológicas amplas (não clínicas).
- `rotulo_ouro` nos casos gerados: função `reference_label` em `scripts/_labeler.py`.
- Casos em `gold_fixed.json`: rótulo definido na especificação da PoC (inclui bordas).

## Privacidade

Nenhum identificador real de pessoa. IDs no formato `SYN-xxx` / `SYN-FIX-xxx`.