from fastapi.testclient import TestClient

from triagem_remota.api import app

client = TestClient(app)

PAYLOAD = {
    "case_id": "API-1",
    "idade_anos": 35,
    "sintomas": ["coriza"],
    "sinais_vitais": {
        "frequencia_cardiaca_bpm": 72,
        "pressao_sistolica_mmhg": 115,
        "temperatura_celsius": 36.6,
    },
    "duracao_horas": 12,
    "comorbidades_simuladas": ["nenhuma"],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_triagem_ok():
    r = client.post("/triagem", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"] == "API-1"
    assert "nivel_urgencia" in body


def test_triagem_invalid():
    bad = {**PAYLOAD, "sintomas": ["invalido"]}
    r = client.post("/triagem", json=bad)
    assert r.status_code == 422