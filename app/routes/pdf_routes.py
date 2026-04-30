"""FastAPI routes for PDF operations."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Optional

from app.schemas.pdf_schemas import (
    PDFExtractRequest,
    PDFExtractResponse,
    PDFUploadResponse,
    PDFListResponse,
    PDFDetailResponse,
    PDFDocumentResponse,
)
from app.config.settings import settings
from app.exceptions import PDFExtractextException, PDFNotFoundException
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/pdf", tags=["PDF"])

# Global storage for repository instance (set by user in main.py)
_pdf_repository: Optional[PDFRepositoryInterface] = None


def set_pdf_repository(repository: PDFRepositoryInterface) -> None:
    """Set the PDF repository instance (called by user in main.py)."""
    global _pdf_repository
    _pdf_repository = repository


def get_pdf_service() -> PDFService:
    """Dependency injection for PDF service."""
    if _pdf_repository is None:
        raise RuntimeError("PDF repository not configured. Call set_pdf_repository() in main.py")
    return PDFService(_pdf_repository)


@router.get("", response_model=PDFListResponse)
def list_pdfs(
    service: PDFService = Depends(get_pdf_service),
):
    """
    List all persisted PDF documents.

    Args:
        service: Injected PDF service

    Returns:
        PDFListResponse with all documents
    """
    try:
        documents = service.find_all()
        doc_responses = [
            PDFDocumentResponse(
                id=doc.id,
                filename=doc.filename,
                page_count=doc.page_count,
                file_size=doc.file_size,
                checksum=doc.checksum,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ]
        return PDFListResponse(
            documents=doc_responses,
            total=len(doc_responses)
        )
    except PDFExtractextException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", response_model=PDFDetailResponse)
def get_pdf(
    doc_id: str,
    service: PDFService = Depends(get_pdf_service),
):
    """
    Get a single PDF document by ID with full text content.

    Args:
        doc_id: Document unique identifier
        service: Injected PDF service

    Returns:
        PDFDetailResponse with full document data

    Raises:
        HTTPException: If document not found
    """
    try:
        doc = service.find_by_id(doc_id)
        if doc is None:
            raise PDFNotFoundException(f"Document not found: {doc_id}")

        return PDFDetailResponse(
            id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count,
            file_size=doc.file_size,
            checksum=doc.checksum,
            text_content=doc.text_content,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
    except PDFNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        PDFUploadResponse with extracted data.
        If document already exists (duplicate checksum), returns existing document.

    Raises:
        HTTPException: If file is invalid or extraction fails
    """
    try:
        content = await file.read()

        if len(content) > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")

        # Check if duplicate before processing
        checksum = service.generate_checksum(content)
        existing = service.find_by_checksum(checksum)
        is_duplicate = existing is not None

        doc = await service.process_pdf(content, file.filename)

        return PDFUploadResponse(
            id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count,
            file_size=doc.file_size,
            text_preview=doc.text_content[:500],
            checksum=doc.checksum,
            is_duplicate=is_duplicate,
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


@router.delete("/{doc_id}", status_code=204)
def delete_pdf(
    doc_id: str,
    service: PDFService = Depends(get_pdf_service),
):
    """
    Delete a PDF document by ID.

    Args:
        doc_id: Document unique identifier
        service: Injected PDF service

    Returns:
        204 No Content if deleted

    Raises:
        HTTPException: If document not found
    """
    try:
        deleted = service.delete_by_id(doc_id)
        if not deleted:
            raise PDFNotFoundException(f"Document not found: {doc_id}")
        return None  # 204 No Content
    except PDFNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))
