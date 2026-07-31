"""Request tracing, structured logs, and HTTP boundary guardrails."""

import json
import logging
import time
from contextvars import ContextVar
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import Settings

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


class JsonLogFormatter(logging.Formatter):
    """Render stable machine-readable logs without request content."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "request_id": request_id_context.get(),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(level: str) -> None:
    """Configure one structured stderr handler for application logs."""

    root = logging.getLogger()
    root.setLevel(level)
    if any(getattr(handler, "vybe_structured", False) for handler in root.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    handler.vybe_structured = True  # type: ignore[attr-defined]
    root.addHandler(handler)


class RequestGuardMiddleware(BaseHTTPMiddleware):
    """Apply request tracing, body limits, origin checks, and safe headers."""

    def __init__(self, app: FastAPI, settings: Settings) -> None:
        super().__init__(app)
        self.maximum_body_bytes = settings.max_request_body_bytes
        self.logger = logging.getLogger("vybe.request")

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = str(uuid4())
        token = request_id_context.set(request_id)
        started = time.perf_counter()
        try:
            try:
                response = self._reject_unsafe_request(request) or await call_next(
                    request
                )
            except Exception:
                self.logger.exception(
                    "unexpected_error method=%s path=%s",
                    request.method,
                    request.url.path,
                )
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "An unexpected error occurred.",
                        "request_id": request_id,
                    },
                )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=()"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; style-src 'self'; script-src 'self'; "
                "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
                "base-uri 'self'; form-action 'self'"
            )
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            self.logger.info(
                "request method=%s path=%s status=%s duration_ms=%s",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response
        finally:
            request_id_context.reset(token)

    def _reject_unsafe_request(self, request: Request) -> Response | None:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.maximum_body_bytes:
                    return JSONResponse(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        content={"detail": "The request body is too large."},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "The Content-Length header is invalid."},
                )

        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            host = request.headers.get("host")
            if origin and host and origin not in {f"http://{host}", f"https://{host}"}:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Cross-origin state changes are not allowed."},
                )
        return None


def install_operations(application: FastAPI, settings: Settings) -> None:
    """Install operational middleware and safe unexpected-error handling."""

    configure_logging(settings.log_level)
    application.add_middleware(RequestGuardMiddleware, settings=settings)
