"""FastAPI routes for PDF operations (HTTP adapter)."""

import logging
from pathlib import PurePath
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Response, UploadFile

from app.dependencies import (
    get_delete_pdf_use_case,
    get_get_pdf_use_case,
    get_list_pdfs_use_case,
    get_upload_pdf_use_case,
)
from app.schemas.pdf_schemas import PDFExtractResponse, PDFListResponse, PDFUploadResponse
from app.use_cases.delete_pdf import DeletePDF
from app.use_cases.get_pdf import GetPDF
from app.use_cases.list_pdfs import ListPDFs
from app.use_cases.upload_pdf import UploadPDF

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdfs", tags=["PDF"])


@router.get("", response_model=PDFListResponse)
def list_pdfs(use_case: ListPDFs = Depends(get_list_pdfs_use_case)) -> PDFListResponse:
    """List all persisted PDF documents."""
    return PDFListResponse.from_documents(use_case.execute())


@router.post("", response_model=PDFUploadResponse)
def upload_pdf(
    file: UploadFile = File(...),
    use_case: UploadPDF = Depends(get_upload_pdf_use_case),
) -> PDFUploadResponse:
    """Upload a PDF file, extract its text and persist it."""
    logger.info("POST /pdfs — uploading file: %s", file.filename)
    document = use_case.execute(file.file.read(), file.filename)
    return PDFUploadResponse.from_document(document)


@router.get("/{file_id}/text", response_model=PDFExtractResponse)
def get_text(file_id: str, use_case: GetPDF = Depends(get_get_pdf_use_case)) -> PDFExtractResponse:
    """Get the text extracted from a persisted PDF."""
    return PDFExtractResponse.from_document(use_case.execute(file_id))


@router.get("/{doc_id}/download")
def download_pdf_text(doc_id: str, use_case: GetPDF = Depends(get_get_pdf_use_case)) -> Response:
    """Download the extracted text as a .txt file."""
    document = use_case.execute(doc_id)
    return Response(
        content=document.text_content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": _attachment_header(document.filename)},
    )


@router.delete("/{doc_id}", status_code=204)
def delete_pdf(doc_id: str, use_case: DeletePDF = Depends(get_delete_pdf_use_case)) -> None:
    """Permanently delete a PDF document by ID."""
    use_case.execute(doc_id)


def _attachment_header(pdf_filename: str) -> str:
    """Build a safe Content-Disposition for the .txt version of a PDF name.

    Uses an ASCII fallback plus the RFC 6266 ``filename*`` form so that
    quotes, newlines or non-ASCII characters cannot break the header.
    """
    txt_name = f"{PurePath(pdf_filename).stem}.txt"
    ascii_name = "".join(
        c if c.isascii() and c.isprintable() and c not in '"\\' else "_" for c in txt_name
    )
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(txt_name)}"
