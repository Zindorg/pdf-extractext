"""FastAPI routes for PDF operations."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends

from api.schemas.pdf_schemas import (
    PDFExtractRequest,
    PDFExtractResponse,
    PDFUploadResponse,
)
from core.config import settings
from core.exceptions import PDFExtractextException
from infrastructure.pdf_extractor_adapter import PDFExtractorAdapter
from repositories.pdf_repository import PDFRepository
from services.pdf_service import PDFService

router = APIRouter(prefix="/pdf", tags=["PDF"])


def get_pdf_service() -> PDFService:
    """Dependency injection for PDF service."""
    repository = PDFRepository()
    extractor = PDFExtractorAdapter()
    return PDFService(repository, extractor)


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    service: PDFService = Depends(get_pdf_service),
):
    """
    Upload a PDF and extract text automatically.

    Args:
        file: PDF file to upload
        service: Injected PDF service

    Returns:
        PDFUploadResponse with extracted data

    Raises:
        HTTPException: If file is invalid or extraction fails
    """
    try:
        content = await file.read()

        if len(content) > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")

        doc = await service.process_pdf(content, file.filename)

        return PDFUploadResponse(
            id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count,
            file_size=doc.file_size,
            text_preview=doc.text_content[:500],
        )
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{file_id}/extract", response_model=PDFExtractResponse)
async def extract_text(
    file_id: str,
    request: PDFExtractRequest = None,
    service: PDFService = Depends(get_pdf_service),
):
    """
    Extract text from uploaded PDF.

    Args:
        file_id: Unique identifier of the PDF
        request: Optional extraction parameters
        service: Injected PDF service

    Returns:
        PDFExtractResponse with extracted text

    Raises:
        HTTPException: If PDF not found or extraction fails
    """
    try:
        req = request or PDFExtractRequest()
        doc = await service.extract_text_from_pdf(
            file_id, req.start_page, req.end_page
        )

        return PDFExtractResponse(
            id=doc.id,
            filename=doc.filename,
            text=doc.text_content,
            pages_extracted=doc.page_count,
            total_pages=doc.page_count,
        )
    except PDFExtractextException as e:
        raise HTTPException(status_code=404, detail=str(e))
