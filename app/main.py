"""FastAPI application factory and process entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_settings
from app.operations import install_operations

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def create_app() -> FastAPI:
    """Build the VYBE API without performing heavyweight startup work."""

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.3.0",
        description="AI-assisted, catalog-grounded music discovery.",
    )
    install_operations(application, settings)
    application.mount(
        "/static",
        StaticFiles(directory=PROJECT_ROOT / "app" / "static"),
        name="static",
    )
    application.include_router(router)

    @application.get("/", include_in_schema=False)
    def user_interface() -> FileResponse:
        """Serve the responsive Phase 1-3 application interface."""

        return FileResponse(PROJECT_ROOT / "app" / "templates" / "index.html")

    return application


app = create_app()
