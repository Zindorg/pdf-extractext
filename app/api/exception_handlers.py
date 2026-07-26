"""Global exception handlers for FastAPI."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import PDFExtractextException
from app.exceptions.problem_detail import ProblemDetail

logger = logging.getLogger(__name__)


def _build_problem_detail(
    *, title: str, detail: str, status: int, request: Request
) -> JSONResponse:
    """Build a standardized RFC 9457 error response."""
    problem = ProblemDetail(
        title=title,
        detail=detail,
        status=status,
        instance=str(request.url),
    )
    return JSONResponse(status_code=status, content=problem.to_dict())


async def pdf_extractext_exception_handler(
    request: Request, exc: PDFExtractextException
) -> JSONResponse:
    """Handle generic PDF application exceptions."""
    logger.error("Application exception: %s (status=%d)", exc, exc.status)
    return _build_problem_detail(
        title=exc.title,
        detail=str(exc),
        status=exc.status,
        request=request,
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI validation errors (422)."""
    detail_msg = "Validation error"
    if exc.errors():
        parts = []
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", []))
            msg = err.get("msg", "")
            parts.append(f"{loc}: {msg}")
        detail_msg = "; ".join(parts)

    logger.warning("Validation error: %s", detail_msg)
    return _build_problem_detail(
        title="Unprocessable Entity",
        detail=detail_msg,
        status=422,
        request=request,
    )


# Convenience export for registration
pdf_exception_handlers = {
    PDFExtractextException: pdf_extractext_exception_handler,
    RequestValidationError: request_validation_exception_handler,
}
