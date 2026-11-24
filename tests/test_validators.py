import pytest

from triagem_remota.exceptions import TriageValidationError
from triagem_remota.validators import validate_case_payload


def _base():
    return {
        "case_id": "T-1",
        "idade_anos": 30,
        "sintomas": ["tosse"],
        "sinais_vitais": {
            "frequencia_cardiaca_bpm": 80,
            "pressao_sistolica_mmhg": 120,
            "temperatura_celsius": 36.8,
        },
        "duracao_horas": 24,
        "comorbidades_simuladas": ["nenhuma"],
    }


def test_valid_case():
    case = validate_case_payload(_base())
    assert case.case_id == "T-1"


def test_invalid_symptom():
    data = _base()
    data["sintomas"] = ["sintoma_inventado"]
    with pytest.raises(TriageValidationError):
        validate_case_payload(data)


def test_invalid_temperature():
    data = _base()
    data["sinais_vitais"]["temperatura_celsius"] = 50
    with pytest.raises(TriageValidationError):
        validate_case_payload(data)


def test_negative_age():
    data = _base()
    data["idade_anos"] = -1
    with pytest.raises(TriageValidationError):
        validate_case_payload(data)