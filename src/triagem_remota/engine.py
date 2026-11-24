from __future__ import annotations

import logging

from triagem_remota.constants import ENCAMINHAMENTOS
from triagem_remota.models import IntakeCase, TriageResult
from triagem_remota.rules import (
    avaliar_regras,
    confianca_heuristica,
    resumo_plain_language,
)

logger = logging.getLogger(__name__)


class TriageEngine:
    def triage(self, case: IntakeCase) -> TriageResult:
        logger.info("Iniciando triagem para case_id=%s", case.case_id)
        outcome = avaliar_regras(case)
        nivel = outcome.nivel
        result = TriageResult(
            case_id=case.case_id,
            nivel_urgencia=nivel,
            encaminhamento=ENCAMINHAMENTOS[nivel.value],
            resumo_plain_language=resumo_plain_language(case, nivel),
            confianca_heuristica=confianca_heuristica(
                nivel, outcome.pontuacao, len(outcome.regras_disparadas)
            ),
            processing_steps=outcome.steps,
            regras_disparadas=outcome.regras_disparadas,
            pontuacao_total=outcome.pontuacao,
        )
        logger.info(
            "Triagem concluída case_id=%s nivel=%s regras=%s",
            case.case_id,
            nivel.value,
            outcome.regras_disparadas,
        )
        return result