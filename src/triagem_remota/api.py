from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from triagem_remota.engine import TriageEngine
from triagem_remota.exceptions import CaseNotFoundError, TriageValidationError
from triagem_remota.logging_config import setup_logging
from triagem_remota.models import IntakeCase, TriageResult

setup_logging()

app = FastAPI(
    title="Triagem Remota de Sintomas — PoC",
    description="Prova de conceito — não usar para decisão clínica real.",
    version="0.1.0",
)

_engine = TriageEngine()
_ROOT = Path(__file__).resolve().parents[2]
_CASES_PATH = _ROOT / "data" / "synthetic" / "cases.json"


def _load_cases() -> list[dict]:
    if not _CASES_PATH.is_file():
        return []
    return json.loads(_CASES_PATH.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "triagem-remota"}


@app.post("/triagem", response_model=TriageResult)
def triar(case: IntakeCase) -> TriageResult:
    try:
        return _engine.triage(case)
    except TriageValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/demo/casos")
def listar_casos_demo() -> dict[str, list[str]]:
    cases = _load_cases()
    return {"case_ids": [c["case_id"] for c in cases]}