"""FastAPI routes for PDF operations."""

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from app.dependencies import (
    get_delete_pdf_use_case,
    get_download_text_use_case,
    get_extract_text_use_case,
    get_list_pdfs_use_case,
    get_process_pdf_use_case,
)
from app.exceptions import PDFNotFoundException
from app.schemas.pdf_schemas import (
    PDFExtractResponse,
    PDFListResponse,
    PDFUploadResponse,
)
from app.use_cases.delete_pdf import DeletePDF
from app.use_cases.download_text import DownloadExtractedText
from app.use_cases.extract_text import ExtractText
from app.use_cases.list_pdfs import ListPDFs
from app.use_cases.process_pdf import ProcessPDFFile

router = APIRouter(prefix="/pdfs", tags=["PDF"])


@router.get("", response_model=PDFListResponse)
def list_pdfs(use_case: ListPDFs = Depends(get_list_pdfs_use_case)) -> PDFListResponse:
    """List all persisted PDF documents.

    Args:
        use_case: Injected ListPDFs use case.

    Returns:
        List of all PDF documents with metadata.
    """
    return use_case.execute()


@router.post("", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...), use_case: ProcessPDFFile = Depends(get_process_pdf_use_case)
) -> PDFUploadResponse:
    """Upload a PDF file, extract text, and persist metadata to MongoDB.

    Args:
        file: Uploaded PDF file.
        use_case: Injected ProcessPDFFile use case.

    Returns:
        Upload response with persisted document metadata.
    """
    content = await file.read()
    result = await use_case.execute(content, file.filename)
    return PDFUploadResponse(**result)


@router.get("/{file_id}/text", response_model=PDFExtractResponse)
def get_text(
    file_id: str,
    use_case: ExtractText = Depends(get_extract_text_use_case),
) -> PDFExtractResponse:
    """Get extracted text from a previously persisted PDF document.

    Args:
        file_id: Document ID.
        use_case: Injected ExtractText use case.

    Returns:
        Extracted text response.
    """
    return use_case.execute(file_id)


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
    doc = use_case.execute(doc_id)
    download_filename = (
        doc.filename.replace(".pdf", ".txt") if doc.filename.endswith(".pdf") else f"{doc.filename}.txt"
    )

    return StreamingResponse(
        use_case.stream_text(doc.text_content),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{download_filename}"'
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
        raise PDFNotFoundException(detail=f"Document not found: {doc_id}")
    return None
