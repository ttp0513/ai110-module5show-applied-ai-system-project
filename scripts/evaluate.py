"""Run VYBE's fixed deterministic evaluation suite."""

import argparse
from pathlib import Path

from app.evaluation import write_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/evaluation-report.json"),
    )
    arguments = parser.parse_args()
    report = write_report(arguments.output)
    print(f"Evaluation report: {arguments.output}")
    print(
        f"Overall metric pass rate: {report['overall_metric_pass_rate']['value']:.2f}%"
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
