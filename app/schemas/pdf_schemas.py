"""Pydantic schemas (DTOs) for API responses.

Each response knows how to build itself from the domain entity, so the
mapping lives in a single place per DTO.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.pdf_document import PDFDocument

TEXT_PREVIEW_LENGTH = 500


class PDFDocumentResponse(BaseModel):
    """Metadata of a persisted PDF."""

    id: str
    filename: str
    page_count: int
    file_size: int
    checksum: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PDFListResponse(BaseModel):
    """Response for listing all PDFs."""

    documents: list[PDFDocumentResponse]
    total: int

    @classmethod
    def from_documents(cls, documents: list[PDFDocument]) -> "PDFListResponse":
        return cls(
            documents=[PDFDocumentResponse.model_validate(doc) for doc in documents],
            total=len(documents),
        )


class PDFUploadResponse(BaseModel):
    """Response for PDF upload."""

    id: str
    filename: str
    page_count: int
    file_size: int
    text_preview: str = Field(..., max_length=TEXT_PREVIEW_LENGTH)
    checksum: str

    @classmethod
    def from_document(cls, doc: PDFDocument) -> "PDFUploadResponse":
        return cls(
            id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count,
            file_size=doc.file_size,
            text_preview=doc.text_content[:TEXT_PREVIEW_LENGTH],
            checksum=doc.checksum,
        )


class PDFExtractResponse(BaseModel):
    """Response with extracted text."""

    id: str
    filename: str
    text: str
    page_count: int

    @classmethod
    def from_document(cls, doc: PDFDocument) -> "PDFExtractResponse":
        return cls(
            id=doc.id,
            filename=doc.filename,
            text=doc.text_content,
            page_count=doc.page_count,
        )
