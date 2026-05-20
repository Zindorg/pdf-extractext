"""FastAPI routes for PDF operations."""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config.settings import settings
from app.exceptions import (
    DuplicateDocumentException,
    InvalidFileException,
    PDFExtractextException,
    PDFNotFoundException,
)
from app.repositories.repository_factory import RepositoryFactory
from app.schemas.pdf_schemas import (
    PDFDetailResponse,
    PDFDocumentResponse,
    PDFExtractRequest,
    PDFExtractResponse,
    PDFListResponse,
    PDFUploadResponse,
)
from app.services.pdf_service import PDFService
from app.use_cases.download_text import DownloadExtractedText
from app.use_cases.list_pdfs import ListPDFs
from app.use_cases.get_pdf import GetPDF
from app.use_cases.extract_text import ExtractText
from app.use_cases.delete_pdf import DeletePDF

router = APIRouter(prefix="/pdfs", tags=["PDF"])

_pdf_service: Optional[PDFService] = None


def set_pdf_repository(repository) -> None:
    """Set PDF repository for testing compatibility.

    Args:
        repository: PDF repository instance.
    """
    global _pdf_service
    _pdf_service = PDFService(repository=repository)


def get_pdf_service() -> PDFService:
    """Get or create the PDF service instance.

    Returns:
        Configured PDFService.

    Raises:
        RuntimeError: If repository is not configured.
    """
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService(repository=RepositoryFactory.get_pdf_repository())
    return _pdf_service


# Use case dependency injectors
def get_list_pdfs_use_case(service: PDFService = Depends(get_pdf_service)) -> ListPDFs:
    """Inject ListPDFs use case."""
    return ListPDFs(service)


def get_get_pdf_use_case(service: PDFService = Depends(get_pdf_service)) -> GetPDF:
    """Inject GetPDF use case."""
    return GetPDF(service)


def get_extract_text_use_case(
    service: PDFService = Depends(get_pdf_service),
) -> ExtractText:
    """Inject ExtractText use case."""
    return ExtractText(service)


def get_delete_pdf_use_case(
    service: PDFService = Depends(get_pdf_service),
) -> DeletePDF:
    """Inject DeletePDF use case."""
    return DeletePDF(service)


def get_download_text_use_case(
    service: PDFService = Depends(get_pdf_service),
) -> DownloadExtractedText:
    """Inject DownloadExtractedText use case."""
    return DownloadExtractedText(service)


@router.get("", response_model=PDFListResponse)
def list_pdfs(use_case: ListPDFs = Depends(get_list_pdfs_use_case)) -> PDFListResponse:
    """List all persisted PDF documents.

    Args:
        use_case: Injected ListPDFs use case.

    Returns:
        List of all PDF documents with metadata.
    """
    return use_case.execute()


@router.get("/{doc_id}", response_model=PDFDetailResponse)
def get_pdf(
    doc_id: str, use_case: GetPDF = Depends(get_get_pdf_use_case)
) -> PDFDetailResponse:
    """Get a single PDF document by ID with full text content.

    Args:
        doc_id: Document ID.
        use_case: Injected GetPDF use case.

    Returns:
        PDF document with full text content.

    Raises:
        HTTPException: 404 if document not found.
    """
    doc = use_case.execute(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
    return doc


@router.post("", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...), service: PDFService = Depends(get_pdf_service)
) -> PDFUploadResponse:
    """Upload a PDF file, extract text, and persist metadata to MongoDB.

    Args:
        file: Uploaded PDF file.
        service: Injected PDF service.

    Returns:
        Upload response with persisted document metadata.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid file type: {file.content_type}. Expected PDF",
        )

    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=422, detail="File too large")
    if not content:
        raise HTTPException(status_code=422, detail="File is empty")

    checksum = service.generate_checksum(content)
    existing = service.find_by_checksum(checksum)

    if existing is not None:
        return PDFUploadResponse(
            id=existing.id,
            filename=existing.filename,
            page_count=existing.page_count,
            file_size=existing.file_size,
            text_preview=existing.text_content[:500],
            checksum=existing.checksum,
            is_duplicate=True,
        )

    doc = await service.process_pdf(content, file.filename)
    return PDFUploadResponse(
        id=doc.id,
        filename=doc.filename,
        page_count=doc.page_count,
        file_size=doc.file_size,
        text_preview=doc.text_content[:500],
        checksum=doc.checksum,
        is_duplicate=False,
    )


@router.get("/{file_id}/text", response_model=PDFExtractResponse)
async def get_text(
    file_id: str,
    request: PDFExtractRequest = None,
    use_case: ExtractText = Depends(get_extract_text_use_case),
) -> PDFExtractResponse:
    """Get extracted text from a previously persisted PDF document.

    Args:
        file_id: Document ID.
        request: Optional page range request.
        use_case: Injected ExtractText use case.

    Returns:
        Extracted text response.
    """
    return await use_case.execute(file_id, request)


@router.get("/{doc_id}/download")
def download_pdf_text(
    doc_id: str, use_case: DownloadExtractedText = Depends(get_download_text_use_case)
) -> StreamingResponse:
    """Download extracted text as a .txt file.

    Generates a plain text file on-the-fly from the text
    previously extracted and persisted in MongoDB.

    Args:
        doc_id: Document ID.
        use_case: Injected DownloadExtractedText use case.

    Returns:
        StreamingResponse with text/plain content disposition.
    """
    text = use_case.execute(doc_id)

    return StreamingResponse(
        use_case.stream_text(text),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="extracted_{doc_id[:16]}.txt"'
        },
    )


@router.delete("/{doc_id}", status_code=204)
def delete_pdf(
    doc_id: str, use_case: DeletePDF = Depends(get_delete_pdf_use_case)
) -> None:
    """Permanently delete a PDF document by ID.

    Args:
        doc_id: Document ID.
        use_case: Injected DeletePDF use case.
    """
    deleted = use_case.execute(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
    return None
