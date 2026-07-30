"""FastAPI application factory and process entry point."""

from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings


def create_app() -> FastAPI:
    """Build the VYBE API without performing heavyweight startup work."""

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-assisted, catalog-grounded music discovery.",
    )
    application.include_router(router)
    return application


app = create_app()
