from triagem_remota.models import IntakeCase, NivelUrgencia, SinaisVitais
from triagem_remota.rules import avaliar_regras


def _case(**kwargs) -> IntakeCase:
    defaults = {
        "case_id": "R-1",
        "idade_anos": 40,
        "sintomas": ["tosse"],
        "sinais_vitais": SinaisVitais(
            frequencia_cardiaca_bpm=80,
            pressao_sistolica_mmhg=120,
            temperatura_celsius=36.8,
        ),
        "duracao_horas": 12,
        "comorbidades_simuladas": ["nenhuma"],
    }
    defaults.update(kwargs)
    if "sinais_vitais" in kwargs and isinstance(kwargs["sinais_vitais"], dict):
        defaults["sinais_vitais"] = SinaisVitais(**kwargs["sinais_vitais"])
    return IntakeCase(**defaults)


def test_convulsao_emergencia():
    c = _case(sintomas=["convulsao"])
    out = avaliar_regras(c)
    assert out.nivel == NivelUrgencia.EMERGENCIA
    assert "RF_CONVULSAO" in out.regras_disparadas


def test_dor_toracica_dispneia():
    c = _case(
        sintomas=["dor_toracica", "falta_ar"],
        sinais_vitais={
            "frequencia_cardiaca_bpm": 105,
            "pressao_sistolica_mmhg": 130,
            "temperatura_celsius": 36.9,
        },
    )
    out = avaliar_regras(c)
    assert out.nivel == NivelUrgencia.EMERGENCIA


def test_coriza_autocuidado():
    c = _case(sintomas=["coriza", "tosse"], duracao_horas=48)
    out = avaliar_regras(c)
    assert out.nivel == NivelUrgencia.AUTOCUIDADO


def test_hipotensao_emergencia():
    c = _case(
        sinais_vitais={
            "frequencia_cardiaca_bpm": 90,
            "pressao_sistolica_mmhg": 85,
            "temperatura_celsius": 36.5,
        }
    )
    out = avaliar_regras(c)
    assert out.nivel == NivelUrgencia.EMERGENCIA
    assert "RF_HIPOTENSAO" in out.regras_disparadas