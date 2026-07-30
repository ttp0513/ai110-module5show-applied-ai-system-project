"""Verify default configuration boundaries."""

from app.config import Settings


def test_safe_default_configuration() -> None:
    settings = Settings(_env_file=None)

    assert settings.demo_mode is True
    assert settings.ai_provider == "demo"
    assert settings.ai_api_key == ""
    assert settings.recommendation_count == 5
    assert settings.private_database_path.as_posix() == "data/vybe.db"
    assert settings.session_cookie_max_age_days == 3650
