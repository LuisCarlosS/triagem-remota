#!/usr/bin/env python3
"""Executa a PoC de triagem para um ou todos os casos sintéticos."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from triagem_remota.engine import TriageEngine
from triagem_remota.exceptions import CaseNotFoundError
from triagem_remota.logging_config import setup_logging
from triagem_remota.models import IntakeCase

CASES_PATH = ROOT / "data" / "synthetic" / "cases.json"
OUT_DIR = ROOT / "outputs"


def load_cases() -> list[dict]:
    if not CASES_PATH.is_file():
        raise FileNotFoundError(f"Execute prepare_data.py primeiro. Ausente: {CASES_PATH}")
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def find_case(case_id: str) -> dict:
    for c in load_cases():
        if c["case_id"] == case_id:
            return c
    raise CaseNotFoundError(f"Caso não encontrado: {case_id}")


def run_one(engine: TriageEngine, raw: dict) -> Path:
    case = IntakeCase.model_validate(raw)
    result = engine.triage(case)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"triagem_{case.case_id}.json"
    out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    logging.info("Resultado salvo em %s", out_path)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="PoC Triagem Remota de Sintomas")
    parser.add_argument("--case-id", help="ID do caso sintético (ex.: SYN-001)")
    parser.add_argument("--all", action="store_true", help="Processar todos os casos")
    args = parser.parse_args()

    if not args.case_id and not args.all:
        parser.error("Informe --case-id ou --all")

    setup_logging()
    engine = TriageEngine()

    if args.all:
        cases = load_cases()
        for raw in cases:
            run_one(engine, raw)
        print(f"Processados {len(cases)} casos. Saídas em {OUT_DIR}")
        return 0

    try:
        raw = find_case(args.case_id)
    except CaseNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    path = run_one(engine, raw)
    print(f"Triagem concluída: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())