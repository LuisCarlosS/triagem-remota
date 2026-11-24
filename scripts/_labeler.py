"""
Rotulador de referência (espelho da especificação em docs/TECNICO.md).
Implementação separada do motor em triagem_remota.rules — mede conformidade da engine.
"""

from __future__ import annotations

from triagem_remota.models import IntakeCase, NivelUrgencia

SINTOMA_PONTOS: dict[str, float] = {
    "dor_toracica": 35,
    "falta_ar": 30,
    "febre": 12,
    "confusao_mental": 40,
    "convulsao": 45,
    "sangramento": 25,
    "palpitacoes": 18,
    "dor_cabeca": 8,
    "tontura": 10,
    "nausea": 6,
    "dor_abdominal": 10,
    "tosse": 4,
    "fraqueza": 8,
    "dor_articular_leve": 3,
    "coriza": 2,
}


def _comorbidade(case: IntakeCase, *nomes: str) -> bool:
    com = {c for c in case.comorbidades_simuladas if c != "nenhuma"}
    return any(n in com for n in nomes)


def reference_label(case: IntakeCase) -> NivelUrgencia:
    """Espelho manual da especificação; manter alinhado a docs/TECNICO.md."""
    sintomas = set(case.sintomas)
    sv = case.sinais_vitais

    if "convulsao" in sintomas:
        return NivelUrgencia.EMERGENCIA
    if (
        "dor_toracica" in sintomas
        and "falta_ar" in sintomas
        and sv.frequencia_cardiaca_bpm >= 100
    ):
        return NivelUrgencia.EMERGENCIA
    if sv.pressao_sistolica_mmhg < 90:
        return NivelUrgencia.EMERGENCIA
    if sv.saturacao_o2_percent is not None and sv.saturacao_o2_percent < 88:
        return NivelUrgencia.EMERGENCIA
    if "confusao_mental" in sintomas and sv.temperatura_celsius >= 38.5:
        return NivelUrgencia.EMERGENCIA
    if "sangramento" in sintomas and sv.pressao_sistolica_mmhg < 100:
        return NivelUrgencia.EMERGENCIA

    if "falta_ar" in sintomas and sv.saturacao_o2_percent is not None:
        if 88 <= sv.saturacao_o2_percent < 92:
            return NivelUrgencia.URGENTE
    if sv.temperatura_celsius >= 39.0 and "febre" in sintomas:
        return NivelUrgencia.URGENTE
    if "dor_toracica" in sintomas and _comorbidade(case, "cardiopatia", "diabetes"):
        return NivelUrgencia.URGENTE
    if case.idade_anos >= 65 and "fraqueza" in sintomas and case.duracao_horas <= 24:
        return NivelUrgencia.URGENTE

    pontos = sum(SINTOMA_PONTOS.get(s, 5) for s in sintomas)
    if sv.temperatura_celsius >= 37.8:
        pontos += 5
    if sv.frequencia_cardiaca_bpm > 110:
        pontos += 8
    if _comorbidade(case, "imunossupressao"):
        pontos += 10
    if case.duracao_horas > 72 and pontos < 15:
        pontos -= 5

    if pontos >= 55:
        return NivelUrgencia.EMERGENCIA
    if pontos >= 35:
        return NivelUrgencia.URGENTE
    if pontos >= 15:
        return NivelUrgencia.ROTINA
    return NivelUrgencia.AUTOCUIDADO