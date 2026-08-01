"""Ensure the fixed Phase 12 evaluation meets declared MVP thresholds."""

import json
from pathlib import Path

from app.evaluation import evaluate, write_report


def test_fixed_evaluation_meets_every_threshold() -> None:
    report = evaluate()

    assert report["passed"] is True
    assert report["overall_metric_pass_rate"]["value"] >= 90.0
    assert report["unsupported_factual_claims"]["value"] == 0
    assert all(metric["passed"] for metric in report["metrics"].values())


def test_evaluation_report_is_reproducible_except_timestamp(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = write_report(first_path)
    second = write_report(second_path)
    first.pop("generated_at")
    second.pop("generated_at")

    assert first == second
    assert json.loads(first_path.read_text(encoding="utf-8"))["passed"] is True
