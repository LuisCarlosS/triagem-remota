# Documentação técnica — Triagem Remota de Sintomas (PoC)

## Enquadramento

Área: **Tecnologia Assistiva e Saúde Digital** — foco em **triagem remota** a partir de questionário
estruturado e sinais vitais **sintéticos**. A saída inclui linguagem simples (`resumo_plain_language`) para
leitura humana ou integração posterior a leitores de tela — sem alegar certificação WCAG nesta PoC.

## Hipótese testável

Em dados sintéticos com `rotulo_ouro`, o motor de regras em `triagem_remota.rules` reproduz a
especificação espelhada em `scripts/_labeler.py`, permitindo medir **conformidade de implementação**
(acurácia, F1 por classe), não desempenho clínico.

## Fluxo de processamento

1. Validação Pydantic (`IntakeCase`).
2. Avaliação de red flags de emergência (ordem fixa).
3. Critérios de urgência.
4. Pontuação heurística por sintomas e sinais vitais.
5. Montagem de `TriageResult` com `processing_steps` e `regras_disparadas`.

## Regras (resumo)

| Código | Efeito |
|--------|--------|
| RF_CONVULSAO | emergência |
| RF_DOR_TORACICA_DISPNEIA_TAQUICARDIA | emergência |
| RF_HIPOTENSAO (PAS < 90) | emergência |
| RF_HIPOxia_SEVERA (SpO2 < 88) | emergência |
| RF_CONFUSAO_FEBRE_ALTA | emergência |
| RF_SANGRAMENTO_HYPOTENSION | emergência |
| RU_* | urgência (SpO2 limítrofe, febre ≥ 39 °C, etc.) |
| SC_* | classes por pontuação ≥ 55 / 35 / 15 |

Limiares de pontuação: ver `SINTOMA_PONTOS` em `src/triagem_remota/rules.py`.

## Limitações e avisos

- **Não** é dispositivo médico, **não** substitui Manchester Triage System ou avaliação presencial.
- Referências a triagem clássica (ex.: Manchester) são **contexto bibliográfico** — não auditamos
  diretrizes oficiais nem estudos nesta entrega.
- `confianca_heuristica` é score interno da PoC, não probabilidade calibrada.

## Reprodutibilidade

- Seed `42` em `prepare_data.py`.
- Comandos documentados no [README.md](../README.md).
- Artefatos em `outputs/` (ignorados pelo git); regerar com `run_experiment.py`.

## Resultado do experimento (executado localmente)

- Data da execução verificada: ambiente Windows, Python 3.12.10.
- **70 casos**, acurácia **100%** vs `rotulo_ouro`, **0** discordâncias.
- Detalhes: `outputs/experiment_report.json` após rodar o script.