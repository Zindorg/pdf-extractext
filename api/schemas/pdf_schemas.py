"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, ConfigDict, Field


class PDFUploadResponse(BaseModel):
    """Response for PDF upload."""

    id: str
    filename: str
    page_count: int
    file_size: int
    text_preview: str = Field(..., max_length=500)

    model_config = ConfigDict(from_attributes=True)


class PDFExtractRequest(BaseModel):
    """Request for text extraction from PDF."""

    start_page: int = Field(default=1, ge=1)
    end_page: int = Field(default=0, ge=0)

    model_config = ConfigDict(
        json_schema_extra={"example": {"start_page": 1, "end_page": 5}}
    )


class PDFExtractResponse(BaseModel):
    """Response with extracted text."""

    id: str
    filename: str
    text: str
    pages_extracted: int
    total_pages: int
