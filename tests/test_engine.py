from triagem_remota.engine import TriageEngine
from triagem_remota.models import IntakeCase, NivelUrgencia, SinaisVitais


def test_pipeline_steps():
    case = IntakeCase(
        case_id="E-1",
        idade_anos=50,
        sintomas=["febre", "tosse"],
        sinais_vitais=SinaisVitais(
            frequencia_cardiaca_bpm=85,
            pressao_sistolica_mmhg=118,
            temperatura_celsius=37.5,
        ),
        duracao_horas=24,
        comorbidades_simuladas=["nenhuma"],
    )
    result = TriageEngine().triage(case)
    assert result.case_id == "E-1"
    assert len(result.processing_steps) >= 3
    assert result.nivel_urgencia in NivelUrgencia
    assert result.encaminhamento
    assert 0 <= result.confianca_heuristica <= 1