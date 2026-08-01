"""Verify final documentation, configuration, and version contracts."""

import re
from pathlib import Path

from app.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_readme_local_links_resolve() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\[[^]]+\]\((?!https?://)([^)#]+)(?:#[^)]+)?\)", readme)

    assert links
    assert all((PROJECT_ROOT / link).is_file() for link in links)


def test_env_example_documents_every_setting() -> None:
    lines = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    documented = {
        line.partition("=")[0].removeprefix("VYBE_").lower()
        for line in lines
        if line and not line.startswith("#")
    }

    assert documented == set(Settings.model_fields)


def test_release_metadata_is_consistent() -> None:
    project = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    main = (PROJECT_ROOT / "app" / "main.py").read_text(encoding="utf-8")
    routes = (PROJECT_ROOT / "app" / "api" / "routes.py").read_text(encoding="utf-8")

    assert 'version = "1.0.0"' in project
    assert 'version="1.0.0"' in main
    assert '"version": "1.0.0"' in routes
    assert 'status": "Phase 13 MVP complete"' in routes


def test_root_model_card_answers_responsible_ai_prompts() -> None:
    model_card = (PROJECT_ROOT / "model_card.md").read_text(encoding="utf-8")

    required_sections = (
        "## Limitations and biases",
        "## Potential misuse and prevention",
        "## Reliability testing reflection",
        "## Collaboration with AI",
        "### Helpful AI suggestion",
        "### Flawed AI suggestion",
    )
    assert all(section in model_card for section in required_sections)


def test_reproducible_evidence_covers_release_commands_and_interactions() -> None:
    evidence = (PROJECT_ROOT / "artifacts" / "reproducible-execution.md").read_text(
        encoding="utf-8"
    )

    required_evidence = (
        "python.exe -m pip check",
        "python.exe -m pytest -q",
        "python.exe -m scripts.evaluate",
        "/api/health",
        "/api/capabilities",
        "## Interaction 1",
        "## Interaction 2",
        "## Interaction 3",
        "provider: gemini",
        "used_fallback: false",
        "76 tests passed",
        "Overall metric pass rate: 100.00%",
    )
    assert all(item in evidence for item in required_evidence)
    assert "VYBE_GEMINI_API_KEY=" not in evidence
