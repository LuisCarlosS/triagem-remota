# Triagem Remota de Sintomas — PoC (Saúde Digital)

Prova de conceito **educacional** de triagem remota com motor de regras transparente, API REST,
CLI, dados **100% sintéticos** e experimento reproduzível.

> **Aviso:** esta solução **não** deve ser usada para decisão clínica real. Não há evidência de
> segurança, eficácia ou prontidão para produção.

## Tecnologias

- Python 3.11+
- Pydantic v2, FastAPI, Uvicorn
- pytest, httpx (testes de API)
- scikit-learn (métricas opcionais no experimento)

## Estrutura do projeto

```
triagem-remota/
├── README.md
├── pyproject.toml
├── requirements.txt
├── docs/
│   ├── TECNICO.md
│   └── DADOS_SINTETICOS.md
├── data/synthetic/
│   ├── cases.json
│   ├── gold_fixed.json
│   ├── intake_schema.json
│   └── README_DATA.md
├── src/triagem_remota/
│   ├── api.py
│   ├── constants.py
│   ├── engine.py
│   ├── models.py
│   ├── rules.py
│   └── validators.py
├── scripts/
│   ├── prepare_data.py
│   ├── run_poc.py
│   ├── run_experiment.py
│   └── _labeler.py
└── tests/
```

## Pré-requisitos

- Python 3.11 ou superior instalado (no Windows, use `py -3` ou o caminho completo do instalador).
- Git opcional.

## Instalação e execução

```powershell
cd caminho\para\triagem-remota
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,experiments]"
python scripts\prepare_data.py
python scripts\run_poc.py --case-id SYN-001
python scripts\run_poc.py --all
python scripts\run_experiment.py
pytest -v
uvicorn triagem_remota.api:app --app-dir src --host 127.0.0.1 --port 8000
```

Documentação interativa da API: `http://127.0.0.1:8000/docs`

### Exemplo de requisição `POST /triagem`

```json
{
  "case_id": "API-DEMO",
  "idade_anos": 45,
  "sintomas": ["dor_toracica", "falta_ar"],
  "sinais_vitais": {
    "frequencia_cardiaca_bpm": 112,
    "pressao_sistolica_mmhg": 135,
    "temperatura_celsius": 36.9,
    "saturacao_o2_percent": 93
  },
  "duracao_horas": 1,
  "comorbidades_simuladas": ["hipertensao"]
}
```

Resposta inclui `nivel_urgencia`, `encaminhamento`, `processing_steps` e `regras_disparadas`.

## O que foi implementado

- Validação de entradas e listas fechadas de sintomas/comorbidades.
- Motor de regras com red flags, urgência e pontuação.
- Registro de etapas em cada triagem (`processing_steps`).
- Scripts para gerar dados, executar a PoC e rodar experimento.
- Testes automatizados (validadores, regras, engine, API).
- Documentação técnica em `docs/`.

## Resultados verificados neste ambiente

Execução em **24/11/2026** (Python **3.12.10**, Windows):

| Verificação | Resultado |
|-------------|-----------|
| `pytest -v` | **12 passed** |
| `run_experiment.py` | **70** casos, acurácia **100%**, **0** falhas |
| `run_poc.py --case-id SYN-001` | `emergencia` (regra `RF_DOR_TORACICA_DISPNEIA_TAQUICARDIA`) |

Artefatos gerados localmente: `outputs/experiment_report.json`, `outputs/confusion_matrix.txt`,
`outputs/triagem_SYN-001.json` (pasta `outputs/` no `.gitignore` — regenere com os scripts).

## Transparência

- Dados: apenas sintéticos; ver `data/synthetic/README_DATA.md`.
- Referências acadêmicas sobre triagem (Manchester, telessaúde): **não validadas** nesta entrega.
- Python não estava instalado inicialmente neste ambiente; foi instalado via `winget` para permitir
  a verificação acima. Em outra máquina, use um Python 3.11+ já existente.

## Documentação adicional

- [docs/TECNICO.md](docs/TECNICO.md) — arquitetura, regras, limitações.
- [docs/DADOS_SINTETICOS.md](docs/DADOS_SINTETICOS.md) — geração e seed.

## Manutenibilidade

O núcleo de regras está isolado em `rules.py` para facilitar evolução (ex.: substituição por modelo
ML mantendo a API). Se o arquivo crescer, dividir em módulos de emergência e pontuação. O rotulador
em `scripts/_labeler.py` deve permanecer alinhado manualmente à especificação ao alterar regras.

Possível próximo passo: testes baseados em propriedades (Hypothesis) para casos-limite adicionais.