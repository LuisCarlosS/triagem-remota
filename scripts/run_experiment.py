#!/usr/bin/env python3
"""Experimento: compara predições da engine com rótulo ouro."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from triagem_remota.engine import TriageEngine
from triagem_remota.models import IntakeCase, NivelUrgencia

CASES_PATH = ROOT / "data" / "synthetic" / "cases.json"
OUT_DIR = ROOT / "outputs"

LABELS = [
    NivelUrgencia.EMERGENCIA.value,
    NivelUrgencia.URGENTE.value,
    NivelUrgencia.ROTINA.value,
    NivelUrgencia.AUTOCUIDADO.value,
]


def _metrics_manual(y_true: list[str], y_pred: list[str]) -> dict:
    idx = {l: i for i, l in enumerate(LABELS)}
    n = len(y_true)
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    acc = correct / n if n else 0.0

    per_class = {}
    for label in LABELS:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_class[label] = {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

    matrix = [[0] * len(LABELS) for _ in LABELS]
    for t, p in zip(y_true, y_pred):
        matrix[idx[t]][idx[p]] += 1

    return {
        "accuracy": round(acc, 4),
        "n_cases": n,
        "per_class": per_class,
        "confusion_matrix": {"labels": LABELS, "counts": matrix},
    }


def _try_sklearn_metrics(y_true: list[str], y_pred: list[str]) -> dict | None:
    try:
        from sklearn.metrics import classification_report, confusion_matrix
    except ImportError:
        return None
    report = classification_report(y_true, y_pred, labels=LABELS, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    return {
        "classification_report": report,
        "confusion_matrix_sklearn": cm.tolist(),
    }


def main() -> int:
    if not CASES_PATH.is_file():
        print("Execute scripts/prepare_data.py primeiro.", file=sys.stderr)
        return 1

    raw_cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    engine = TriageEngine()
    y_true: list[str] = []
    y_pred: list[str] = []
    failures: list[dict] = []

    for raw in raw_cases:
        case = IntakeCase.model_validate(raw)
        gold = (case.rotulo_ouro or NivelUrgencia.AUTOCUIDADO).value
        pred = engine.triage(case).nivel_urgencia.value
        y_true.append(gold)
        y_pred.append(pred)
        if gold != pred:
            failures.append(
                {
                    "case_id": case.case_id,
                    "rotulo_ouro": gold,
                    "predicao": pred,
                    "sintomas": case.sintomas,
                }
            )

    metrics = _metrics_manual(y_true, y_pred)
    sklearn_extra = _try_sklearn_metrics(y_true, y_pred)
    report = {
        "hipotese": "Conformidade engine vs rotulo_ouro sintético (não clínico)",
        "metrics": metrics,
        "sklearn": sklearn_extra,
        "n_failures": len(failures),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "experiment_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "sample_failures.json").write_text(
        json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = ["Confusion matrix (linhas=ouro, colunas=pred):"]
    header = "             " + " ".join(f"{l[:8]:>8}" for l in LABELS)
    lines.append(header)
    for i, row_label in enumerate(LABELS):
        row = " ".join(f"{v:>8}" for v in metrics["confusion_matrix"]["counts"][i])
        lines.append(f"{row_label[:12]:>12} {row}")
    (OUT_DIR / "confusion_matrix.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Acurácia: {metrics['accuracy']:.2%} ({metrics['n_cases']} casos)")
    print(f"Falhas: {len(failures)} — detalhes em outputs/sample_failures.json")
    print(f"Relatório: outputs/experiment_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())