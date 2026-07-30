"""Phase 2 application and health routes."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Public health response without credentials or internal paths."""

    status: Literal["ok"]
    application: str
    environment: str
    demo_mode: bool
    phase: int


@router.get("/", tags=["application"])
def application_summary() -> dict[str, str]:
    """Identify the API while the product UI is developed in a later phase."""

    return {
        "name": get_settings().app_name,
        "status": "Phase 2 architecture scaffold",
        "documentation": "/docs",
    }


@router.get("/api/health", response_model=HealthResponse, tags=["operations"])
def health_check() -> HealthResponse:
    """Report that the Phase 2 process and configuration loaded successfully."""

    settings = get_settings()
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        environment=settings.environment,
        demo_mode=settings.demo_mode,
        phase=2,
    )
