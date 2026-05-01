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
from app.exceptions import (
    PDFExtractextException,
    PDFNotFoundException,
    DuplicateDocumentException,
    InvalidFileException,
)
from app.repositories.interfaces.pdf_repository_interface import PDFRepositoryInterface
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/pdf", tags=["PDF"])

_pdf_repository: Optional[PDFRepositoryInterface] = None


def set_pdf_repository(repository: PDFRepositoryInterface) -> None:
    global _pdf_repository
    _pdf_repository = repository


def get_pdf_service() -> PDFService:
    if _pdf_repository is None:
        raise RuntimeError("PDF repository not configured. Call set_pdf_repository() in main.py")
    return PDFService(_pdf_repository)


@router.get("", response_model=PDFListResponse)
def list_pdfs(service: PDFService = Depends(get_pdf_service)):
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
        return PDFListResponse(documents=doc_responses, total=len(doc_responses))
    except PDFExtractextException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", response_model=PDFDetailResponse)
def get_pdf(doc_id: str, service: PDFService = Depends(get_pdf_service)):
    try:
        doc = service.find_by_id(doc_id)
        if doc is None:
            raise PDFNotFoundException(f"Document not found: {doc_id}")
        return PDFDetailResponse(
            id=doc.id, filename=doc.filename, page_count=doc.page_count,
            file_size=doc.file_size, checksum=doc.checksum,
            text_content=doc.text_content, created_at=doc.created_at, updated_at=doc.updated_at,
        )
    except PDFNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...), service: PDFService = Depends(get_pdf_service)):
    try:
        if file.content_type not in ("application/pdf", "application/octet-stream"):
            raise InvalidFileException(f"Invalid file type: {file.content_type}. Expected PDF")

        content = await file.read()
        if len(content) > settings.max_file_size:
            raise InvalidFileException("File too large")
        if not content:
            raise InvalidFileException("File is empty")

        checksum = service.generate_checksum(content)
        existing = service.find_by_checksum(checksum)

        if existing is not None:
            return PDFUploadResponse(
                id=existing.id, filename=existing.filename,
                page_count=existing.page_count, file_size=existing.file_size,
                text_preview=existing.text_content[:500], checksum=existing.checksum,
                is_duplicate=True,
            )

        doc = await service.process_pdf(content, file.filename)
        return PDFUploadResponse(
            id=doc.id, filename=doc.filename, page_count=doc.page_count,
            file_size=doc.file_size, text_preview=doc.text_content[:500],
            checksum=doc.checksum, is_duplicate=False,
        )

    except DuplicateDocumentException:
        raise HTTPException(status_code=409, detail="Duplicate document detected")
    except InvalidFileException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{file_id}/extract", response_model=PDFExtractResponse)
async def extract_text(file_id: str, request: PDFExtractRequest = None, service: PDFService = Depends(get_pdf_service)):
    try:
        req = request or PDFExtractRequest()
        doc = await service.extract_text_from_pdf(file_id, req.start_page, req.end_page)
        return PDFExtractResponse(
            id=doc.id, filename=doc.filename, text=doc.text_content,
            pages_extracted=doc.page_count, total_pages=doc.page_count,
        )
    except PDFNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{doc_id}", status_code=204)
def delete_pdf(doc_id: str, service: PDFService = Depends(get_pdf_service)):
    try:
        deleted = service.delete_by_id(doc_id)
        if not deleted:
            raise PDFNotFoundException(f"Document not found: {doc_id}")
        return None
    except PDFNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PDFExtractextException as e:
        raise HTTPException(status_code=400, detail=str(e))
