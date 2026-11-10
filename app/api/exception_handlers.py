"""Translate domain errors into RFC 9457 HTTP responses.

This is the only place that knows which HTTP status corresponds to each
domain error, so the domain stays free of HTTP concerns.
"""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.problem_detail import ProblemDetail
from app.domain.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractextException,
    PDFExtractionException,
    PDFNotFoundException,
)

logger = logging.getLogger(__name__)

NOT_FOUND = (404, "Not Found")
CONFLICT = (409, "Conflict")
UNPROCESSABLE = (422, "Unprocessable Entity")
SERVER_ERROR = (500, "Internal Server Error")

# Any domain error not listed here (e.g. RepositoryException) is a 500.
_HTTP_ERRORS: dict[type[PDFExtractextException], tuple[int, str]] = {
    PDFNotFoundException: NOT_FOUND,
    DuplicateDocumentException: CONFLICT,
    InvalidFileException: UNPROCESSABLE,
    PDFExtractionException: UNPROCESSABLE,
}


def _problem(request: Request, status: int, title: str, detail: str) -> JSONResponse:
    problem = ProblemDetail(title=title, status=status, detail=detail, instance=str(request.url))
    return JSONResponse(status_code=status, content=problem.model_dump())


async def domain_exception_handler(request: Request, exc: PDFExtractextException) -> JSONResponse:
    status, title = _HTTP_ERRORS.get(type(exc), SERVER_ERROR)
    if status >= 500:
        # Traza completa (incluida la causa del driver) solo en el log.
        logger.error("Server error: %s", exc, exc_info=exc)
    else:
        logger.info("Client error: %s (status=%d)", exc, status)
    return _problem(request, status, title, str(exc))


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    detail = "; ".join(
        f"{'.'.join(str(part) for part in err.get('loc', []))}: {err.get('msg', '')}"
        for err in exc.errors()
    ) or "Validation error"
    logger.info("Validation error: %s", detail)
    return _problem(request, *UNPROCESSABLE, detail)


pdf_exception_handlers = {
    PDFExtractextException: domain_exception_handler,
    RequestValidationError: request_validation_exception_handler,
}
