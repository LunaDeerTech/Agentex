"""Application exception definitions and handlers."""

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


class AppError(Exception):
    """Application-level error with standardized response."""

    def __init__(
        self,
        code: int,
        message: str,
        status_code: int = 400,
        data: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.data = data


def _json_error(code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def _map_http_status_to_code(status_code: int) -> int:
    if status_code == 401:
        return 40100
    if status_code == 403:
        return 40300
    if status_code == 404:
        return 40400
    if status_code == 422:
        return 40000
    if status_code >= 500:
        return 50000
    return 40000


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "AppError",
        path=request.url.path,
        method=request.method,
        code=exc.code,
        message=exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_json_error(exc.code, exc.message, exc.data),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = _map_http_status_to_code(exc.status_code)
    logger.warning(
        "HTTPException",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_json_error(code, str(exc.detail), None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    sanitized_errors: list[dict[str, Any]] = []

    for err in errors:
        sanitized = dict(err)
        ctx = sanitized.get("ctx")
        if isinstance(ctx, dict):
            sanitized_ctx = dict(ctx)
            if "error" in sanitized_ctx:
                sanitized_ctx["error"] = str(sanitized_ctx["error"])
            sanitized["ctx"] = sanitized_ctx
        sanitized_errors.append(sanitized)

    logger.warning(
        "ValidationError",
        path=request.url.path,
        method=request.method,
        errors=sanitized_errors,
    )
    return JSONResponse(
        status_code=422,
        content=_json_error(40000, "Validation error", sanitized_errors),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "UnhandledException",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content=_json_error(50000, "Internal server error", None),
    )


def register_exception_handlers(app) -> None:
    """Register global exception handlers on the FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
