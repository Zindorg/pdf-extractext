"""Problem Detail DTO per RFC 9457."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Details for HTTP APIs."""

    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str
    instance: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        """Return the problem detail as a dictionary."""
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
        }
