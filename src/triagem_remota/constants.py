"""Listas fechadas e textos de encaminhamento (PoC)."""

SINTOMAS_VALIDOS = frozenset(
    {
        "dor_toracica",
        "falta_ar",
        "febre",
        "confusao_mental",
        "tontura",
        "dor_cabeca",
        "tosse",
        "nausea",
        "dor_abdominal",
        "sangramento",
        "convulsao",
        "palpitacoes",
        "fraqueza",
        "dor_articular_leve",
        "coriza",
    }
)

COMORBIDADES_VALIDAS = frozenset(
    {
        "diabetes",
        "hipertensao",
        "cardiopatia",
        "imunossupressao",
        "asma",
        "nenhuma",
    }
)

ENCAMINHAMENTOS = {
    "emergencia": (
        "Procure imediatamente um pronto-socorro ou ligue para o serviço de emergência "
        "da sua região. Esta PoC não substitui avaliação médica."
    ),
    "urgente": (
        "Procure atendimento presencial ou teleconsulta nas próximas 24 horas. "
        "Acompanhe o agravamento dos sintomas."
    ),
    "rotina": (
        "Agende consulta ambulatorial em alguns dias. Mantenha hidratação e repouso "
        "conforme orientação geral, sem autodiagnóstico."
    ),
    "autocuidado": (
        "Sintomas compatíveis com quadro leve. Monitore em casa, medidas de conforto "
        "e retorne se houver piora."
    ),
}