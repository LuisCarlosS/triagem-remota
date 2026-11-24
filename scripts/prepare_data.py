#!/usr/bin/env python3
"""Gera data/synthetic/cases.json com seed fixa e rótulos ouro de referência."""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from _labeler import reference_label  # noqa: E402
from triagem_remota.constants import COMORBIDADES_VALIDAS, SINTOMAS_VALIDOS  # noqa: E402
from triagem_remota.models import IntakeCase  # noqa: E402

RNG_SEED = 42
N_RANDOM = 63
OUT_PATH = ROOT / "data" / "synthetic" / "cases.json"
GOLD_FIXED = ROOT / "data" / "synthetic" / "gold_fixed.json"


def _rand_vitals(rng: random.Random) -> dict:
    return {
        "frequencia_cardiaca_bpm": rng.randint(60, 130),
        "pressao_sistolica_mmhg": rng.randint(90, 160),
        "temperatura_celsius": round(rng.uniform(36.2, 39.5), 1),
        "saturacao_o2_percent": rng.choice([None, rng.randint(86, 99)]),
    }


def _gen_case(rng: random.Random, idx: int) -> dict:
    n_sym = rng.randint(1, 4)
    sintomas = rng.sample(sorted(SINTOMAS_VALIDOS), n_sym)
    comorb = rng.choice([["nenhuma"], rng.sample([c for c in COMORBIDADES_VALIDAS if c != "nenhuma"], 1)])
    base = datetime(2026, 1, 1) + timedelta(hours=rng.randint(0, 500))
    case_dict = {
        "case_id": f"SYN-{idx:03d}",
        "idade_anos": rng.randint(5, 90),
        "sintomas": sintomas,
        "sinais_vitais": _rand_vitals(rng),
        "duracao_horas": round(rng.uniform(1, 168), 1),
        "comorbidades_simuladas": comorb,
        "timestamp_simulado": base.isoformat(timespec="seconds"),
    }
    case = IntakeCase.model_validate(case_dict)
    case_dict["rotulo_ouro"] = reference_label(case).value
    return case_dict


def main() -> int:
    rng = random.Random(RNG_SEED)
    fixed = json.loads(GOLD_FIXED.read_text(encoding="utf-8"))
    seen = {c["case_id"] for c in fixed}
    generated = []
    idx = 2
    while len(generated) < N_RANDOM:
        if f"SYN-{idx:03d}" in seen:
            idx += 1
            continue
        generated.append(_gen_case(rng, idx))
        idx += 1

    cases = fixed + generated
    cases.sort(key=lambda c: c["case_id"])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Gravado {len(cases)} casos em {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())