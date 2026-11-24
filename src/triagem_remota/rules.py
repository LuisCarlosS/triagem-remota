from __future__ import annotations

from dataclasses import dataclass

from triagem_remota.constants import ENCAMINHAMENTOS
from triagem_remota.models import IntakeCase, NivelUrgencia, ProcessingStep

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


@dataclass
class RuleOutcome:
    nivel: NivelUrgencia
    regras_disparadas: list[str]
    pontuacao: float
    steps: list[ProcessingStep]


def _has_comorbidade(case: IntakeCase, *nomes: str) -> bool:
    com = {c for c in case.comorbidades_simuladas if c != "nenhuma"}
    return any(n in com for n in nomes)


def _step(etapa: str, detalhe: str, **dados) -> ProcessingStep:
    return ProcessingStep(etapa=etapa, detalhe=detalhe, dados=dict(dados))


def avaliar_regras(case: IntakeCase) -> RuleOutcome:
    steps: list[ProcessingStep] = []
    fired: list[str] = []
    sintomas = set(case.sintomas)
    sv = case.sinais_vitais

    steps.append(
        _step("inicio", "Avaliação iniciada", case_id=case.case_id, sintomas=list(sintomas))
    )

    # --- Prioridade: emergência (red flags) ---
    if "convulsao" in sintomas:
        fired.append("RF_CONVULSAO")
        steps.append(_step("emergencia", "Convulsão ativa", regra="RF_CONVULSAO"))
        return RuleOutcome(NivelUrgencia.EMERGENCIA, fired, 100.0, steps)

    if (
        "dor_toracica" in sintomas
        and "falta_ar" in sintomas
        and sv.frequencia_cardiaca_bpm >= 100
    ):
        fired.append("RF_DOR_TORACICA_DISPNEIA_TAQUICARDIA")
        steps.append(
            _step(
                "emergencia",
                "Dor torácica com dispneia e taquicardia",
                regra="RF_DOR_TORACICA_DISPNEIA_TAQUICARDIA",
            )
        )
        return RuleOutcome(NivelUrgencia.EMERGENCIA, fired, 95.0, steps)

    if sv.pressao_sistolica_mmhg < 90:
        fired.append("RF_HIPOTENSAO")
        steps.append(
            _step(
                "emergencia",
                "Pressão sistólica crítica",
                pa=sv.pressao_sistolica_mmhg,
                regra="RF_HIPOTENSAO",
            )
        )
        return RuleOutcome(NivelUrgencia.EMERGENCIA, fired, 92.0, steps)

    if sv.saturacao_o2_percent is not None and sv.saturacao_o2_percent < 88:
        fired.append("RF_HIPOxia_SEVERA")
        steps.append(
            _step(
                "emergencia",
                "Saturação de oxigênio muito baixa",
                spo2=sv.saturacao_o2_percent,
                regra="RF_HIPOxia_SEVERA",
            )
        )
        return RuleOutcome(NivelUrgencia.EMERGENCIA, fired, 90.0, steps)

    if "confusao_mental" in sintomas and sv.temperatura_celsius >= 38.5:
        fired.append("RF_CONFUSAO_FEBRE_ALTA")
        steps.append(
            _step(
                "emergencia",
                "Confusão com febre elevada",
                regra="RF_CONFUSAO_FEBRE_ALTA",
            )
        )
        return RuleOutcome(NivelUrgencia.EMERGENCIA, fired, 88.0, steps)

    if "sangramento" in sintomas and sv.pressao_sistolica_mmhg < 100:
        fired.append("RF_SANGRAMENTO_HYPOTENSION")
        steps.append(
            _step("emergencia", "Sangramento com hipotensão", regra="RF_SANGRAMENTO_HYPOTENSION")
        )
        return RuleOutcome(NivelUrgencia.EMERGENCIA, fired, 91.0, steps)

    steps.append(_step("emergencia", "Nenhuma red flag de emergência", disparou=False))

    # --- Urgente ---
    urgente = False
    if "falta_ar" in sintomas and sv.saturacao_o2_percent is not None:
        if 88 <= sv.saturacao_o2_percent < 92:
            fired.append("RU_SPO2_LIMITE")
            urgente = True
            steps.append(_step("urgente", "SpO2 limítrofe", spo2=sv.saturacao_o2_percent))

    if sv.temperatura_celsius >= 39.0 and "febre" in sintomas:
        fired.append("RU_FEBRE_ALTA")
        urgente = True
        steps.append(_step("urgente", "Febre alta", temp=sv.temperatura_celsius))

    if "dor_toracica" in sintomas and _has_comorbidade(case, "cardiopatia", "diabetes"):
        fired.append("RU_DOR_TORACICA_COMORB")
        urgente = True
        steps.append(_step("urgente", "Dor torácica com comorbidade relevante"))

    if case.idade_anos >= 65 and "fraqueza" in sintomas and case.duracao_horas <= 24:
        fired.append("RU_IDOSO_FRAQUEZA_AGUDA")
        urgente = True
        steps.append(_step("urgente", "Idoso com fraqueza aguda"))

    if urgente:
        return RuleOutcome(NivelUrgencia.URGENTE, fired, 70.0, steps)

    steps.append(_step("urgente", "Critérios de urgência não atendidos", disparou=False))

    # --- Pontuação ---
    pontos = sum(SINTOMA_PONTOS.get(s, 5) for s in sintomas)
    if sv.temperatura_celsius >= 37.8:
        pontos += 5
    if sv.frequencia_cardiaca_bpm > 110:
        pontos += 8
    if _has_comorbidade(case, "imunossupressao"):
        pontos += 10
    if case.duracao_horas > 72 and pontos < 15:
        pontos -= 5

    steps.append(_step("pontuacao", "Pontuação heurística calculada", total=pontos))

    if pontos >= 55:
        fired.append("SC_EMERGENCIA_PONTOS")
        nivel = NivelUrgencia.EMERGENCIA
    elif pontos >= 35:
        fired.append("SC_URGENTE_PONTOS")
        nivel = NivelUrgencia.URGENTE
    elif pontos >= 15:
        fired.append("SC_ROTINA_PONTOS")
        nivel = NivelUrgencia.ROTINA
    else:
        fired.append("SC_AUTOCUIDADO_PONTOS")
        nivel = NivelUrgencia.AUTOCUIDADO

    steps.append(
        _step("classificacao", f"Nível={nivel.value}", pontuacao=pontos, regras=fired)
    )
    return RuleOutcome(nivel, fired, float(pontos), steps)


def resumo_plain_language(case: IntakeCase, nivel: NivelUrgencia) -> str:
    sintomas_txt = ", ".join(s.replace("_", " ") for s in case.sintomas)
    return (
        f"Pessoa de {case.idade_anos} anos, com sintomas: {sintomas_txt}, há "
        f"aproximadamente {case.duracao_horas:.0f} horas. "
        f"Classificação heurística desta PoC: {nivel.value}. "
        f"{ENCAMINHAMENTOS[nivel.value]}"
    )


def confianca_heuristica(nivel: NivelUrgencia, pontuacao: float, n_regras: int) -> float:
    base = {NivelUrgencia.EMERGENCIA: 0.85, NivelUrgencia.URGENTE: 0.75, NivelUrgencia.ROTINA: 0.65, NivelUrgencia.AUTOCUIDADO: 0.6}
    bonus = min(0.1, n_regras * 0.02)
    if nivel in (NivelUrgencia.ROTINA, NivelUrgencia.AUTOCUIDADO):
        dist = abs(pontuacao - (25 if nivel == NivelUrgencia.ROTINA else 8))
        bonus += max(0, 0.1 - dist * 0.01)
    return min(1.0, round(base[nivel] + bonus, 2))