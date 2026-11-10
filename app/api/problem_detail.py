"""Problem Detail DTO per RFC 9457."""

from typing import Optional

from pydantic import BaseModel


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Details for HTTP APIs."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
